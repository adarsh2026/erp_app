import bcrypt
from tornado.web import authenticated
from handlers.base import BaseHandler
from handlers.validators import validate_password, first_error

class LoginHandler(BaseHandler):

    def get(self):
        if self.current_user:
            self.redirect("/dashboard")
            return
        self.render("login.html", error=None)

    async def post(self):
        username = self.get_body_argument("username", "").strip()
        password = self.get_body_argument("password", "").strip()

        if not username or not password:
            self.render("login.html", error="Please enter both username and password")
            return

        row = await self.db.fetchrow(
            "SELECT user_id, username, password_hash, is_active "
            "FROM users WHERE username = $1",
            username,
        )

        if row is None or not row["is_active"]:
            self.render("login.html", error="Invalid username or password")
            return

        password_ok = bcrypt.checkpw(
            password.encode("utf-8"), row["password_hash"].encode("utf-8")
        )

        if not password_ok:
            self.render("login.html", error="Invalid username or password")
            return
        self.set_secure_cookie("user_id", str(row["user_id"]), expires_days=7)

        self.redirect("/dashboard")


class LogoutHandler(BaseHandler):

    @authenticated
    def get(self):
        self.clear_cookie("user_id")
        self.redirect("/login")


class ChangePasswordHandler(BaseHandler):
    @authenticated
    async def get(self):
        permissions = await self.get_permissions()
        self.render("change_password.html", user=self.current_user, permissions=permissions)

    @authenticated
    async def post(self):
        return_url = self.request.headers.get("Referer") or "/dashboard"

        current_password = self.get_body_argument("current_password", "")
        new_password = self.get_body_argument("new_password", "")
        confirm_password = self.get_body_argument("confirm_password", "")

        error = first_error(
            validate_password(current_password, "Current password"),
            validate_password(new_password, "New password"),
        )
        if not error and new_password != confirm_password:
            error = "New password and confirm password do not match."

        if error:
            self.redirect_with_error(return_url, error)
            return

        row = await self.db.fetchrow(
            "SELECT password_hash FROM users WHERE user_id = $1",
            int(self.current_user["id"]),
        )

        current_ok = row is not None and bcrypt.checkpw(
            current_password.encode("utf-8"), row["password_hash"].encode("utf-8")
        )
        if not current_ok:
            self.redirect_with_error(return_url, "Current password is incorrect.")
            return

        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        await self.db.execute(
            "UPDATE users SET password_hash = $1 WHERE user_id = $2",
            new_hash, int(self.current_user["id"]),
        )

        self.redirect(return_url)