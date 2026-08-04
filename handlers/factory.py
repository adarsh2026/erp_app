from tornado.web import authenticated
from handlers.base import BaseHandler
from handlers.validators import validate_name, validate_location, first_error


def _has_access(handler, permissions):
    return handler.is_admin() or "general_master_data" in permissions

class FactoryHandler(BaseHandler):
    @authenticated
    async def get(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return
        rows = await self.db.fetch("SELECT factory_id, factory_name, factory_location FROM factories ORDER BY factory_id DESC")
        self.render(
            "factory.html",
            user=self.current_user,
            permissions=permissions,
            factories=rows,
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
            validate_name(name, "Factory name"),
            validate_location(location, "Location"),
        )
        if error:
            self.redirect_with_error("/master/factory", error)
            return

        dup = await self.db.fetchrow("SELECT factory_id FROM factories WHERE factory_name = $1", name)
        if dup:
            self.redirect_with_error("/master/factory", "A factory with this name already exists.")
            return

        await self.db.execute(
            "INSERT INTO factories (factory_name, factory_location) VALUES ($1, $2)",
            name, location or None,
        )
        self.redirect("/master/factory")


class FactoryEditHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT factory_id FROM factories WHERE factory_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/factory", "Factory record not found.")
            return

        name = self.get_body_argument("name", "").strip()
        location = self.get_body_argument("location", "").strip()

        error = first_error(
            validate_name(name, "Factory name"),
            validate_location(location, "Location"),
        )
        if error:
            self.redirect_with_error("/master/factory", error)
            return

        dup = await self.db.fetchrow(
            "SELECT factory_id FROM factories WHERE factory_name = $1 AND factory_id != $2",
            name, int(item_id),
        )
        if dup:
            self.redirect_with_error("/master/factory", "A factory with this name already exists.")
            return

        await self.db.execute(
            "UPDATE factories SET factory_name = $1, factory_location = $2 WHERE factory_id = $3",
            name, location or None, int(item_id),
        )
        self.redirect("/master/factory")


class FactoryDeleteHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT factory_id FROM factories WHERE factory_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/factory", "Factory record not found.")
            return

        await self.db.execute("DELETE FROM factories WHERE factory_id = $1", int(item_id))
        self.redirect("/master/factory")