# 🏥 Smart Doctor Appointment System
## 🧠 Agentic AI with MCP Integration

A full-stack web application that demonstrates agentic AI behavior using Model Context Protocol (MCP) to expose APIs and tools for dynamic discovery and invocation by AI agents.

## 🎯 Features

### ✨ Core Functionality
- **Role-based Authentication**: Patient and Doctor roles with secure login
- **Smart Appointment Scheduling**: AI-powered natural language booking
- **Multi-turn Conversations**: Context-aware chat sessions
- **Doctor Analytics**: AI-generated reports and summaries
- **Email & SMS Notifications**: Automated confirmations and alerts via SMTP and Twilio
- **Google Calendar Integration**: Real-time availability checking

### 🤖 AI Capabilities
- Natural language appointment booking
- Intelligent doctor report generation
- Context-aware conversation handling
- Automated scheduling conflict resolution

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL database
- Gmail account (for SMTP)
- Twilio account (for SMS)
- Google Calendar API credentials (optional)

### Environment Setup

Create a `.env` file in the root directory:

```env
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=appointments
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# SMTP Configuration (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Twilio Configuration (SMS)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Google Calendar API (Optional)
GOOGLE_CALENDAR_CREDENTIALS={"token": "your_token", "refresh_token": "your_refresh_token", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "your_client_id", "client_secret": "your_client_secret", "scopes": ["https://www.googleapis.com/auth/calendar"]}
```

### Installation & Running

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 5000
   ```

3. **Access the Application**:
   - API: `http://localhost:5000`
   - Documentation: `http://localhost:5000/docs`
   - Dashboard: `http://localhost:5000/dashboard`

## 📚 API Documentation

### 🔐 Authentication Endpoints

#### POST `/register`
Register a new user (patient or doctor)

**Request Body**:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "password123",
  "role": "patient",
  "phone": "+1234567890",
  "specialization": "Cardiology"
}
```

**Response**:
```json
{
  "message": "Patient registered successfully",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "patient"
  }
}
```

#### POST `/login`
Authenticate user

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "patient"
  }
}
```

### 👨‍⚕️ Doctor Management

#### GET `/doctors`
Get all doctors

**Response**:
```json
[
  {
    "id": 1,
    "name": "Dr. Smith",
    "specialization": "Cardiology",
    "email": "dr.smith@hospital.com"
  }
]
```

#### POST `/doctors/{doctor_id}/reports`
Generate doctor reports

**Request Body**:
```json
{
  "report_type": "daily_summary",
  "date_filter": "2024-01-15"
}
```

**Available Report Types**:
- `daily_summary`: Daily appointment summary
- `yesterday_visits`: Yesterday's completed visits
- `today_tomorrow_appointments`: Today and tomorrow's appointments
- `symptom_analysis`: Filter by symptoms (use date_filter for symptom)

### 📅 Appointment Management

#### GET `/appointments`
Get appointments with optional filters

**Query Parameters** (optional):
- `user_id`: Filter by patient ID
- `doctor_id`: Filter by doctor ID

#### POST `/appointments/book`
Book an appointment

**Query Parameters**:
- `user_id`: Patient's user ID

**Request Body**:
```json
{
  "doctor_name": "Dr. Smith",
  "date": "2024-01-15",
  "time_slot": "10:00",
  "symptoms": "headache"
}
```

**Response**:
```json
{
  "message": "Appointment booked for John Doe with Dr. Smith at 10:00 on 2024-01-15. Confirmation email sent successfully. SMS sent successfully!",
  "status": "success"
}
```

#### GET `/availability/{doctor_name}/{date}`
Check doctor availability

**Response**:
```json
{
  "doctor": "Dr. Smith",
  "date": "2024-01-15",
  "available_slots": ["09:00", "09:30", "10:00", "14:00", "14:30"]
}
```

### 💬 AI Chat Interface

#### POST `/chat`
Natural language interface for the appointment system

**Query Parameters**:
- `user_id`: User ID for context
- `message`: Natural language message

**Example Messages**:
- "I want to book an appointment with Dr. Smith tomorrow at 2 PM"
- "Check Dr. Johnson's availability for Friday"
- "How many patients did I see yesterday?" (for doctors)

### 🗣️ Session Management

#### POST `/session`
Manage chat sessions for conversation continuity

**Query Parameters**:
- `user_id`: User ID
- `action`: "create", "update", or "get"
- `context_data`: JSON string (optional)

## 🔧 MCP Tools

The system exposes the following MCP tools for AI agents:

