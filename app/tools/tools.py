# Applying the changes by adding SMS functionality and modifying the doctor reports tool.
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any
from sqlmodel import select, func
from datetime import datetime, timedelta, date
from app.models import Appointment, Doctor, User, ChatSession, UserRole
from app.core.database import get_session
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client

load_dotenv()

mcp = FastMCP("appointment")

# Session management for conversation continuity
session_contexts = {}

@mcp.tool(description="Initialize or get chat session context for conversation continuity")
async def manage_session(user_id: int, action: str = "get", context_data: str = None) -> str:
    session = get_session()

    if action == "create" or action == "update":
        # Find existing session or create new one
        chat_session = session.exec(
            select(ChatSession).where(ChatSession.user_id == user_id)
        ).first()

        if not chat_session:
            chat_session = ChatSession(user_id=user_id, session_data=context_data or "{}")
            session.add(chat_session)
        else:
            chat_session.session_data = context_data or "{}"
            chat_session.updated_at = datetime.utcnow()

        session.commit()
        return f"Session {action}d successfully"

    elif action == "get":
        chat_session = session.exec(
            select(ChatSession).where(ChatSession.user_id == user_id)
        ).first()

        if chat_session:
            return chat_session.session_data
        else:
            return "{}"

@mcp.tool(description="Register a new user (patient or doctor) with email, name, password, and role")
async def register_user(email: str, name: str, password: str, role: str, specialization: str = None) -> str:
    session = get_session()

    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        return f"User with email {email} already exists"

    # Create new user
    user = User(
        email=email,
        name=name,
        password_hash=password,  # In production, use proper hashing
        role=UserRole(role.lower())
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # If doctor, create doctor profile
    if role.lower() == "doctor" and specialization:
        doctor = Doctor(
            name=name,
            specialization=specialization,
            email=email,
            user_id=user.id
        )
        session.add(doctor)
        session.commit()

    return f"{role.title()} {name} registered successfully with email {email}"

@mcp.tool(description="Authenticate user with email and password, returns user info")
async def authenticate_user(email: str, password: str) -> str:
    session = get_session()
    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if not user or user.password_hash != password: 
        return "Invalid credentials"

    user_info = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }

    return json.dumps(user_info)

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

@mcp.tool(description="Book an appointment for a patient by user_id, doctor name, date and desired 30-minute time slot.")
async def booking_tool(user_id: int, time_slot: str, date: str, doctor_name: str, symptoms: str = None) -> str:
    session = get_session()

    # Get patient user
    patient = session.exec(select(User).where(User.id == user_id)).first()
    if not patient:
        return "Patient not found"

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
        patient_id=user_id,
        time_slot=time_slot,
        doctor_id=doctor.id,
        date=date,
        symptoms=symptoms
    )
    session.add(appointment)
    session.commit()

    # Send email confirmation to the patient
    email_result = await email_tool(patient.email, patient.name, time_slot, date, doctor_name)

    # Send SMS notification to the patient
    patient_phone = getattr(patient, 'phone', None) or "+1234567890"  # You'll need to add phone field to User model
    sms_message = f"Your appointment with Dr. {doctor_name} on {date} at {time_slot} has been booked."
    sms_result = await send_sms_notification(patient_phone, sms_message)

    return f"Appointment booked for {patient.name} with Dr. {doctor_name} at {time_slot} on {date}. {email_result} {sms_result}"

