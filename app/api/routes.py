
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlmodel import select
from app.core.database import get_session
from app.models import User, Doctor, Appointment, UserRole
from pydantic import BaseModel
from typing import Optional, List
import json

router = APIRouter(tags=["General"])

# Pydantic models for requests
class UserRegister(BaseModel):
    email: str
    name: str
    password: str
    role: str
    specialization: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class AppointmentRequest(BaseModel):
    doctor_name: str
    date: str
    time_slot: str
    symptoms: Optional[str] = None

class ReportRequest(BaseModel):
    report_type: str
    date_filter: Optional[str] = None

@router.get("/")
async def root():
    return HTMLResponse("""
    <h1>🏥 Smart Doctor Appointment System</h1>
    <h2>🧠 Agentic AI with MCP Integration</h2>
    <p><strong>Features:</strong></p>
    <ul>
        <li>🔐 Role-based Authentication (Patient/Doctor)</li>
        <li>📅 Smart Appointment Scheduling</li>
        <li>📊 AI-powered Doctor Reports</li>
        <li>💬 Multi-turn Conversation Support</li>
        <li>📧 Email Notifications</li>
        <li>🗓️ Google Calendar Integration</li>
    </ul>
    <p><a href="/docs">📋 API Documentation</a> | <a href="/dashboard">📊 Dashboard</a></p>
    """)

@router.get("/status")
async def status():
    return JSONResponse({
        "status": "running",
        "version": "1.0.0",
        "features": {
            "authentication": "Role-based (Patient/Doctor)",
            "appointments": "Smart scheduling with AI",
            "reports": "AI-powered analytics",
            "integrations": ["Google Calendar", "SMTP Email", "PostgreSQL"],
            "conversation": "Multi-turn support with context"
        },
        "mcp_tools": [
            "register_user", "authenticate_user", "manage_session",
            "add_doctor", "availability_tool", "booking_tool", 
            "doctor_reports_tool", "send_doctor_notification",
            "email_tool", "get_system_prompts"
        ],
        "endpoints": {
            "auth": ["/register", "/login", "/users", "/current-user"],
            "appointments": ["/appointments", "/appointments/book", "/availability"],
            "doctors": ["/doctors", "/doctors/reports"],
            "system": ["/", "/status", "/dashboard"]
        }
    })

# Authentication endpoints
@router.post("/register")
async def register_user(user_data: UserRegister):
    session = get_session()
    
    # Check if user exists
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=user_data.password,  # In production, hash this
        role=UserRole(user_data.role.lower())
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create doctor profile if needed
    if user_data.role.lower() == "doctor" and user_data.specialization:
        doctor = Doctor(
            name=user_data.name,
            specialization=user_data.specialization,
            email=user_data.email,
            user_id=user.id
        )
        session.add(doctor)
        session.commit()
    
    return {
        "message": f"{user_data.role.title()} registered successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

@router.post("/login")
async def login_user(login_data: UserLogin):
    session = get_session()
    user = session.exec(select(User).where(User.email == login_data.email)).first()
    
    if not user or user.password_hash != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

@router.get("/users")
async def get_users():
    session = get_session()
    users = session.exec(select(User)).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users]

@router.get("/current-user/{user_id}")
async def get_current_user(user_id: int):
    session = get_session()
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }

# Doctor endpoints
@router.get("/doctors")
async def get_doctors():
    session = get_session()
    doctors = session.exec(select(Doctor)).all()
    return [{"id": d.id, "name": d.name, "specialization": d.specialization, "email": d.email} for d in doctors]

@router.post("/doctors")
async def add_doctor(name: str, specialization: str, email: str):
    session = get_session()
    existing = session.exec(select(Doctor).where(Doctor.email == email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Doctor already exists")
    
    doctor = Doctor(name=name, specialization=specialization, email=email)
    session.add(doctor)
    session.commit()
    
    return {"message": f"Doctor {name} added successfully"}

@router.post("/doctors/{doctor_id}/reports")
async def get_doctor_report(doctor_id: int, report_data: ReportRequest):
    session = get_session()
    doctor = session.exec(select(Doctor).where(Doctor.id == doctor_id)).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Import the MCP tool function
    from app.tools.tools import doctor_reports_tool
    report = await doctor_reports_tool(doctor_id, report_data.report_type, report_data.date_filter)
    
    return {"doctor": doctor.name, "report": report}

# Appointment endpoints
@router.get("/appointments")
async def get_appointments(user_id: Optional[int] = None, doctor_id: Optional[int] = None):
    session = get_session()
    query = select(Appointment)
    
    if user_id:
        query = query.where(Appointment.patient_id == user_id)
    if doctor_id:
        query = query.where(Appointment.doctor_id == doctor_id)
    
    appointments = session.exec(query).all()
    result = []
    
    for apt in appointments:
        patient = session.exec(select(User).where(User.id == apt.patient_id)).first()
        doctor = session.exec(select(Doctor).where(Doctor.id == apt.doctor_id)).first()
        result.append({
            "id": apt.id,
            "patient_name": patient.name if patient else "Unknown",
            "doctor_name": doctor.name if doctor else "Unknown",
            "date": apt.date,
            "time_slot": apt.time_slot,
            "status": apt.status,
            "symptoms": apt.symptoms
        })
    
    return result

@router.post("/appointments/book")
async def book_appointment(user_id: int, appointment_data: AppointmentRequest):
    session = get_session()
    
    # Import MCP tool
    from app.tools.tools import booking_tool
    result = await booking_tool(
        user_id=user_id,
        time_slot=appointment_data.time_slot,
        date=appointment_data.date,
        doctor_name=appointment_data.doctor_name,
        symptoms=appointment_data.symptoms
    )
    
    if "booked" in result.lower():
        return {"message": result, "status": "success"}
    else:
        raise HTTPException(status_code=400, detail=result)

@router.get("/availability/{doctor_name}/{date}")
async def check_availability(doctor_name: str, date: str):
    from app.tools.tools import availability_tool
    slots = await availability_tool(doctor_name, date)
    return {"doctor": doctor_name, "date": date, "available_slots": slots}

# LLM Chat endpoint for natural language processing
@router.post("/chat")
async def chat_with_ai(user_id: int, message: str):
    """
    Natural language interface for the appointment system.
    This would integrate with your chosen LLM (OpenAI, Claude, etc.)
    """
    # This is a placeholder for LLM integration
    # You would replace this with actual LLM API calls
    
    response = f"""
    🤖 AI Assistant Response:
    
    Received message: "{message}"
    User ID: {user_id}
    
    Available actions:
    - Check doctor availability
    - Book appointments  
    - Generate reports
    - Send notifications
    
    To implement full LLM integration, connect your preferred LLM service (OpenAI, Claude, etc.)
    and configure it to use the MCP tools defined in tools.py
    """
    
    return {"response": response, "user_id": user_id}

# Session management for conversation continuity
@router.post("/session")
async def manage_chat_session(user_id: int, action: str, context_data: Optional[str] = None):
    from app.tools.tools import manage_session
    result = await manage_session(user_id, action, context_data)
    return {"result": result}

@router.get("/session/{user_id}")
async def get_chat_session(user_id: int):
    from app.tools.tools import manage_session
    context = await manage_session(user_id, "get")
    return {"user_id": user_id, "context": json.loads(context)}
