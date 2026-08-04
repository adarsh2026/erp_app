from tornado.web import authenticated
from handlers.base import BaseHandler
from handlers.validators import validate_name, validate_code, first_error

def _has_access(handler, permissions):
    return handler.is_admin() or "general_master_data" in permissions

class ProductHandler(BaseHandler):
    @authenticated
    async def get(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return
        rows = await self.db.fetch("SELECT product_id, product_name, product_code FROM products ORDER BY product_id DESC")
        self.render(
            "product.html",
            user=self.current_user,
            permissions=permissions,
            products=rows,
        )

    @authenticated
    async def post(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        name = self.get_body_argument("name", "").strip()
        code = self.get_body_argument("code", "").strip()

        error = first_error(
            validate_name(name, "Product name"),
            validate_code(code, "Product code"),
        )
        if error:
            self.redirect_with_error("/master/product", error)
            return

        if code:
            dup = await self.db.fetchrow("SELECT product_id FROM products WHERE product_code = $1", code)
            if dup:
                self.redirect_with_error("/master/product", "A product with this code already exists.")
                return

        await self.db.execute(
            "INSERT INTO products (product_name, product_code) VALUES ($1, $2)",
            name, code or None,
        )
        self.redirect("/master/product")


class ProductEditHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT product_id FROM products WHERE product_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/product", "Product record not found.")
            return

        name = self.get_body_argument("name", "").strip()
        code = self.get_body_argument("code", "").strip()

        error = first_error(
            validate_name(name, "Product name"),
            validate_code(code, "Product code"),
        )
        if error:
            self.redirect_with_error("/master/product", error)
            return

        if code:
            dup = await self.db.fetchrow(
                "SELECT product_id FROM products WHERE product_code = $1 AND product_id != $2",
                code, int(item_id),
            )
            if dup:
                self.redirect_with_error("/master/product", "A product with this code already exists.")
                return

        await self.db.execute(
            "UPDATE products SET product_name = $1, product_code = $2 WHERE product_id = $3",
            name, code or None, int(item_id),
        )
        self.redirect("/master/product")

class ProductDeleteHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT product_id FROM products WHERE product_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/product", "Product record not found.")
            return

        await self.db.execute("DELETE FROM products WHERE product_id = $1", int(item_id))
        self.redirect("/master/product")