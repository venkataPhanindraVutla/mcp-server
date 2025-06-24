from sqlmodel import SQLModel, Field

class Appointment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    time_slot: str
    doctor_id: int

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    hashed_password: str
    role: str  # "doctor" or "patient"

class Doctor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    specialization: str
    email: str