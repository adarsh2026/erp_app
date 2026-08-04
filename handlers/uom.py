from tornado.web import authenticated
from handlers.base import BaseHandler
from handlers.validators import validate_name, validate_symbol, first_error


def _has_access(handler, permissions):
    return handler.is_admin() or "general_master_data" in permissions


class UomHandler(BaseHandler):
    @authenticated
    async def get(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return
        rows = await self.db.fetch("SELECT uom_id, uom_name, uom_symbol FROM uoms ORDER BY uom_id DESC")
        self.render(
            "uom.html",
            user=self.current_user,
            permissions=permissions,
            uoms=rows,
        )
   
    @authenticated
    async def post(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        name = self.get_body_argument("name", "").strip()
        symbol = self.get_body_argument("symbol", "").strip()
                
        error = first_error(
            validate_name(name, "UOM name"),
            validate_symbol(symbol, "Symbol"),
        )
        if error:
            self.redirect_with_error("/master/uom", error)
            return

        dup = await self.db.fetchrow("SELECT uom_id FROM uoms WHERE uom_name = $1", name)
        if dup:
            self.redirect_with_error("/master/uom", "A UOM with this name already exists.")
            return

        await self.db.execute(
            "INSERT INTO uoms (uom_name, uom_symbol) VALUES ($1, $2)",
            name, symbol or None,
        )
        self.redirect("/master/uom")


class UomEditHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT uom_id FROM uoms WHERE uom_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/uom", "UOM record not found.")
            return

        name = self.get_body_argument("name", "").strip()
        symbol = self.get_body_argument("symbol", "").strip()

        error = first_error(
            validate_name(name, "UOM name"),
            validate_symbol(symbol, "Symbol"),
        )
        if error:
            self.redirect_with_error("/master/uom", error)
            return

        dup = await self.db.fetchrow(
            "SELECT uom_id FROM uoms WHERE uom_name = $1 AND uom_id != $2",
            name, int(item_id),
        )
        if dup:
            self.redirect_with_error("/master/uom", "A UOM with this name already exists.")
            return

        await self.db.execute(
            "UPDATE uoms SET uom_name = $1, uom_symbol = $2 WHERE uom_id = $3",
            name, symbol or None, int(item_id),
        )
        self.redirect("/master/uom")
        
class UomDeleteHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT uom_id FROM uoms WHERE uom_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/uom", "UOM record not found.")
            return

        await self.db.execute("DELETE FROM uoms WHERE uom_id = $1", int(item_id))
        self.redirect("/master/uom")