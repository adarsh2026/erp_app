from tornado.web import authenticated
from handlers.base import BaseHandler
from handlers.validators import validate_name


def _has_access(handler, permissions):
    return handler.is_admin() or "general_master_data" in permissions

class DepartmentHandler(BaseHandler):
    @authenticated
    async def get(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return
        rows = await self.db.fetch("SELECT department_id, department_name FROM departments ORDER BY department_id DESC")
        self.render(
            "department.html",
            user=self.current_user,
            permissions=permissions,
            departments=rows,
        )

    @authenticated
    async def post(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        name = self.get_body_argument("name", "").strip()

        error = validate_name(name, "Department name")
        if error:
            self.redirect_with_error("/master/department", error)
            return

        dup = await self.db.fetchrow(
            "SELECT department_id FROM departments WHERE department_name = $1", name
        )
        if dup:
            self.redirect_with_error("/master/department", "A department with this name already exists.")
            return

        await self.db.execute("INSERT INTO departments (department_name) VALUES ($1)", name)
        self.redirect("/master/department")
        
class DepartmentEditHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT department_id FROM departments WHERE department_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/department", "Department record not found.")
            return

        name = self.get_body_argument("name", "").strip()

        error = validate_name(name, "Department name")
        if error:
            self.redirect_with_error("/master/department", error)
            return

        dup = await self.db.fetchrow(
            "SELECT department_id FROM departments WHERE department_name = $1 AND department_id != $2",
            name, int(item_id),
        )
        if dup:
            self.redirect_with_error("/master/department", "A department with this name already exists.")
            return

        await self.db.execute(
            "UPDATE departments SET department_name = $1 WHERE department_id = $2", name, int(item_id)
        )
        self.redirect("/master/department")


class DepartmentDeleteHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT department_id FROM departments WHERE department_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/department", "Department record not found.")
            return

        await self.db.execute("DELETE FROM departments WHERE department_id = $1", int(item_id))
        self.redirect("/master/department")