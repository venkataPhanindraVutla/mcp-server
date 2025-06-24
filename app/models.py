from sqlmodel import SQLModel, Field

class Appointment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    time_slot: str