### Authentication Tools
- `register_user`: Register new users
- `authenticate_user`: User login
- `manage_session`: Handle conversation context

### Appointment Tools
- `add_doctor`: Add doctors to the system
- `availability_tool`: Check doctor availability
- `booking_tool`: Book appointments
- `email_tool`: Send confirmation emails
- `send_sms_notification`: Send SMS notifications via Twilio

### Reporting Tools
- `doctor_reports_tool`: Generate various doctor reports
- `send_doctor_notification`: Send notifications to doctors

### System Tools
- `get_system_prompts`: Get available commands and help

## 🎯 Usage Examples

### Scenario 1: Patient Appointment Scheduling
```
Patient: "I want to book an appointment with Dr. Ahuja tomorrow morning"
System: 
1. Checks Dr. Ahuja's availability for tomorrow morning
2. Shows available slots (9:00 AM, 9:30 AM, 10:00 AM)
3. Patient selects preferred time
4. Books appointment
5. Sends email confirmation to patient
6. Sends SMS notification to patient
```

### Scenario 2: Doctor Reports and Notifications
```
Doctor: "How many patients visited yesterday?"
System:
1. Queries database for yesterday's completed appointments
2. Generates summary report
3. Sends SMS notification to doctor with summary
```

### Multi-turn Conversation Example
```
Patient: "Check Dr. Smith's availability for Friday afternoon"
System: "Available slots: 2:00 PM, 2:30 PM, 3:00 PM, 4:00 PM"

Patient: "Book the 3 PM slot"
System: Uses conversation context → Books 3:00 PM appointment with Dr. Smith for Friday
```

## 🔧 Technical Architecture

### Backend Stack
- **FastAPI**: Modern web framework with automatic API documentation
- **SQLModel**: Type-safe database operations with Pydantic integration
- **PostgreSQL**: Robust relational database
- **MCP (Model Context Protocol)**: Tool exposure for AI agents
- **Twilio**: SMS notifications
- **SMTP**: Email notifications

### Key Components
- **Authentication**: Role-based system (Patient/Doctor)
- **Session Management**: Conversation context tracking
- **Notification System**: Both email and SMS
- **Calendar Integration**: Google Calendar API
- **AI Tools**: MCP-exposed functions for LLM interaction

### Database Schema
```sql
-- Users table
users: id, email, name, role, password_hash, phone, created_at

-- Doctors table  
doctors: id, name, specialization, email, user_id

-- Appointments table
appointments: id, patient_id, doctor_id, date, time_slot, status, symptoms, notes, created_at

-- Chat Sessions table
chatsessions: id, user_id, session_data, created_at, updated_at
```

## 🚀 Deployment

### Local Development
```bash
uvicorn server:app --host 0.0.0.0 --port 5000 --reload
```

### Production (Replit)
```bash
uvicorn server:app --host 0.0.0.0 --port 5000
```

## ✅ Requirements Implementation Status

### ✅ Completed Features
- **Role-based Authentication**: Patient and Doctor roles implemented
- **Natural Language Appointment Booking**: MCP tools for AI agent interaction
- **Multi-turn Conversations**: Session context management
- **Doctor Reports**: Multiple report types with AI-generated summaries
- **Dual Notification System**: Email for bookings, SMS for doctor notifications
- **Google Calendar Integration**: Real-time availability checking
- **PostgreSQL Database**: Complete data persistence
- **MCP Integration**: All required tools exposed
- **FastAPI Backend**: RESTful API with auto-documentation

### 🚧 Recommended Enhancements
- **Frontend React Application**: Currently backend-only
- **JWT Authentication**: Upgrade from basic auth
- **LLM Integration**: Connect actual LLM provider for chat endpoint
- **Advanced Auto-rescheduling**: AI-powered conflict resolution

## 📝 Setup Instructions

1. **Environment Variables**: Configure all required environment variables in `.env`
2. **Database**: Ensure PostgreSQL is running and accessible
3. **Twilio**: Set up Twilio account for SMS functionality
4. **Gmail**: Configure Gmail app password for SMTP
5. **Google Calendar**: Optional - set up API credentials for calendar integration

## 🎯 Demo Scenarios

### Patient Workflow
1. Register as patient with phone number
2. Use natural language to request appointment
3. Receive email confirmation and SMS notification

### Doctor Workflow  
1. Register as doctor with specialization
2. Request daily/weekly reports via natural language
3. Receive SMS notifications with summaries

---

**🚀 A complete agentic AI solution for healthcare appointment management!**