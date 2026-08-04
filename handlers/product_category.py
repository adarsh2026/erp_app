from tornado.web import authenticated
from handlers.base import BaseHandler
from handlers.validators import validate_name

def _has_access(handler, permissions):
    return handler.is_admin() or "material_management" in permissions

class ProductCategoryHandler(BaseHandler):
    @authenticated
    async def get(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return
        rows = await self.db.fetch("SELECT product_category_id, category_name FROM product_categories ORDER BY product_category_id DESC")
        self.render(    
            "product_category.html",
            user=self.current_user,
            permissions=permissions,
            categories=rows,
        )

    @authenticated
    async def post(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        name = self.get_body_argument("name", "").strip()

        error = validate_name(name, "Category name")
        if error:
            self.redirect_with_error("/master/product-category", error)
            return

        dup = await self.db.fetchrow(
            "SELECT product_category_id FROM product_categories WHERE category_name = $1", name
        )
        if dup:
            self.redirect_with_error("/master/product-category", "A category with this name already exists.")
            return

        await self.db.execute("INSERT INTO product_categories (category_name) VALUES ($1)", name)
        self.redirect("/master/product-category")


class ProductCategoryEditHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT product_category_id FROM product_categories WHERE product_category_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/product-category", "Category record not found.")
            return

        name = self.get_body_argument("name", "").strip()

        error = validate_name(name, "Category name")
        if error:
            self.redirect_with_error("/master/product-category", error)
            return

        dup = await self.db.fetchrow(
            "SELECT product_category_id FROM product_categories WHERE category_name = $1 AND product_category_id != $2",
            name, int(item_id),
        )
        if dup:
            self.redirect_with_error("/master/product-category", "A category with this name already exists.")
            return

        await self.db.execute(
            "UPDATE product_categories SET category_name = $1 WHERE product_category_id = $2", name, int(item_id)
        )
        self.redirect("/master/product-category")


class ProductCategoryDeleteHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT product_category_id FROM product_categories WHERE product_category_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/product-category", "Category record not found.")
            return

        await self.db.execute("DELETE FROM product_categories WHERE product_category_id = $1", int(item_id))
        self.redirect("/master/product-category")