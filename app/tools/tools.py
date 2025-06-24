from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import List
from sqlmodel import select
from datetime import datetime, timedelta
from app.models import Appointment, Doctor
from app.core.database import get_session
import os
import json

load_dotenv()

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

@mcp.tool(description="Check 30-minute slot availability for a specific doctor by name and date (YYYY-MM-DD), integrating with Google Calendar.")
async def availability_tool(doctor_name: str, date: str) -> List[str]:
    session = get_session()
    doctor = session.exec(select(Doctor).where(Doctor.name == doctor_name)).first()
    if not doctor:
        return [f"Doctor '{doctor_name}' not found. Please add the doctor first using their name, specialization, and email."]

    # Check local database bookings
    booked = session.exec(
        select(Appointment.time_slot).where(
            (Appointment.doctor_id == doctor.id) & (Appointment.date == date)
        )
    ).all()
    booked_set = set(booked)

    # Check Google Calendar availability
    google_booked = await check_google_calendar_availability(doctor.email, date)
    booked_set.update(google_booked)

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
    import smtplib
    import os
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        # Email configuration from environment variables
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not smtp_username or not smtp_password:
            return "SMTP credentials not configured. Please set SMTP_USERNAME and SMTP_PASSWORD environment variables."
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = f"Appointment Confirmation with Dr. {doctor_name}"
        
        # Email body
        body = f"""
        Dear {name},
        
        Your appointment has been successfully booked!
        
        Details:
        - Doctor: Dr. {doctor_name}
        - Date: {date}
        - Time: {time_slot}
        
        Please arrive 15 minutes early for your appointment.
        
        Best regards,
        Appointment Booking System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, email, text)
        server.quit()
        
        return f"Confirmation email sent successfully to {email} for appointment with Dr. {doctor_name} on {date} at {time_slot}."
        
    except Exception as e:
        return f"Failed to send email: {str(e)}"


async def check_google_calendar_availability(doctor_email: str, date: str) -> List[str]:
    """Check Google Calendar for existing appointments and return booked time slots."""
    try:
        google_creds = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        if not google_creds:
            return []
        
        creds_data = json.loads(google_creds)
        creds = Credentials.from_authorized_user_info(creds_data)
        
        service = build('calendar', 'v3', credentials=creds)
        
        # Set time range for the specific date
        start_datetime = f"{date}T09:00:00Z"
        end_datetime = f"{date}T17:00:00Z"
        
        # Get events for the doctor's calendar
        events_result = service.events().list(
            calendarId=doctor_email,
            timeMin=start_datetime,
            timeMax=end_datetime,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        booked_slots = []
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            if 'T' in start:
                # Parse the datetime and extract time slot
                event_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_slot = event_time.strftime("%H:%M")
                booked_slots.append(time_slot)
        
        return booked_slots
        
    except Exception as e:
        print(f"Error checking Google Calendar: {e}")
        return []  # Return empty list if Google Calendar check fails

@mcp.tool(description="Add prompts and context to help users interact with the appointment system more effectively.")
async def get_system_prompts() -> str:
    return """
    Available Commands and Prompts:
    
    1. ADD DOCTOR: "Add Dr. [Name] as a [Specialization] with email [email@domain.com]"
    2. CHECK AVAILABILITY: "Check availability for Dr. [Name] on [YYYY-MM-DD]"
    3. BOOK APPOINTMENT: "Book appointment for [Patient Name] with email [email] with Dr. [Doctor Name] on [YYYY-MM-DD] at [HH:MM]"
    4. SEND CONFIRMATION: "Send confirmation email to [email] for appointment with Dr. [Doctor Name] on [date] at [time]"
    
    Example Interactions:
    - "Add Dr. Smith as a Cardiologist with email smith@hospital.com"
    - "Check availability for Dr. Smith on 2024-01-15"
    - "Book appointment for John Doe with email john@email.com with Dr. Smith on 2024-01-15 at 10:00"
    - "Send confirmation email to john@email.com for appointment with Dr. Smith on 2024-01-15 at 10:00"
    
    System Features:
    - 30-minute appointment slots from 9:00 AM to 5:00 PM
    - Google Calendar integration for availability checking
    - SMTP email confirmations
    - PostgreSQL database for appointment storage
    """

__all__ = ["mcp"]
