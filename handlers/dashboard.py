from tornado.web import authenticated
from handlers.base import BaseHandler


class DashboardHandler(BaseHandler):
    @authenticated
    async def get(self):
        permissions = await self.get_permissions()
        has_gmd = self.is_admin() or "general_master_data" in permissions
        has_mm = self.is_admin() or "material_management" in permissions

        factory_count = 0
        department_count = 0
        session_count = 0
        product_count = 0
        gmd_rows = []

        if has_gmd:
            factory_count = await self.db.fetchval("SELECT COUNT(*) FROM factories")
            department_count = await self.db.fetchval("SELECT COUNT(*) FROM departments")
            session_count = await self.db.fetchval("SELECT COUNT(*) FROM sessions")
            product_count = await self.db.fetchval("SELECT COUNT(*) FROM products")

            factories = await self.db.fetch("SELECT factory_name FROM factories ORDER BY factory_id DESC LIMIT 5")
            departments = await self.db.fetch("SELECT department_name FROM departments ORDER BY department_id DESC LIMIT 5")
            sessions = await self.db.fetch("SELECT session_name FROM sessions ORDER BY session_id DESC LIMIT 5")
            products = await self.db.fetch("SELECT product_name FROM products ORDER BY product_id DESC LIMIT 5")
            uoms = await self.db.fetch("SELECT uom_name FROM uoms ORDER BY uom_id DESC LIMIT 5")

            row_count = max(
                [len(factories), len(departments), len(sessions), len(products), len(uoms)],
                default=0,
            )
            for i in range(row_count):
                gmd_rows.append({
                    "factory": factories[i]["factory_name"] if i < len(factories) else None,
                    "department": departments[i]["department_name"] if i < len(departments) else None,
                    "session": sessions[i]["session_name"] if i < len(sessions) else None,
                    "product": products[i]["product_name"] if i < len(products) else None,
                    "uom": uoms[i]["uom_name"] if i < len(uoms) else None,
                })

        mm_rows = []
        if has_mm:
            suppliers = await self.db.fetch("SELECT supplier_name FROM suppliers ORDER BY supplier_id DESC LIMIT 5")
            categories = await self.db.fetch("SELECT category_name FROM product_categories ORDER BY product_category_id DESC LIMIT 5")
            product_masters = await self.db.fetch("SELECT master_product_name FROM product_master ORDER BY product_master_id DESC LIMIT 5")
            mm_products = await self.db.fetch("SELECT product_name FROM products ORDER BY product_id DESC LIMIT 5")
            mm_uoms = await self.db.fetch("SELECT uom_name FROM uoms ORDER BY uom_id DESC LIMIT 5")

            row_count = max(
                [len(suppliers), len(categories), len(product_masters), len(mm_products), len(mm_uoms)],
                default=0,
            )
            for i in range(row_count):
                mm_rows.append({
                    "supplier": suppliers[i]["supplier_name"] if i < len(suppliers) else None,
                    "category": categories[i]["category_name"] if i < len(categories) else None,
                    "product_master": product_masters[i]["master_product_name"] if i < len(product_masters) else None,
                    "product": mm_products[i]["product_name"] if i < len(mm_products) else None,
                    "uom": mm_uoms[i]["uom_name"] if i < len(mm_uoms) else None,
                })

        self.render(
            "dashboard.html",
            user=self.current_user,
            permissions=permissions,
            has_gmd=has_gmd,
            has_mm=has_mm,
            factory_count=factory_count,
            department_count=department_count,
            session_count=session_count,
            product_count=product_count,
            gmd_rows=gmd_rows,
            mm_rows=mm_rows,
        )