@mcp.tool(description="Get doctor statistics and reports for appointments")
async def doctor_reports_tool(doctor_id: int, report_type: str, date_filter: str = None) -> str:
    session = get_session()

    doctor = session.exec(select(Doctor).where(Doctor.id == doctor_id)).first()
    if not doctor:
        return "Doctor not found"

    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    if report_type == "daily_summary":
        target_date = date_filter or str(today)
        appointments = session.exec(
            select(Appointment).where(
                (Appointment.doctor_id == doctor_id) &
                (Appointment.date == target_date)
            )
        ).all()

        total = len(appointments)
        completed = len([a for a in appointments if a.status == "completed"])
        scheduled = len([a for a in appointments if a.status == "scheduled"])

        report_text = f"Daily Summary for Dr. {doctor.name} on {target_date}:\n" \
               f"Total appointments: {total}\n" \
               f"Completed: {completed}\n" \
               f"Scheduled: {scheduled}"
        
        # Send SMS notification to doctor
        doctor_phone = getattr(doctor, 'phone', None) or "+1234567890"  # You'll need to add phone field to Doctor model
        notification_result = await send_sms_notification(
            doctor_phone, 
            f"Daily Report - {date_filter}: Total {total}, Completed {completed}, Scheduled {scheduled}"
        )

        return report_text

    elif report_type == "yesterday_visits":
        appointments = session.exec(
            select(Appointment).where(
                (Appointment.doctor_id == doctor_id) &
                (Appointment.date == str(yesterday)) &
                (Appointment.status == "completed")
            )
        ).all()

        return f"Yesterday ({yesterday}), Dr. {doctor.name} had {len(appointments)} completed visits."

    elif report_type == "today_tomorrow_appointments":
        today_appts = session.exec(
            select(Appointment).where(
                (Appointment.doctor_id == doctor_id) &
                (Appointment.date == str(today))
            )
        ).all()

        tomorrow_appts = session.exec(
            select(Appointment).where(
                (Appointment.doctor_id == doctor_id) &
                (Appointment.date == str(tomorrow))
            )
        ).all()

        return f"Appointments for Dr. {doctor.name}:\n" \
               f"Today ({today}): {len(today_appts)} appointments\n" \
               f"Tomorrow ({tomorrow}): {len(tomorrow_appts)} appointments"

    elif report_type == "symptom_analysis":
        symptom_filter = date_filter or "fever"  # Default to fever
        appointments = session.exec(
            select(Appointment).where(
                (Appointment.doctor_id == doctor_id) &
                (Appointment.symptoms.ilike(f"%{symptom_filter}%"))
            )
        ).all()

        return f"Patients with '{symptom_filter}' symptoms for Dr. {doctor.name}: {len(appointments)} cases"

    return "Invalid report type. Available types: daily_summary, yesterday_visits, today_tomorrow_appointments, symptom_analysis"

@mcp.tool(description="Send notification to doctor via email (can be extended to Slack/WhatsApp)")
async def send_doctor_notification(doctor_email: str, subject: str, message: str, notification_type: str = "email") -> str:
    if notification_type == "email":
        return await send_email_notification(doctor_email, subject, message)
    elif notification_type == "slack":
        # Placeholder for Slack integration
        return f"Slack notification sent to doctor: {subject}"
    elif notification_type == "whatsapp":
        # Placeholder for WhatsApp integration
        return f"WhatsApp notification sent to doctor: {subject}"
    else:
        return "Unsupported notification type"

async def send_email_notification(email: str, subject: str, message: str) -> str:
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if not smtp_username or not smtp_password:
            return "SMTP credentials not configured"

        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, email, text)
        server.quit()

        return f"Email notification sent successfully to {email}"

    except Exception as e:
        return f"Failed to send email: {str(e)}"

async def send_sms_notification(phone_number: str, message: str) -> str:
    """Send SMS notification using Twilio"""
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not account_sid or not auth_token or not from_number:
            return "Twilio credentials not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables."

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=message,
            from_=from_number,
            to=phone_number
        )

        return f"SMS sent successfully! Message SID: {message.sid}"
    except Exception as e:
        return f"Failed to send SMS: {str(e)}"

@mcp.tool(description="Send a confirmation email to the patient about their appointment with the doctor.")
async def email_tool(email: str, name: str, time_slot: str, date: str, doctor_name: str) -> str:
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if not smtp_username or not smtp_password:
            return "SMTP credentials not configured. Please set SMTP_USERNAME and SMTP_PASSWORD environment variables."

        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = f"Appointment Confirmation with Dr. {doctor_name}"

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

        start_datetime = f"{date}T09:00:00Z"
        end_datetime = f"{date}T17:00:00Z"

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
                event_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_slot = event_time.strftime("%H:%M")
                booked_slots.append(time_slot)

        return booked_slots

    except Exception as e:
        print(f"Error checking Google Calendar: {e}")
        return []

@mcp.tool(description="Get system prompts and available commands for users")
async def get_system_prompts() -> str:
    return """
    Smart Doctor Appointment System - Available Commands:

    AUTHENTICATION:
    - "Register as patient/doctor with email [email], name [name], password [password]"
    - "Login with email [email] and password [password]"

    PATIENT COMMANDS:
    - "Check availability for Dr. [Name] on [YYYY-MM-DD]"
    - "Book appointment with Dr. [Name] on [YYYY-MM-DD] at [HH:MM] for [symptoms]"

    DOCTOR COMMANDS:
    - "Show daily summary for [YYYY-MM-DD]"
    - "How many patients visited yesterday?"
    - "How many appointments today and tomorrow?"
    - "How many patients with [symptom]?"

    SYSTEM FEATURES:
    - Role-based access (Patient/Doctor)
    - 30-minute slots (9:00 AM - 5:00 PM)
    - Google Calendar integration
    - Email confirmations
    - Multi-turn conversations
    - Smart reporting and analytics

    EXAMPLE INTERACTIONS:
    Patient: "I want to book with Dr. Smith tomorrow at 2 PM for headache"
    Doctor: "Send me today's appointment summary via email"
    """

__all__ = ["mcp"]
`