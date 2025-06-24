from mcp.server.fastmcp import FastMCP
from typing import List
from sqlmodel import select
from datetime import datetime, timedelta
from app.models import Appointment, Doctor
from app.core.database import get_session

mcp = FastMCP("appointment")

@mcp.tool(description="Add a new doctor to the system by providing their name, specialization, and email.")
async def add_doctor(name: str, specialization: str, email: str) -> str:
    session = get_session()
    existing = session.exec(select(Doctor).where(Doctor.name == name)).first()
    if existing:
        return f"Doctor {name} already exists."

    new_doctor = Doctor(name=name, specialization=specialization, email=email)
    session.add(new_doctor)
    session.commit()
    return f"Doctor {name} added successfully."

@mcp.tool(description="Check 30-minute slot availability for a specific doctor by name and date (YYYY-MM-DD).")
async def availability_tool(doctor_name: str, date: str) -> List[str]:
    session = get_session()
    doctor = session.exec(select(Doctor).where(Doctor.name == doctor_name)).first()
    if not doctor:
        return [f"Doctor '{doctor_name}' not found. Please add the doctor first using their name, specialization, and email."]

    booked = session.exec(
        select(Appointment.time_slot).where(
            (Appointment.doctor_id == doctor.id) & (Appointment.date == date)
        )
    ).all()

    booked_set = set(booked)
    start_time = datetime.strptime("09:00", "%H:%M")
    end_time = datetime.strptime("17:00", "%H:%M")

    slots = []
    current = start_time
    while current < end_time:
        slot_str = current.strftime("%H:%M")
        if slot_str not in booked_set:
            slots.append(slot_str)
        current += timedelta(minutes=30)

    return slots

@mcp.tool(description="Book an appointment for a patient by name, email, doctor name, date and desired 30-minute time slot.")
async def booking_tool(name: str, email: str, time_slot: str, date: str, doctor_name: str) -> str:
    session = get_session()
    doctor = session.exec(select(Doctor).where(Doctor.name == doctor_name)).first()
    if not doctor:
        return f"Doctor '{doctor_name}' not found. Please add them first."

    exists = session.exec(
        select(Appointment).where(
            (Appointment.time_slot == time_slot) &
            (Appointment.date == date) &
            (Appointment.doctor_id == doctor.id)
        )
    ).first()
    if exists:
        return f"Slot '{time_slot}' on {date} is already booked for Dr. {doctor_name}."

    appointment = Appointment(
        name=name,
        email=email,
        time_slot=time_slot,
        doctor_id=doctor.id,
        date=date
    )
    session.add(appointment)
    session.commit()
    return f"Appointment booked for {name} with Dr. {doctor_name} at {time_slot} on {date}."

@mcp.tool(description="Send a confirmation email to the patient about their appointment with the doctor.")
async def email_tool(email: str, name: str, time_slot: str, date: str, doctor_name: str) -> str:
    return f"Email sent to {email}: Dear {name}, your appointment with Dr. {doctor_name} at {time_slot} on {date} is confirmed!"


__all__ = ["mcp"]
