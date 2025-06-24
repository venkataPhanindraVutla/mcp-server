from mcp.server.fastmcp import FastMCP
from typing import List
from sqlmodel import select
from app.models import Appointment
from app.core.database import get_session

mcp = FastMCP("appointment")

@mcp.tool()
async def availability_tool() -> List[str]:
    all_slots = ["10:00 AM", "11:30 AM", "2:00 PM", "4:00 PM"]
    session = get_session()
    booked = session.exec(select(Appointment.time_slot)).all()
    return [slot for slot in all_slots if slot not in booked]


@mcp.tool()
async def booking_tool(name: str, time_slot: str) -> str:
    session = get_session()
    exists = session.exec(select(Appointment).where(Appointment.time_slot == time_slot)).first()
    if exists:
        return f"Slot '{time_slot}' is already booked."

    appointment = Appointment(name=name, time_slot=time_slot)
    session.add(appointment)
    session.commit()
    return f"Appointment booked for {name} at {time_slot}."


@mcp.tool()
async def email_tool(email: str, name: str, time_slot: str) -> str:
    return f"Email sent to {email}: Dear {name}, your appointment at {time_slot} is confirmed!"