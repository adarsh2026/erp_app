import bcrypt
from tornado.web import authenticated

from handlers.base import BaseHandler
from handlers.validators import validate_password, validate_person_name, first_error

MODULES = ["general_master_data", "material_management"]

MODULE_LABELS = {
    "general_master_data": "General Master Data",
    "material_management": "Material Management",
}

USERNAME_MIN = 3
USERNAME_MAX = 30

def validate_username(value, label="Username"):
    if value is None or value.strip() == "":
        return f"{label} is required."
    v = value.strip()
    if len(v) < USERNAME_MIN or len(v) > USERNAME_MAX:
        return f"{label} must be {USERNAME_MIN}-{USERNAME_MAX} characters."
    if not v.replace("_", "").replace(".", "").isalnum():
        return f"{label} can only contain letters, numbers, '.' and '_'."
    return None


async def _is_target_admin(handler, target_user_id):
    row = await handler.db.fetchrow(
        "SELECT roles.role_name FROM users "
        "JOIN roles ON users.role_id = roles.role_id "
        "WHERE users.user_id = $1",
        target_user_id,
    )
    return row is not None and row["role_name"] == "admin"


class AdminPermissionsHandler(BaseHandler):
    @authenticated
    async def get(self):
        if not self.is_admin(): 
            self.redirect("/dashboard")
            return
        users = await self.db.fetch(
            "SELECT users.user_id, users.username, users.full_name "
            "FROM users JOIN roles ON users.role_id = roles.role_id "
            "WHERE roles.role_name != 'admin' ORDER BY users.username"
        )
        perm_rows = await self.db.fetch("SELECT user_id, module_name FROM user_permissions")
        roles = await self.db.fetch("SELECT role_id, role_name FROM roles ORDER BY role_name")

        permissions_map = {}
        for row in perm_rows:
            permissions_map.setdefault(row["user_id"], set()).add(row["module_name"])

        self.render(
            "admin_permissions.html",
            user=self.current_user,
            users=users,
            permissions_map=permissions_map,
            roles=roles,
            modules=MODULES,
            module_labels=MODULE_LABELS,
        )

class AdminPermissionsUpdateHandler(BaseHandler):

    @authenticated
    async def post(self, target_user_id):
        if not self.is_admin():
            self.redirect("/dashboard")
            return

        target_user_id = int(target_user_id)

        if await _is_target_admin(self, target_user_id):
            self.redirect_with_error("/admin/permissions", "Cannot modify permissions for an admin account.")
            return

        selected_modules = self.get_body_arguments("modules")

        await self.db.execute(
            "DELETE FROM user_permissions WHERE user_id = $1", target_user_id
        )

        for module in selected_modules:
            if module in MODULES:
                await self.db.execute(
                    "INSERT INTO user_permissions (user_id, module_name) VALUES ($1, $2)",
                    target_user_id, module,
                )

        self.redirect("/admin/permissions")


class AdminResetPasswordHandler(BaseHandler):
    @authenticated
    async def post(self, target_user_id):
        if not self.is_admin():
            self.redirect("/dashboard")
            return

        target_user_id = int(target_user_id)

        if await _is_target_admin(self, target_user_id):
            self.redirect_with_error("/admin/permissions", "Cannot reset the password of an admin account.")
            return

        new_password = self.get_body_argument("new_password", "")
        error = validate_password(new_password, "New password")
        if error:
            self.redirect_with_error("/admin/permissions", error)
            return

        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        await self.db.execute(
            "UPDATE users SET password_hash = $1 WHERE user_id = $2",
            new_hash, target_user_id,
        )

        self.redirect("/admin/permissions")


class AdminDeleteUserHandler(BaseHandler):
    @authenticated
    async def post(self, target_user_id):
        if not self.is_admin():
            self.redirect("/dashboard")
            return

        target_user_id = int(target_user_id)

        if await _is_target_admin(self, target_user_id):
            self.redirect_with_error("/admin/permissions", "Cannot delete an admin account.")
            return

        await self.db.execute("DELETE FROM users WHERE user_id = $1", target_user_id)
        self.redirect("/admin/permissions")


class AdminCreateUserHandler(BaseHandler):
    @authenticated
    async def post(self):
        if not self.is_admin():
            self.redirect("/dashboard")
            return

        username = self.get_body_argument("username", "").strip()
        full_name = self.get_body_argument("full_name", "").strip()
        password = self.get_body_argument("password", "")
        role_name = self.get_body_argument("role", "").strip().lower()

        error = first_error(
            validate_username(username, "Username"),
            validate_person_name(full_name, "Full name"),
            validate_password(password, "Password"),
        )
        if error:
            self.redirect_with_error("/admin/permissions", error)
            return

        existing = await self.db.fetchrow(
            "SELECT user_id FROM users WHERE username = $1", username
        )
        if existing:
            self.redirect_with_error("/admin/permissions", "That username is already taken.")
            return

        role_row = await self.db.fetchrow(
            "SELECT role_id FROM roles WHERE LOWER(role_name) = LOWER($1)", role_name
        )
        if not role_row:
            valid_roles = await self.db.fetch("SELECT role_name FROM roles ORDER BY role_name")
            valid_names = ", ".join(r["role_name"] for r in valid_roles)
            self.redirect_with_error(
                "/admin/permissions",
                f"Invalid role '{role_name}'. Valid roles are: {valid_names}.",
            )
            return

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        await self.db.execute(
            "INSERT INTO users (username, password_hash, full_name, role_id, is_active) "
            "VALUES ($1, $2, $3, $4, TRUE)",
            username, password_hash, full_name, role_row["role_id"],
        )

        self.redirect("/admin/permissions")