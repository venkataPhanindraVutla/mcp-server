from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.core.database import get_session
from app.models import Appointment

templates = Jinja2Templates(directory="templates")
dashboard_router = APIRouter(tags=["Dashboard"])

@dashboard_router.get("/dashboard", response_class=HTMLResponse)
async def show_dashboard(request: Request):
    session = get_session()
    appointments = session.query(Appointment).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "appointments": appointments})