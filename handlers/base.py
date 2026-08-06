import tornado.web
from urllib.parse import quote

class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):  
        return self.application.settings["db_pool"]

    def get_current_user(self):
      
        user_id = self.get_secure_cookie("user_id")
        if not user_id:
            return None
        return {"id": user_id.decode("utf-8")}

    def redirect_with_error(self, url, message):
        
        sep = "&" if "?" in url else "?"
        self.redirect(f"{url}{sep}form_error={quote(message)}")


    async def prepare(self):
    
        if self.current_user is not None:
            row = await self.db.fetchrow(
                "SELECT users.username, users.full_name, roles.role_name "
                "FROM users JOIN roles ON users.role_id = roles.role_id "
                "WHERE users.user_id = $1",
                int(self.current_user["id"]),
            )
            if row:
                self.current_user["username"] = row["username"]
                self.current_user["full_name"] = row["full_name"]
                self.current_user["role"] = row["role_name"]
            else:
               
                self.current_user["username"] = ""
                self.current_user["full_name"] = ""
                self.current_user["role"] = "user"

    def is_admin(self):
        return self.current_user is not None and self.current_user.get("role") in ("admin", "superadmin")

    def is_superadmin(self):
        return self.current_user is not None and self.current_user.get("role") == "superadmin"

    async def get_permissions(self):
       
        if self.current_user is None:
            return set()

        if self.is_admin():
            return {"general_master_data", "material_management"}

        rows = await self.db.fetch(
            "SELECT module_name FROM user_permissions WHERE user_id = $1",
            int(self.current_user["id"]),
        )
        return {r["module_name"] for r in rows}

    def write_error(self, status_code, **kwargs):
        self.clear()
        self.set_status(status_code)

        pages = {
            404: ("Page not found", "The page you're looking for doesn't exist or may have been moved."),
            403: ("Access denied", "You don't have permission to view this page."),
            405: ("Method not allowed", "That action isn't supported on this page."),
            500: ("Something went wrong", "An unexpected error occurred on our end. Please try again."),
        }
        title, message = pages.get(
            status_code, ("Error", "Something went wrong. Please try again.")
        )   

        self.render(    
            "error.html",
            status_code=status_code,
            error_title=title,
            error_message=message,
        )


class NotFoundHandler(BaseHandler):
    def prepare(self):
        raise tornado.web.HTTPError(404)

    def get(self):
        pass