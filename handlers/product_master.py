from tornado.web import authenticated
from handlers.base import BaseHandler
from handlers.validators import validate_name, validate_positive_int, first_error

def _has_access(handler, permissions):
    return handler.is_admin() or "material_management" in permissions

class ProductMasterHandler(BaseHandler):
    @authenticated
    async def get(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return
        rows = await self.db.fetch(
            "SELECT pm.product_master_id, pm.master_product_name, "
            "pm.product_category_id AS category_id, pm.uom_id AS uom_id, "
            "pc.category_name AS category_name, u.uom_name AS uom_name "
            "FROM product_master pm "
            "LEFT JOIN product_categories pc ON pm.product_category_id = pc.product_category_id "
            "LEFT JOIN uoms u ON pm.uom_id = u.uom_id "
            "ORDER BY pm.created_at DESC"
        )
        categories = await self.db.fetch("SELECT product_category_id, category_name FROM product_categories ORDER BY category_name")
        uoms = await self.db.fetch("SELECT uom_id, uom_name FROM uoms ORDER BY uom_name")
        self.render(
            "product_master.html",
            user=self.current_user,
            permissions=permissions,
            products=rows,
            categories=categories,
            uoms=uoms,
        )

    @authenticated
    async def post(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        name = self.get_body_argument("name", "").strip()
        category_id = self.get_body_argument("category_id", "").strip()
        uom_id = self.get_body_argument("uom_id", "").strip()

        error = first_error(
            validate_name(name, "Product name"),
            validate_positive_int(category_id, "Category"),
            validate_positive_int(uom_id, "UOM"),
        )
        if error:
            self.redirect_with_error("/master/product-master", error)
            return

        dup = await self.db.fetchrow(
            "SELECT product_master_id FROM product_master WHERE master_product_name = $1", name
        )
        if dup:
            self.redirect_with_error("/master/product-master", "A product with this name already exists.")
            return

        await self.db.execute(
            "INSERT INTO product_master (master_product_name, product_category_id, uom_id) VALUES ($1, $2, $3)",
            name, int(category_id), int(uom_id),
        )
        self.redirect("/master/product-master")

class ProductMasterEditHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT product_master_id FROM product_master WHERE product_master_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/product-master", "Product record not found.")
            return

        name = self.get_body_argument("name", "").strip()
        category_id = self.get_body_argument("category_id", "").strip()
        uom_id = self.get_body_argument("uom_id", "").strip()

        error = first_error(
            validate_name(name, "Product name"),
            validate_positive_int(category_id, "Category"),
            validate_positive_int(uom_id, "UOM"),
        )
        if error:
            self.redirect_with_error("/master/product-master", error)
            return

        dup = await self.db.fetchrow(
            "SELECT product_master_id FROM product_master WHERE master_product_name = $1 AND product_master_id != $2",
            name, int(item_id),
        )
        if dup:
            self.redirect_with_error("/master/product-master", "A product with this name already exists.")
            return

        await self.db.execute(
            "UPDATE product_master SET master_product_name = $1, product_category_id = $2, uom_id = $3 WHERE product_master_id = $4",
            name, int(category_id), int(uom_id), int(item_id),
        )
        self.redirect("/master/product-master")

class ProductMasterDeleteHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT product_master_id FROM product_master WHERE product_master_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/product-master", "Product record not found.")
            return

        await self.db.execute("DELETE FROM product_master WHERE product_master_id = $1", int(item_id))
        self.redirect("/master/product-master")