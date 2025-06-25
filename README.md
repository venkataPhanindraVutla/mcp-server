
# 🏥 Smart Doctor Appointment System
## 🧠 Agentic AI with MCP Integration

A full-stack web application that demonstrates agentic AI behavior using Model Context Protocol (MCP) to expose APIs and tools for dynamic discovery and invocation by AI agents.

## 🎯 Features

### ✨ Core Functionality
- **JWT Authentication**: Secure role-based authentication for Patients and Doctors
- **Smart Appointment Scheduling**: AI-powered natural language booking
- **Multi-turn Conversations**: Context-aware chat sessions
- **Doctor Analytics**: AI-generated reports and summaries
- **Email & SMS Notifications**: Automated confirmations and alerts
- **Google Calendar Integration**: Real-time availability checking
- **React Frontend**: Modern, responsive user interface

### 🤖 AI Capabilities
- Natural language appointment booking via Gemini LLM
- Intelligent doctor report generation
- Context-aware conversation handling
- Automated scheduling conflict resolution

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+ (for React frontend)
- PostgreSQL database
- Gmail account (for SMTP)
- Gemini API key
- Twilio account (for SMS, optional)

### Environment Setup

Create a `.env` file in the root directory:

```env
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=appointments
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# SMTP Configuration (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key

# Twilio Configuration (Optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Google Calendar API (Optional)
GOOGLE_CALENDAR_CREDENTIALS={"token": "your_token", "refresh_token": "your_refresh_token", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "your_client_id", "client_secret": "your_client_secret", "scopes": ["https://www.googleapis.com/auth/calendar"]}
```

### Installation & Running

1. **Install Backend Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

3. **Start the Backend Server**:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 5000 --reload
   ```

4. **Start the Frontend (in another terminal)**:
   ```bash
   cd frontend
   npm start
   ```

5. **Access the Application**:
   - Backend API: `http://localhost:5000`
   - Frontend: `http://localhost:3000`
   - API Docs: `http://localhost:5000/docs`

## 📚 Complete API Documentation

### Base URL
```
http://localhost:5000
```

---

## 🔐 Authentication Endpoints

### POST `/register`
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

**Response (200)**:
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

**Error (400)**:
```json
{
  "detail": "User already exists"
}
```

---

### POST `/login`
Authenticate user and get JWT token

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "patient"
  }
}
```

**Error (401)**:
```json
{
  "detail": "Invalid credentials"
}
```

---

### GET `/current-user`
Get current authenticated user info

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response (200)**:
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "user@example.com",
  "role": "patient",
  "phone": "+1234567890"
}
```

---

### GET `/users`
Get all users (for admin purposes)

