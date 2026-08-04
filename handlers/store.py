from tornado.web import authenticated
from handlers.base import BaseHandler
from handlers.validators import validate_name, validate_location, first_error


def _has_access(handler, permissions):
    return handler.is_admin() or "general_master_data" in permissions
    
class StoreHandler(BaseHandler):
    @authenticated
    async def get(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return
        rows = await self.db.fetch("SELECT store_id, store_name, store_location FROM stores ORDER BY store_id DESC")
        self.render(
            "store.html",
            user=self.current_user,
            permissions=permissions,
            stores=rows,
        )
        
    @authenticated
    async def post(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        name = self.get_body_argument("name", "").strip()
        location = self.get_body_argument("location", "").strip()

        error = first_error(
            validate_name(name, "Store name"),
            validate_location(location, "Location"),
        )
        if error:
            self.redirect_with_error("/master/store", error)
            return

        dup = await self.db.fetchrow("SELECT store_id FROM stores WHERE store_name = $1", name)
        if dup:
            self.redirect_with_error("/master/store", "A store with this name already exists.")
            return

        await self.db.execute(
            "INSERT INTO stores (store_name, store_location) VALUES ($1, $2)",
            name, location or None,
        )
        self.redirect("/master/store")


class StoreEditHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT store_id FROM stores WHERE store_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/store", "Store record not found.")
            return

        name = self.get_body_argument("name", "").strip()
        location = self.get_body_argument("location", "").strip()

        error = first_error(
            validate_name(name, "Store name"),
            validate_location(location, "Location"),
        )
        if error:
            self.redirect_with_error("/master/store", error)
            return

        dup = await self.db.fetchrow(
            "SELECT store_id FROM stores WHERE store_name = $1 AND store_id != $2",
            name, int(item_id),
        )
        if dup:
            self.redirect_with_error("/master/store", "A store with this name already exists.")
            return

        await self.db.execute(
            "UPDATE stores SET store_name = $1, store_location = $2 WHERE store_id = $3",
            name, location or None, int(item_id),
        )
        self.redirect("/master/store")


class StoreDeleteHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT store_id FROM stores WHERE store_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/store", "Store record not found.")
            return

        await self.db.execute("DELETE FROM stores WHERE store_id = $1", int(item_id))
        self.redirect("/master/store")