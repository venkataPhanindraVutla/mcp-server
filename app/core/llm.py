
import google.generativeai as genai
import json
import os
from typing import Dict, Any, Optional
from app.core.database import get_session
from app.models import User
from sqlmodel import select

class LLMService:
    def __init__(self):
        """Initialize Gemini LLM service"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def process_chat_message(self, user_id: int, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a chat message with context and available tools"""
        try:
            # Get user context
            session = get_session()
            user = session.exec(select(User).where(User.id == user_id)).first()
            if not user:
                return {"error": "User not found"}
            
            # Load conversation context
            from app.tools.tools import manage_session
            stored_context = await manage_session(user_id, "get")
            context_data = json.loads(stored_context) if stored_context else {}
            
            # Build system prompt with available tools and context
            system_prompt = self._build_system_prompt(user, context_data)
            
            # Generate response
            full_prompt = f"{system_prompt}\n\nUser message: {message}"
            response = self.model.generate_content(full_prompt)
            ai_response = response.text
            
            # Process potential tool calls
            tool_result = await self._process_tool_calls(user_id, user, message, ai_response)
            if tool_result:
                ai_response = tool_result
            
            # Update conversation context
            context_data["last_message"] = message
            context_data["last_response"] = ai_response
            context_data["conversation_history"] = context_data.get("conversation_history", [])
            context_data["conversation_history"].append({
                "user": message,
                "assistant": ai_response,
                "timestamp": str(json.loads(json.dumps(context_data, default=str)))
            })
            
            # Keep only last 10 exchanges
            if len(context_data["conversation_history"]) > 10:
                context_data["conversation_history"] = context_data["conversation_history"][-10:]
            
            await manage_session(user_id, "update", json.dumps(context_data))
            
            return {
                "response": ai_response,
                "user_id": user_id,
                "user_role": user.role,
                "context_updated": True
            }
            
        except Exception as e:
            return {
                "error": f"LLM processing failed: {str(e)}", 
                "fallback_response": "I'm sorry, I couldn't process your request. Please try again or use specific commands."
            }
    
    def _build_system_prompt(self, user: User, context_data: Dict[str, Any]) -> str:
        """Build system prompt with user context and available tools"""
        return f"""
        You are an AI assistant for a smart doctor appointment system.
        Current user: {user.name} (Role: {user.role}, Email: {user.email})
        
        Available MCP tools you can use:
        - availability_tool(doctor_name, date) - Check doctor availability
        - booking_tool(user_id, time_slot, date, doctor_name, symptoms) - Book appointments (patients only)
        - doctor_reports_tool(doctor_id, report_type, date_filter) - Generate reports (doctors only)
        - send_doctor_notification(doctor_email, subject, message, notification_type) - Send notifications
        
        Context from previous conversation: {context_data}
        
        Instructions:
        1. Parse the user's message and determine the appropriate action
        2. For patients: Help with appointment booking and checking availability
        3. For doctors: Help with reports, schedules, and patient summaries
        4. Maintain conversation context and refer to previous exchanges
        5. Be helpful, professional, and accurate
        6. If you need to use tools, clearly indicate the action you're taking
        
        Response guidelines:
        - For availability checks: Extract doctor name and date, then use availability_tool
        - For bookings: Extract all required details (doctor, date, time, symptoms) and use booking_tool
        - For doctor reports: Use doctor_reports_tool with appropriate filters
        - Always confirm actions before executing them
        """
    
    async def _process_tool_calls(self, user_id: int, user: User, message: str, ai_response: str) -> Optional[str]:
        """Process potential tool calls based on message content and AI response"""
        message_lower = message.lower()
        
        try:
            # Import tools
            from app.tools.tools import availability_tool, booking_tool, doctor_reports_tool
            
            # Check for availability requests
            if any(word in message_lower for word in ["availability", "available", "check", "free"]):
                doctor_name, date = self._extract_doctor_and_date(message)
                if doctor_name and date:
                    slots = await availability_tool(doctor_name, date)
                    return f"Available slots for {doctor_name} on {date}: {', '.join(slots) if slots else 'No slots available'}"
            
            # Check for booking requests (patients only)
            elif "book" in message_lower and user.role == "patient":
                booking_details = self._extract_booking_details(message)
                if self._has_complete_booking_info(booking_details):
                    result = await booking_tool(
                        user_id, 
                        booking_details["time_slot"],
                        booking_details["date"], 
                        booking_details["doctor_name"],
                        booking_details.get("symptoms", "")
                    )
                    return result
                else:
                    return "I can help you book an appointment. Please provide: doctor name, date, time, and any symptoms you'd like to mention."
            
            # Check for report requests (doctors only)
            elif any(word in message_lower for word in ["report", "patients", "appointments", "summary"]) and user.role == "doctor":
                # Get doctor ID from user
                session = get_session()
                from app.models import Doctor
                doctor = session.exec(select(Doctor).where(Doctor.user_id == user_id)).first()
                if doctor:
                    report_type = self._extract_report_type(message)
                    date_filter = self._extract_date_filter(message)
                    report = await doctor_reports_tool(doctor.id, report_type, date_filter)
                    return report
                else:
                    return "Doctor profile not found. Please contact support."
            
            return None
            
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    def _extract_doctor_and_date(self, message: str) -> tuple:
        """Extract doctor name and date from message"""
        import re
        from datetime import datetime, timedelta
        
        # Extract doctor name
        doctor_match = re.search(r'dr\.?\s+(\w+)', message.lower())
        doctor_name = f"Dr. {doctor_match.group(1).title()}" if doctor_match else "Dr. Smith"
        
        # Extract date
        today = datetime.now()
        if "tomorrow" in message.lower():
            date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "today" in message.lower():
            date = today.strftime("%Y-%m-%d")
        else:
            # Try to find a date pattern
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', message)
            date = date_match.group(1) if date_match else today.strftime("%Y-%m-%d")
        
        return doctor_name, date
    
    def _extract_booking_details(self, message: str) -> Dict[str, str]:
        """Extract booking details from message"""
        import re
        from datetime import datetime, timedelta
        
        details = {}
        
        # Extract doctor name
        doctor_match = re.search(r'dr\.?\s+(\w+)', message.lower())
        if doctor_match:
            details["doctor_name"] = f"Dr. {doctor_match.group(1).title()}"
        
        # Extract time
        time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)', message.lower())
        if time_match:
            hour = int(time_match.group(1))
            minute = time_match.group(2) or "00"
            period = time_match.group(3)
            if period == "pm" and hour != 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0
            details["time_slot"] = f"{hour:02d}:{minute}"
        
        # Extract date
        today = datetime.now()
        if "tomorrow" in message.lower():
            details["date"] = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "today" in message.lower():
            details["date"] = today.strftime("%Y-%m-%d")
        else:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', message)
            if date_match:
                details["date"] = date_match.group(1)
        
        # Extract symptoms
        symptoms_keywords = ["symptoms", "problem", "issue", "pain", "fever", "headache"]
        for keyword in symptoms_keywords:
            if keyword in message.lower():
                # Simple extraction - could be improved
                details["symptoms"] = f"Patient mentioned: {keyword}"
                break
        
        return details
    
    def _has_complete_booking_info(self, details: Dict[str, str]) -> bool:
        """Check if booking details are complete"""
        required = ["doctor_name", "date", "time_slot"]
        return all(key in details for key in required)
    
    def _extract_report_type(self, message: str) -> str:
        """Extract report type from message"""
        if "yesterday" in message.lower():
            return "yesterday_patients"
        elif "today" in message.lower():
            return "today_appointments"
        elif "tomorrow" in message.lower():
            return "tomorrow_appointments"
        elif "fever" in message.lower():
            return "fever_patients"
        else:
            return "general_summary"
    
    def _extract_date_filter(self, message: str) -> Optional[str]:
        """Extract date filter from message"""
        import re
        from datetime import datetime, timedelta
        
        if "yesterday" in message.lower():
            return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        elif "today" in message.lower():
            return datetime.now().strftime("%Y-%m-%d")
        elif "tomorrow" in message.lower():
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Try to find a date pattern
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', message)
        return date_match.group(1) if date_match else None

# Global LLM service instance
llm_service = LLMService()
