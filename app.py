import os
import asyncio
import logging
import tornado.web
import tornado.ioloop
from tornado.log import enable_pretty_logging
from db import create_pool
from handlers.base import NotFoundHandler
from handlers.auth import LoginHandler, LogoutHandler, ChangePasswordHandler
from handlers.dashboard import DashboardHandler
from handlers.admin import AdminPermissionsHandler, AdminPermissionsUpdateHandler, AdminResetPasswordHandler
from handlers.factory import FactoryHandler, FactoryEditHandler, FactoryDeleteHandler
from handlers.department import DepartmentHandler, DepartmentEditHandler, DepartmentDeleteHandler
from handlers.session_master import SessionMasterHandler, SessionEditHandler, SessionDeleteHandler
from handlers.store import StoreHandler, StoreEditHandler, StoreDeleteHandler
from handlers.product import ProductHandler, ProductEditHandler, ProductDeleteHandler
from handlers.uom import UomHandler, UomEditHandler, UomDeleteHandler
from handlers.supplier import SupplierHandler, SupplierEditHandler, SupplierDeleteHandler
from handlers.product_category import ProductCategoryHandler, ProductCategoryEditHandler, ProductCategoryDeleteHandler
from handlers.product_master import ProductMasterHandler, ProductMasterEditHandler, ProductMasterDeleteHandler
from handlers.admin import AdminDeleteUserHandler

from handlers.admin import AdminCreateUserHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COOKIE_SECRET = "2026"
APP_PORT = 8888

def make_app(db_pool):
    settings = {
        "template_path": os.path.join(BASE_DIR, "templates"),
        "static_path": os.path.join(BASE_DIR, "static"),
        "cookie_secret": COOKIE_SECRET,
        "login_url": "/login",
        "debug": True,
        "db_pool": db_pool,
        "default_handler_class": NotFoundHandler,
    }

    return tornado.web.Application(
        [
            (r"/", DashboardHandler),
            (r"/dashboard", DashboardHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/change-password", ChangePasswordHandler),
            (r"/admin/permissions", AdminPermissionsHandler),
            (r"/admin/permissions/(\d+)", AdminPermissionsUpdateHandler),
            (r"/admin/permissions/(\d+)/reset-password", AdminResetPasswordHandler),
            (r"/master/factory", FactoryHandler),
            (r"/master/factory/(\d+)/edit", FactoryEditHandler),
            (r"/master/factory/(\d+)/delete", FactoryDeleteHandler),
            (r"/master/department", DepartmentHandler),
            (r"/master/department/(\d+)/edit", DepartmentEditHandler),
            (r"/master/department/(\d+)/delete", DepartmentDeleteHandler),
            (r"/master/session", SessionMasterHandler),
            (r"/master/session/(\d+)/edit", SessionEditHandler),
            (r"/master/session/(\d+)/delete", SessionDeleteHandler),
            (r"/master/store", StoreHandler),
            (r"/master/store/(\d+)/edit", StoreEditHandler),
            (r"/master/store/(\d+)/delete", StoreDeleteHandler),
            (r"/master/product", ProductHandler),
            (r"/master/product/(\d+)/edit", ProductEditHandler),
            (r"/master/product/(\d+)/delete", ProductDeleteHandler),
            (r"/master/uom", UomHandler),
            (r"/master/uom/(\d+)/edit", UomEditHandler),
            (r"/master/uom/(\d+)/delete", UomDeleteHandler),
            (r"/master/supplier", SupplierHandler),
            (r"/master/supplier/(\d+)/edit", SupplierEditHandler),
            (r"/master/supplier/(\d+)/delete", SupplierDeleteHandler),
            (r"/master/product-category", ProductCategoryHandler),
            (r"/master/product-category/(\d+)/edit", ProductCategoryEditHandler),
            (r"/master/product-category/(\d+)/delete", ProductCategoryDeleteHandler),
            (r"/master/product-master", ProductMasterHandler),
            (r"/master/product-master/(\d+)/edit", ProductMasterEditHandler),
            (r"/master/product-master/(\d+)/delete", ProductMasterDeleteHandler),
            (r"/admin/users", AdminCreateUserHandler),
            (r"/admin/users/([0-9]+)/delete", AdminDeleteUserHandler),
            
        ],
        **settings,
    )

async def main():
    logging.getLogger().setLevel(logging.INFO)
    enable_pretty_logging()

    db_pool = await create_pool()
    app = make_app(db_pool)

    app.listen(APP_PORT)
    print(f"Server Running ->>>>> http://localhost:{APP_PORT}")

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())