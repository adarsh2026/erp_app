from datetime import date
from tornado.web import authenticated
from handlers.base import BaseHandler
from handlers.validators import validate_name, validate_required, first_error

def _has_access(handler, permissions):
    return handler.is_admin() or "general_master_data" in permissions

def validate_dates(start_date, end_date):
    error = first_error(
        validate_required(start_date, "Start date"),
        validate_required(end_date, "End date"),
    )
    if error:
        return error

    try:
        start = date.fromisoformat(start_date.strip())
        end = date.fromisoformat(end_date.strip())
    except ValueError:
        return "Dates must be valid (YYYY-MM-DD)."

    if end < start:
        return "End date cannot be before start date."

    return None


class SessionMasterHandler(BaseHandler):
    @authenticated
    async def get(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return
        rows = await self.db.fetch(
            "SELECT session_id, session_name, start_date, end_date FROM sessions ORDER BY session_id DESC"
        )
        self.render(
            "session.html",
            user=self.current_user,
            permissions=permissions,
            sessions=rows,
        )

    @authenticated
    async def post(self):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        name = self.get_body_argument("name", "").strip()
        start_date = self.get_body_argument("start_date", "").strip()
        end_date = self.get_body_argument("end_date", "").strip()

        error = first_error(
            validate_name(name, "Session name"),
            validate_dates(start_date, end_date),
        )
        if error:
            self.redirect_with_error("/master/session", error)
            return

        dup = await self.db.fetchrow(
            "SELECT session_id FROM sessions WHERE session_name = $1", name
        )
        if dup:
            self.redirect_with_error("/master/session", "A session with this name already exists.")
            return

        await self.db.execute(
            "INSERT INTO sessions (session_name, start_date, end_date) VALUES ($1, $2, $3)",
            name, date.fromisoformat(start_date), date.fromisoformat(end_date),
        )
        self.redirect("/master/session")


class SessionEditHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT session_id FROM sessions WHERE session_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/session", "Session record not found.")
            return

        name = self.get_body_argument("name", "").strip()
        start_date = self.get_body_argument("start_date", "").strip()
        end_date = self.get_body_argument("end_date", "").strip()

        error = first_error(
            validate_name(name, "Session name"),
            validate_dates(start_date, end_date),
        )
        if error:
            self.redirect_with_error("/master/session", error)
            return

        dup = await self.db.fetchrow(
            "SELECT session_id FROM sessions WHERE session_name = $1 AND session_id != $2",
            name, int(item_id),
        )
        if dup:
            self.redirect_with_error("/master/session", "A session with this name already exists.")
            return

        await self.db.execute(
            "UPDATE sessions SET session_name = $1, start_date = $2, end_date = $3 WHERE session_id = $4",
            name, date.fromisoformat(start_date), date.fromisoformat(end_date), int(item_id),
        )
        self.redirect("/master/session")


class SessionDeleteHandler(BaseHandler):
    @authenticated
    async def post(self, item_id):
        permissions = await self.get_permissions()
        if not _has_access(self, permissions):
            self.redirect("/dashboard")
            return

        existing = await self.db.fetchrow("SELECT session_id FROM sessions WHERE session_id = $1", int(item_id))
        if not existing:
            self.redirect_with_error("/master/session", "Session record not found.")
            return

        await self.db.execute("DELETE FROM sessions WHERE session_id = $1", int(item_id))
        self.redirect("/master/session")