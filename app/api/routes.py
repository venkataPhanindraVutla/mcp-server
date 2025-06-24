from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter(tags=["General"])

@router.get("/")
async def root():
    return HTMLResponse("<h2>Appointment Booking with FastAPI + MCP</h2>")

@router.get("/status")
async def status():
    return JSONResponse({
        "status": "running",
        "tools": ["availability_tool", "booking_tool", "email_tool"]
    })