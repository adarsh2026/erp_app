from tornado.web import authenticated
from handlers.base import BaseHandler
from handlers.validators import validate_name, validate_optional_person_name, validate_phone, first_error

def _has_access(handler, permissions):
    return handler.is_admin() or "material_management" in permissions

class SupplierHandler(BaseHandler):
    @authenticated
    async def get(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return
        rows = await self.db.fetch(
            "SELECT supplier_id, supplier_name, contact_person_name, contact_phone FROM suppliers ORDER BY supplier_id DESC"
        )
        self.render(
            "supplier.html",
            user=self.current_user,
            permissions=permissions,
            suppliers=rows,
        )

    @authenticated
    async def post(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        name = self.get_body_argument("name", "").strip()
        contact_person = self.get_body_argument("contact_person", "").strip()
        phone = self.get_body_argument("phone", "").strip()

        error = first_error(
            validate_name(name, "Supplier name"),
            validate_optional_person_name(contact_person, "Contact person"),
            validate_phone(phone, "Phone"),
        )
        if error:
            self.redirect_with_error("/master/supplier", error)
            return

        await self.db.execute(
            "INSERT INTO suppliers (supplier_name, contact_person_name, contact_phone) VALUES ($1, $2, $3)",
            name, contact_person or None, phone or None,
        )
        self.redirect("/master/supplier")


class SupplierEditHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT supplier_id FROM suppliers WHERE supplier_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/supplier", "Supplier record not found.")
            return

        name = self.get_body_argument("name", "").strip()
        contact_person = self.get_body_argument("contact_person", "").strip()
        phone = self.get_body_argument("phone", "").strip()

        error = first_error(
            validate_name(name, "Supplier name"),
            validate_optional_person_name(contact_person, "Contact person"),
            validate_phone(phone, "Phone"),
        )
        if error:
            self.redirect_with_error("/master/supplier", error)
            return

        await self.db.execute(
            "UPDATE suppliers SET supplier_name = $1, contact_person_name = $2, contact_phone = $3 WHERE supplier_id = $4",
            name, contact_person or None, phone or None, int(item_id),
        )
        self.redirect("/master/supplier")


class SupplierDeleteHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT supplier_id FROM suppliers WHERE supplier_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/supplier", "Supplier record not found.")
            return

        await self.db.execute("DELETE FROM suppliers WHERE supplier_id = $1", int(item_id))
        self.redirect("/master/supplier")