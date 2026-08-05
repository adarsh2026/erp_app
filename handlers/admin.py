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


async def _get_role_name(handler, target_user_id):
    row = await handler.db.fetchrow(
        "SELECT roles.role_name FROM users "
        "JOIN roles ON users.role_id = roles.role_id "
        "WHERE users.user_id = $1",
        target_user_id,
    )
    return row["role_name"] if row else None


async def _can_manage_target(handler, target_user_id):
    """
    True if the logged-in admin/superadmin is allowed to reset/delete/
    edit-permissions of target_user_id.

    - Nobody can manage their own account here (self-delete/self-reset blocked).
    - Superadmin can manage any admin or user.
    - A regular admin can only manage users it created itself.
    """
    if int(handler.current_user["id"]) == target_user_id:
        return False

    target_role = await _get_role_name(handler, target_user_id)
    if target_role is None:
        return False

    if handler.is_superadmin():
        return target_role in ("admin", "user")

    if target_role != "user":
        return False

    row = await handler.db.fetchrow(
        "SELECT created_by FROM users WHERE user_id = $1", target_user_id
    )
    return row is not None and row["created_by"] == int(handler.current_user["id"])


class AdminPermissionsHandler(BaseHandler):
    @authenticated
    async def get(self):
        if not self.is_admin():
            self.redirect("/dashboard")
            return

        perm_rows = await self.db.fetch("SELECT user_id, module_name FROM user_permissions")
        permissions_map = {}
        for row in perm_rows:
            permissions_map.setdefault(row["user_id"], set()).add(row["module_name"])

        roles = await self.db.fetch("SELECT role_id, role_name FROM roles ORDER BY role_name")
        permissions = await self.get_permissions()

        if self.is_superadmin():
            admins = await self.db.fetch(
                "SELECT users.user_id, users.username, users.full_name "
                "FROM users JOIN roles ON users.role_id = roles.role_id "
                "WHERE roles.role_name = 'admin' ORDER BY users.username"
            )

            selected_admin_id = self.get_query_argument("admin_id", None)
            selected_admin = None
            users = []

            if selected_admin_id:
                try:
                    selected_admin_id = int(selected_admin_id)
                except ValueError:
                    selected_admin_id = None

            if selected_admin_id:
                selected_admin = next((a for a in admins if a["user_id"] == selected_admin_id), None)

            if selected_admin:
                users = await self.db.fetch(
                    "SELECT user_id, username, full_name FROM users "
                    "WHERE created_by = $1 ORDER BY username",
                    selected_admin_id,
                )

            self.render(
                "admin_permissions.html",
                user=self.current_user,
                permissions=permissions,
                is_superadmin=True,
                admins=admins,
                selected_admin=selected_admin,
                users=users,
                permissions_map=permissions_map,
                roles=roles,
                modules=MODULES,
                module_labels=MODULE_LABELS,
            )
            return

        users = await self.db.fetch(
            "SELECT user_id, username, full_name FROM users "
            "WHERE created_by = $1 ORDER BY username",
            int(self.current_user["id"]),
        )

        self.render(
            "admin_permissions.html",
            user=self.current_user,
            permissions=permissions,
            is_superadmin=False,
            admins=[],
            selected_admin=None,
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
        return_url = self.request.headers.get("Referer") or "/admin/permissions"

        if not await _can_manage_target(self, target_user_id):
            self.redirect_with_error(return_url, "You don't have permission to modify this user.")
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

        self.redirect(return_url)


class AdminResetPasswordHandler(BaseHandler):
    @authenticated
    async def post(self, target_user_id):
        if not self.is_admin():
            self.redirect("/dashboard")
            return

        target_user_id = int(target_user_id)
        return_url = self.request.headers.get("Referer") or "/admin/permissions"

        if not await _can_manage_target(self, target_user_id):
            self.redirect_with_error(return_url, "You don't have permission to reset this user's password.")
            return

        new_password = self.get_body_argument("new_password", "")
        error = validate_password(new_password, "New password")
        if error:
            self.redirect_with_error(return_url, error)
            return

        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        await self.db.execute(
            "UPDATE users SET password_hash = $1 WHERE user_id = $2",
            new_hash, target_user_id,
        )

        self.redirect(return_url)


class AdminDeleteUserHandler(BaseHandler):
    @authenticated
    async def post(self, target_user_id):
        if not self.is_admin():
            self.redirect("/dashboard")
            return

        target_user_id = int(target_user_id)
        return_url = self.request.headers.get("Referer") or "/admin/permissions"

        if not await _can_manage_target(self, target_user_id):
            self.redirect_with_error(return_url, "You don't have permission to delete this user.")
            return

        await self.db.execute("DELETE FROM users WHERE user_id = $1", target_user_id)
        self.redirect(return_url)


class AdminCreateUserHandler(BaseHandler):
    @authenticated
    async def post(self):
        if not self.is_admin():
            self.redirect("/dashboard")
            return

        return_url = self.request.headers.get("Referer") or "/admin/permissions"

        username = self.get_body_argument("username", "").strip()
        full_name = self.get_body_argument("full_name", "").strip()
        password = self.get_body_argument("password", "")
        role_name = self.get_body_argument("role", "user").strip().lower()

        if not self.is_superadmin():
            role_name = "user"

        if role_name not in ("admin", "user"):
            self.redirect_with_error(return_url, "Invalid role selected.")
            return

        error = first_error(
            validate_username(username, "Username"),
            validate_person_name(full_name, "Full name"),
            validate_password(password, "Password"),
        )
        if error:
            self.redirect_with_error(return_url, error)
            return

        existing = await self.db.fetchrow(
            "SELECT user_id FROM users WHERE username = $1", username
        )
        if existing:
            self.redirect_with_error(return_url, "That username is already taken.")
            return

        role_row = await self.db.fetchrow(
            "SELECT role_id FROM roles WHERE role_name = $1", role_name
        )
        if not role_row:
            self.redirect_with_error(return_url, f"Role '{role_name}' not found.")
            return

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        await self.db.execute(
            "INSERT INTO users (username, password_hash, full_name, role_id, created_by, is_active) "
            "VALUES ($1, $2, $3, $4, $5, TRUE)",
            username, password_hash, full_name, role_row["role_id"], int(self.current_user["id"]),
        )

        self.redirect(return_url)