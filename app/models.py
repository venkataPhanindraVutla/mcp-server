
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    role: UserRole
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    appointments_as_patient: List["Appointment"] = Relationship(back_populates="patient", foreign_keys="[Appointment.patient_id]")
    doctor_profile: Optional["Doctor"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})

class Doctor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    specialization: str
    email: str = Field(unique=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="doctor_profile")
    appointments: List["Appointment"] = Relationship(back_populates="doctor")

class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="user.id")
    doctor_id: int = Field(foreign_key="doctor.id")
    date: str
    time_slot: str
    status: str = Field(default="scheduled")  # scheduled, completed, cancelled
    symptoms: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    patient: User = Relationship(back_populates="appointments_as_patient", foreign_keys="[Appointment.patient_id]")
    doctor: Doctor = Relationship(back_populates="appointments")

class ChatSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    session_data: str  # JSON string for context
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
