
# 🏥 Smart Doctor Appointment System
## 🧠 Agentic AI with MCP Integration

A full-stack web application that demonstrates agentic AI behavior using Model Context Protocol (MCP) to expose APIs and tools for dynamic discovery and invocation by AI agents.

## 🎯 Features

### ✨ Core Functionality
- **Role-based Authentication**: Patient and Doctor roles with secure login
- **Smart Appointment Scheduling**: AI-powered natural language booking
- **Multi-turn Conversations**: Context-aware chat sessions
- **Doctor Analytics**: AI-generated reports and summaries
- **Email Notifications**: Automated confirmations and alerts
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
TWILIO_PHONE_NUMBER=+1234567890your_app_password

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
   uvicorn server:app --host 0.0.0.0 --port 3000
   ```

3. **Access the Application**:
   - API: `http://localhost:3000`
   - Documentation: `http://localhost:3000/docs`
   - Dashboard: `http://localhost:3000/dashboard`

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
  "specialization": "Cardiology" // Required for doctors
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

#### GET `/users`
Get all users (for admin purposes)

**Response**:
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "patient"
  }
]
```

#### GET `/current-user/{user_id}`
Get current user details

**Response**:
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "patient"
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

#### POST `/doctors`
Add a new doctor

**Query Parameters**:
- `name`: Doctor's name
- `specialization`: Medical specialization
- `email`: Doctor's email

**Response**:
```json
{
  "message": "Doctor Dr. Smith added successfully"
}
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

**Response**:
```json
{
  "doctor": "Dr. Smith",
  "report": "Daily Summary for Dr. Smith on 2024-01-15:\nTotal appointments: 5\nCompleted: 3\nScheduled: 2"
}
```

### 📅 Appointment Management

#### GET `/appointments`
Get appointments

**Query Parameters** (optional):
- `user_id`: Filter by patient ID
- `doctor_id`: Filter by doctor ID

**Response**:
```json
[
  {
    "id": 1,
    "patient_name": "John Doe",
    "doctor_name": "Dr. Smith",
    "date": "2024-01-15",
    "time_slot": "10:00",
    "status": "scheduled",
    "symptoms": "headache"
  }
]
```

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
  "message": "Appointment booked for John Doe with Dr. Smith at 10:00 on 2024-01-15",
  "status": "success"
}
```

#### GET `/availability/{doctor_name}/{date}`
Check doctor availability

**Path Parameters**:
- `doctor_name`: Doctor's name
- `date`: Date in YYYY-MM-DD format

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

**Response**:
```json
{
  "response": "AI Assistant response based on the message",
  "user_id": 1
}
```

### 🗣️ Session Management

#### POST `/session`
Manage chat sessions for conversation continuity

**Query Parameters**:
- `user_id`: User ID
- `action`: "create", "update", or "get"
- `context_data`: JSON string (optional)

#### GET `/session/{user_id}`
Get user's chat session context

**Response**:
```json
{
  "user_id": 1,
  "context": {
    "last_doctor": "Dr. Smith",
    "preferred_time": "afternoon"
  }
}
```

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

### Reporting Tools
- `doctor_reports_tool`: Generate various doctor reports
- `send_doctor_notification`: Send notifications to doctors

### System Tools
- `get_system_prompts`: Get available commands and help

## 🎯 Usage Examples

### Patient Workflow
```python
# 1. Register as patient
POST /register
{
  "email": "patient@example.com",
  "name": "Jane Doe",
  "password": "password123",
  "role": "patient"
}

# 2. Check doctor availability
GET /availability/Dr. Smith/2024-01-15

# 3. Book appointment
POST /appointments/book?user_id=1
{
  "doctor_name": "Dr. Smith",
  "date": "2024-01-15",
  "time_slot": "10:00",
  "symptoms": "headache"
}
```

### Doctor Workflow
```python
# 1. Register as doctor
POST /register
{
  "email": "doctor@hospital.com",
  "name": "Dr. Smith",
  "password": "password123",
  "role": "doctor",
  "specialization": "Cardiology"
}

# 2. Get daily report
POST /doctors/1/reports
{
  "report_type": "daily_summary",
  "date_filter": "2024-01-15"
}

# 3. Check appointments
GET /appointments?doctor_id=1
```

### Natural Language Examples
```
Patient: "I want to book an appointment with Dr. Ahuja tomorrow morning"
System: Checks availability → Books slot → Sends confirmation

Doctor: "How many patients visited yesterday?"
System: Queries database → Generates report → Sends notification

Patient: "Check Dr. Smith's availability for Friday afternoon"
System: Returns available afternoon slots

Patient: "Book the 3 PM slot"
System: Uses conversation context → Books appointment
```

## 🔧 Technical Architecture

### Backend Stack
- **FastAPI**: Modern web framework with automatic API documentation
- **SQLModel**: Type-safe database operations with Pydantic integration
- **PostgreSQL**: Robust relational database for appointments and users
- **MCP (Model Context Protocol)**: Tool exposure for AI agents

### Key Components
- **Authentication**: Role-based system (Patient/Doctor)
- **Session Management**: Conversation context tracking
- **Email Integration**: SMTP for notifications
- **Calendar Integration**: Google Calendar API
- **AI Tools**: MCP-exposed functions for LLM interaction

### Database Schema
```sql
-- Users table
users: id, email, name, role, password_hash, created_at

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
uvicorn server:app --host 0.0.0.0 --port 3000 --reload
```

### Production (Replit)
```bash
uvicorn server:app --host 0.0.0.0 --port 3000
```

## 🧠 AI Integration

To integrate with your preferred LLM:

1. **Choose your LLM provider** (OpenAI, Claude, Mistral, etc.)
2. **Configure API credentials** in environment variables
3. **Update the `/chat` endpoint** to call your LLM
4. **Configure tool calling** to use the MCP tools
5. **Implement conversation context** using session management

Example LLM integration:
```python
import openai

async def process_with_llm(message: str, user_id: int):
    # Get conversation context
    context = await manage_session(user_id, "get")
    
    # Call LLM with available tools
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": await get_system_prompts()},
            {"role": "user", "content": message}
        ],
        tools=get_mcp_tools(),
        tool_choice="auto"
    )
    
    # Execute tool calls and return response
    return process_tool_calls(response)
```

## 🎯 Features Implemented

✅ **Role-based Authentication**: Patient and Doctor roles  
✅ **Smart Appointment Booking**: Natural language interface  
✅ **Multi-turn Conversations**: Session context management  
✅ **Doctor Reports**: AI-powered analytics  
✅ **Email Notifications**: SMTP integration  
✅ **Google Calendar**: Availability checking  
✅ **PostgreSQL Database**: Persistent data storage  
✅ **MCP Integration**: Tool exposure for AI agents  
✅ **RESTful API**: Complete CRUD operations  
✅ **Auto Documentation**: FastAPI Swagger UI  

## 🛠️ Future Enhancements

- Frontend React application
- Real-time notifications (WebSocket)
- Slack/WhatsApp integration
- Advanced AI auto-rescheduling
- Medical records integration
- Video consultation booking
- Mobile app support

## 📝 License

This project is built for educational and demonstration purposes as part of the Full-Stack Developer Intern Assignment.

---

**🚀 Ready to experience the future of healthcare appointment management with AI!**