**Response (200)**:
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "patient"
  }
]
```

---

## 👨‍⚕️ Doctor Management

### GET `/doctors`
Get all doctors

**Response (200)**:
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

---

### POST `/doctors`
Add a new doctor

**Query Parameters**:
- `name` (string): Doctor's name
- `specialization` (string): Medical specialization
- `email` (string): Doctor's email

**Example**:
```
POST /doctors?name=Dr.%20Smith&specialization=Cardiology&email=dr.smith@hospital.com
```

**Response (200)**:
```json
{
  "message": "Doctor Dr. Smith added successfully"
}
```

---

### POST `/doctors/{doctor_id}/reports`
Generate doctor reports

**Path Parameters**:
- `doctor_id` (int): Doctor's ID

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
- `symptom_analysis`: Filter by symptoms (use date_filter for symptom keyword)

**Response (200)**:
```json
{
  "doctor": "Dr. Smith",
  "report": {
    "summary": "Today you have 5 appointments scheduled...",
    "details": [...]
  }
}
```

---

## 📅 Appointment Management

### GET `/appointments`
Get appointments with optional filters

**Query Parameters** (all optional):
- `user_id` (int): Filter by patient ID
- `doctor_id` (int): Filter by doctor ID

**Response (200)**:
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

---

### POST `/appointments/book`
Book an appointment

**Query Parameters**:
- `user_id` (int): Patient's user ID

**Request Body**:
```json
{
  "doctor_name": "Dr. Smith",
  "date": "2024-01-15",
  "time_slot": "10:00",
  "symptoms": "headache"
}
```

**Response (200)**:
```json
{
  "message": "Appointment booked for John Doe with Dr. Smith at 10:00 on 2024-01-15. Confirmation email sent successfully.",
  "status": "success"
}
```

**Error (400)**:
```json
{
  "detail": "Doctor not available at this time"
}
```

---

### GET `/availability/{doctor_name}/{date}`
Check doctor availability

**Path Parameters**:
- `doctor_name` (string): Doctor's name (URL encoded)
- `date` (string): Date in YYYY-MM-DD format

**Example**:
```
GET /availability/Dr.%20Smith/2024-01-15
```

**Response (200)**:
```json
{
  "doctor": "Dr. Smith",
  "date": "2024-01-15",
  "available_slots": ["09:00", "09:30", "10:00", "14:00", "14:30"]
}
```

---

## 💬 AI Chat Interface

### POST `/chat`
Natural language interface powered by Gemini LLM

**Query Parameters**:
- `user_id` (int): User ID for context
- `message` (string): Natural language message

**Example**:
```
POST /chat?user_id=1&message=I%20want%20to%20book%20an%20appointment%20with%20Dr.%20Smith%20tomorrow%20at%202%20PM
```

**Example Messages**:
- "I want to book an appointment with Dr. Smith tomorrow at 2 PM"
- "Check Dr. Johnson's availability for Friday"
- "How many patients did I see yesterday?" (for doctors)
- "Cancel my appointment with Dr. Smith"
- "Reschedule my appointment to next week"

**Response (200)**:
```json
{
  "response": "I'll help you book an appointment with Dr. Smith. Let me check availability for tomorrow at 2 PM...",
  "action_taken": "checked_availability",
  "status": "success"
}
```

---

## 🗣️ Session Management

### POST `/session`
Manage chat sessions for conversation continuity

**Query Parameters**:
- `user_id` (int): User ID
- `action` (string): "create", "update", or "get"
- `context_data` (string, optional): JSON string

**Example**:
```
POST /session?user_id=1&action=create&context_data={"last_inquiry":"appointment_booking"}
```

**Response (200)**:
```json
{
  "result": "Session created successfully"
}
```

---

### GET `/session/{user_id}`
Get chat session context

**Path Parameters**:
- `user_id` (int): User ID

**Response (200)**:
```json
{
  "user_id": 1,
  "context": {
    "last_inquiry": "appointment_booking",
    "preferred_doctor": "Dr. Smith",
    "last_interaction": "2024-01-15T10:30:00Z"
  }
}
```

---

## 🏠 System Endpoints

### GET `/`
Application homepage with feature overview

**Response (200)**:
```html
<h1>🏥 Smart Doctor Appointment System</h1>
<h2>🧠 Agentic AI with MCP Integration</h2>
<!-- Feature list and links -->
```

---

### GET `/status`
System health and configuration status

**Response (200)**:
```json
{
  "status": "running",
  "version": "1.0.0",
  "features": {
    "authentication": "JWT-based (Patient/Doctor)",
    "appointments": "Smart scheduling with AI",
    "reports": "AI-powered analytics",
    "integrations": ["Google Calendar", "SMTP Email", "PostgreSQL", "Gemini LLM"],
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
}
```

---

### GET `/dashboard`
Web dashboard for system overview

**Response**: HTML dashboard page

---

## 🎯 Usage Examples

### Example 1: Complete Patient Workflow

1. **Register as Patient**:
```bash
curl -X POST "http://localhost:5000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "name": "John Doe",
    "password": "password123",
    "role": "patient",
    "phone": "+1234567890"
  }'
```

2. **Login and Get Token**:
```bash
curl -X POST "http://localhost:5000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "password123"
  }'
