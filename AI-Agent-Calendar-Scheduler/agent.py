
# AI Calendar Scheduling Agent
# Author: Divyank Malik
# Date: December 2025


import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random


class MeetingStatus(Enum):
    """Enum for meeting status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass
class CalendarEvent:
    """Represents a calendar event"""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    status: str
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "attendees": self.attendees,
            "status": self.status
        }


@dataclass
class MeetingRequest:
    """Represents a meeting request from a user"""
    requester_name: str
    requester_email: str
    purpose: str
    duration_minutes: int
    preferred_dates: Optional[List[datetime]] = None


class CalendarDatabase:
    """Simulates a calendar database with dummy data"""
    
    def __init__(self):
        self.events: List[CalendarEvent] = []
        self._generate_dummy_events()
    
    def _generate_dummy_events(self):
        """Generate random calendar events for testing"""
        base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Generate events for next 14 days
        event_titles = [
            "Team Standup",
            "Client Meeting",
            "Code Review",
            "Project Planning",
            "1-on-1 with Manager",
            "Design Review",
            "Architecture Discussion",
            "Sprint Retrospective",
            "Product Demo",
            "Training Session"
        ]
        
        event_id = 1
        for day_offset in range(14):
            current_date = base_date + timedelta(days=day_offset)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
            
            # Generate 2-4 random meetings per day
            num_meetings = random.randint(2, 4)
            used_hours = set()
            
            for _ in range(num_meetings):
                # Random hour between 9 AM and 5 PM
                hour = random.randint(9, 16)
                while hour in used_hours:
                    hour = random.randint(9, 16)
                used_hours.add(hour)
                
                start_time = current_date.replace(hour=hour)
                duration = random.choice([30, 60, 90])
                end_time = start_time + timedelta(minutes=duration)
                
                event = CalendarEvent(
                    id=f"evt_{event_id}",
                    title=random.choice(event_titles),
                    start_time=start_time,
                    end_time=end_time,
                    attendees=[f"user{random.randint(1, 5)}@company.com"],
                    status="confirmed"
                )
                self.events.append(event)
                event_id += 1
    
    def get_events_in_range(self, start: datetime, end: datetime) -> List[CalendarEvent]:
        """Get all events within a time range"""
        return [
            event for event in self.events
            if event.start_time >= start and event.end_time <= end
        ]
    
    def add_event(self, event: CalendarEvent):
        """Add a new event to the calendar"""
        self.events.append(event)
        print(f"✓ Event added: {event.title} on {event.start_time.strftime('%Y-%m-%d %H:%M')}")
    
    def is_time_slot_available(self, start_time: datetime, end_time: datetime) -> bool:
        """Check if a time slot is available"""
        for event in self.events:
            # Check for overlap
            if (start_time < event.end_time and end_time > event.start_time):
                return False
        return True


class NaturalLanguageProcessor:
    """Processes natural language meeting requests"""
    
    @staticmethod
    def extract_meeting_info(text: str) -> Dict:
        """Extract meeting information from natural language text"""
        text_lower = text.lower()
        
        # Extract duration
        duration = 60  # default
        duration_patterns = [
            (r'(\d+)\s*(?:minute|min)', 1),
            (r'(\d+)\s*(?:hour|hr)', 60),
            (r'half\s*hour', 30),
            (r'an\s*hour', 60)
        ]
        
        for pattern, multiplier in duration_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if isinstance(multiplier, int) and multiplier == 30:
                    duration = 30
                elif isinstance(multiplier, int) and multiplier == 60:
                    duration = 60
                else:
                    duration = int(match.group(1)) * multiplier
                break
        
        # Extract purpose/topic
        purpose_keywords = ['discuss', 'about', 'regarding', 'talk about', 'meeting about']
        purpose = "General Meeting"
        for keyword in purpose_keywords:
            if keyword in text_lower:
                idx = text_lower.find(keyword)
                purpose = text[idx:idx+50].strip()
                break
        
        return {
            'duration': duration,
            'purpose': purpose
        }


class SchedulingAgent:
    """Main AI agent for scheduling meetings"""
    
    def __init__(self):
        self.calendar = CalendarDatabase()
        self.nlp = NaturalLanguageProcessor()
        self.pending_requests: Dict[str, Tuple[MeetingRequest, List[datetime]]] = {}
        
    def process_meeting_request(self, requester_name: str, requester_email: str, 
                                message: str) -> Dict:
        """
        Process a meeting request and suggest available time slots
        
        Args:
            requester_name: Name of the person requesting the meeting
            requester_email: Email of the requester
            message: Natural language meeting request
            
        Returns:
            Dictionary with suggested time slots
        """
        print(f"\n{'='*60}")
        print(f"Processing meeting request from {requester_name}")
        print(f"Message: {message}")
        print(f"{'='*60}")
        
        # Extract meeting details using NLP
        meeting_info = self.nlp.extract_meeting_info(message)
        duration = meeting_info['duration']
        purpose = meeting_info['purpose']
        
        print(f"\n📋 Extracted Information:")
        print(f"   Duration: {duration} minutes")
        print(f"   Purpose: {purpose}")
        
        # Find available slots
        available_slots = self._find_available_slots(duration, num_slots=5)
        
        if not available_slots:
            return {
                "status": "error",
                "message": "No available slots found in the next 14 days"
            }
        
        # Create meeting request
        request = MeetingRequest(
            requester_name=requester_name,
            requester_email=requester_email,
            purpose=purpose,
            duration_minutes=duration
        )
        
        # Store pending request
        request_id = f"req_{len(self.pending_requests) + 1}"
        self.pending_requests[request_id] = (request, available_slots)
        
        print(f"\n💡 Available Time Slots:")
        for i, slot in enumerate(available_slots, 1):
            print(f"   {i}. {slot.strftime('%A, %B %d, %Y at %I:%M %p')}")
        
        return {
            "status": "success",
            "request_id": request_id,
            "available_slots": [slot.isoformat() for slot in available_slots],
            "message": f"Found {len(available_slots)} available time slots"
        }
    
    def _find_available_slots(self, duration_minutes: int, num_slots: int = 5) -> List[datetime]:
        """Find available time slots for a meeting"""
        available_slots = []
        current_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Search for next 14 days
        for day_offset in range(14):
            if len(available_slots) >= num_slots:
                break
                
            check_date = current_date + timedelta(days=day_offset)
            
            # Skip weekends
            if check_date.weekday() >= 5:
                continue
            
            # Check each hour from 9 AM to 5 PM
            for hour in range(9, 17):
                if len(available_slots) >= num_slots:
                    break
                    
                start_time = check_date.replace(hour=hour)
                end_time = start_time + timedelta(minutes=duration_minutes)
                
                # Don't suggest slots after 5 PM
                if end_time.hour >= 17:
                    continue
                
                if self.calendar.is_time_slot_available(start_time, end_time):
                    available_slots.append(start_time)
        
        return available_slots
    
    def confirm_meeting(self, request_id: str, slot_index: int) -> Dict:
        """
        Confirm a meeting for a specific time slot
        
        Args:
            request_id: ID of the pending request
            slot_index: Index of the chosen time slot (0-based)
            
        Returns:
            Dictionary with confirmation status
        """
        if request_id not in self.pending_requests:
            return {
                "status": "error",
                "message": "Request ID not found"
            }
        
        request, available_slots = self.pending_requests[request_id]
        
        if slot_index < 0 or slot_index >= len(available_slots):
            return {
                "status": "error",
                "message": "Invalid slot index"
            }
        
        chosen_slot = available_slots[slot_index]
        end_time = chosen_slot + timedelta(minutes=request.duration_minutes)
        
        # Create calendar event
        event = CalendarEvent(
            id=f"evt_{len(self.calendar.events) + 1}",
            title=f"Meeting with {request.requester_name}",
            start_time=chosen_slot,
            end_time=end_time,
            attendees=[request.requester_email, "owner@company.com"],
            status=MeetingStatus.CONFIRMED.value
        )
        
        # Add to calendar
        self.calendar.add_event(event)
        
        # Remove from pending
        del self.pending_requests[request_id]
        
        print(f"\n✅ Meeting Confirmed!")
        print(f"   With: {request.requester_name}")
        print(f"   Time: {chosen_slot.strftime('%A, %B %d, %Y at %I:%M %p')}")
        print(f"   Duration: {request.duration_minutes} minutes")
        
        return {
            "status": "success",
            "message": "Meeting confirmed",
            "event": event.to_dict()
        }
    
    def view_calendar(self, days: int = 7):
        """Display calendar events for the next N days"""
        start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=days)
        
        events = self.calendar.get_events_in_range(start, end)
        events.sort(key=lambda x: x.start_time)
        
        print(f"\n📅 Calendar for next {days} days:")
        print(f"{'='*60}")
        
        current_date = None
        for event in events:
            event_date = event.start_time.date()
            if event_date != current_date:
                current_date = event_date
                print(f"\n{event.start_time.strftime('%A, %B %d, %Y')}")
                print("-" * 60)
            
            print(f"  {event.start_time.strftime('%I:%M %p')} - {event.end_time.strftime('%I:%M %p')} | {event.title}")


def main():
    """Demo of the calendar agent"""
    print("🤖 AI Calendar Scheduling Agent")
    print("=" * 60)
    
    # Initialize agent
    agent = SchedulingAgent()
    
    # Display current calendar
    agent.view_calendar(days=7)
    
    # Simulate meeting requests
    print("\n\n" + "="*60)
    print("SIMULATING MEETING REQUESTS")
    print("="*60)
    
    # Request 1
    result1 = agent.process_meeting_request(
        requester_name="John Smith",
        requester_email="john.smith@client.com",
        message="Hi, I'd like to discuss the Q1 project proposal. Can we meet for an hour?"
    )
    
    if result1['status'] == 'success':
        # Accept first slot
        agent.confirm_meeting(result1['request_id'], 0)
    
    # Request 2
    result2 = agent.process_meeting_request(
        requester_name="Sarah Johnson",
        requester_email="sarah.j@partner.com",
        message="Need to talk about the API integration. 30 minutes should be enough."
    )
    
    if result2['status'] == 'success':
        # Accept second slot
        agent.confirm_meeting(result2['request_id'], 1)
    
    # Request 3
    result3 = agent.process_meeting_request(
        requester_name="Mike Chen",
        requester_email="mike.chen@startup.io",
        message="Can we have a quick 45-minute meeting regarding the partnership opportunity?"
    )
    
    if result3['status'] == 'success':
        # Accept third slot
        agent.confirm_meeting(result3['request_id'], 2)
    
    # Display updated calendar
    print("\n\n")
    agent.view_calendar(days=7)
    
    # Export calendar to JSON
    print("\n\n" + "="*60)
    print("EXPORTING CALENDAR DATA")
    print("="*60)
    
    calendar_data = {
        "events": [event.to_dict() for event in agent.calendar.events],
        "total_events": len(agent.calendar.events)
    }
    
    with open("calendar_export.json", "w") as f:
        json.dump(calendar_data, f, indent=2)
    
    print("✓ Calendar exported to calendar_export.json")


if __name__ == "__main__":
    main()