```

3. **Book Appointment via AI Chat**:
```bash
curl -X POST "http://localhost:5000/chat?user_id=1&message=I%20want%20to%20book%20an%20appointment%20with%20Dr.%20Smith%20tomorrow%20at%202%20PM"
```

### Example 2: Doctor Report Workflow

1. **Register as Doctor**:
```bash
curl -X POST "http://localhost:5000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "name": "Dr. Smith",
    "password": "password123",
    "role": "doctor",
    "specialization": "Cardiology"
  }'
```

2. **Get Daily Report via AI**:
```bash
curl -X POST "http://localhost:5000/chat?user_id=2&message=How%20many%20patients%20do%20I%20have%20today?"
```

---

## 🔧 Technical Architecture

### Backend Stack
- **FastAPI**: Modern web framework with automatic API documentation
- **SQLModel**: Type-safe database operations with Pydantic integration
- **PostgreSQL**: Robust relational database
- **JWT**: Secure token-based authentication
- **Gemini LLM**: Google's AI for natural language processing
- **MCP (Model Context Protocol)**: Tool exposure for AI agents

### Frontend Stack
- **React**: Modern UI library
- **TypeScript**: Type-safe JavaScript
- **Axios**: HTTP client for API calls
- **React Router**: Client-side routing
- **Material-UI**: Component library

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

---

## 🚀 Deployment on Replit

### Backend Deployment
1. Set environment variables in Replit Secrets
2. Configure the run command: `uvicorn server:app --host 0.0.0.0 --port 5000`
3. Deploy using Replit's deployment feature

### Frontend Deployment
1. Build the React app: `npm run build`
2. Serve static files through FastAPI or deploy separately
3. Update API base URL for production

---

## 🎯 Demo Scenarios

### Scenario 1: Patient Natural Language Booking
```
Patient: "I want to book an appointment with Dr. Ahuja tomorrow morning"
System: 
1. ✅ Parses natural language using Gemini LLM
2. ✅ Checks Dr. Ahuja's availability via MCP tools
3. ✅ Shows available morning slots (9:00 AM, 9:30 AM, 10:00 AM)
4. ✅ Patient selects preferred time
5. ✅ Books appointment in database
6. ✅ Sends email confirmation
7. ✅ Updates Google Calendar (if configured)
```

### Scenario 2: Multi-turn Conversation
```
Patient: "Check Dr. Smith's availability for Friday afternoon"
System: "Available slots: 2:00 PM, 2:30 PM, 3:00 PM, 4:00 PM"

Patient: "Book the 3 PM slot"
System: ✅ Uses conversation context → Books 3:00 PM appointment with Dr. Smith for Friday
```

### Scenario 3: Doctor Analytics
```
Doctor: "How many patients visited yesterday?"
System:
1. ✅ Queries database for yesterday's completed appointments
2. ✅ Generates AI-powered summary using Gemini
3. ✅ Sends SMS notification to doctor with summary
```

---

## ✅ Requirements Implementation Status

### ✅ Fully Implemented
- **✅ Role-based JWT Authentication**: Secure patient/doctor login
- **✅ Natural Language Processing**: Gemini LLM integration
- **✅ MCP Tool Integration**: All required tools exposed
- **✅ Multi-turn Conversations**: Context-aware sessions
- **✅ Doctor Reports**: Multiple AI-powered report types
- **✅ Email Notifications**: SMTP integration for confirmations
- **✅ Database Integration**: PostgreSQL with full schema
- **✅ API Documentation**: Comprehensive endpoint documentation
- **✅ Error Handling**: Proper HTTP status codes and messages
- **✅ React Frontend**: Modern, responsive user interface

### 🚧 Optional Enhancements
- **📅 Google Calendar Integration**: Available but requires setup
- **📱 SMS Notifications**: Twilio integration available
- **🔐 Advanced Security**: Rate limiting, input validation
- **📊 Advanced Analytics**: More detailed reporting features

---

**🚀 A complete agentic AI solution for healthcare appointment management with modern React frontend!**
