"""
# AI Calendar Scheduling Agent

An intelligent Python-based agent that automates meeting scheduling by analyzing calendar availability and managing meeting requests through natural language processing.

## 🎯 Features

- **Natural Language Processing**: Extracts meeting details from plain English requests
- **Automatic Availability Checking**: Scans calendar for free time slots
- **Smart Scheduling**: Suggests multiple available meeting times
- **Conflict Prevention**: Ensures no double-booking
- **Calendar Management**: Add, view, and export calendar events
- **Dummy Data Generation**: Includes realistic test data for demonstration

## 🏗️ System Architecture

```
┌─────────────────┐
│  User Request   │
│ (Natural Lang)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   NLP Processor         │
│ - Extract duration      │
│ - Extract purpose       │
│ - Parse preferences     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Scheduling Agent       │
│ - Find available slots  │
│ - Generate suggestions  │
│ - Manage requests       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Calendar Database      │
│ - Store events          │
│ - Check availability    │
│ - Prevent conflicts     │
└─────────────────────────┘
```

## 📋 Components

### 1. **CalendarEvent**
- Data structure for calendar events
- Stores: ID, title, times, attendees, status

### 2. **MeetingRequest**
- Represents incoming meeting requests
- Contains requester info and preferences

### 3. **CalendarDatabase**
- Manages all calendar events
- Generates dummy data for testing
- Handles availability checks

### 4. **NaturalLanguageProcessor**
- Parses meeting requests
- Extracts duration and purpose
- Handles various formats

### 5. **SchedulingAgent**
- Main orchestrator
- Processes requests
- Confirms meetings
- Manages workflow

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-calendar-agent.git
cd ai-calendar-agent
```

2. Run the agent:
```bash
python agent.py
```

### Usage

```python
from agent import SchedulingAgent

# Initialize the agent
agent = SchedulingAgent()

# Process a meeting request
result = agent.process_meeting_request(
    requester_name="John Doe",
    requester_email="john@example.com",
    message="Let's meet for 30 minutes to discuss the project"
)

# Confirm a meeting (choose slot 0)
if result['status'] == 'success':
    agent.confirm_meeting(result['request_id'], slot_index=0)

# View calendar
agent.view_calendar(days=7)
```

## 📊 Example Output

```
🤖 AI Calendar Scheduling Agent
============================================================

📅 Calendar for next 7 days:
============================================================

Monday, December 30, 2024
------------------------------------------------------------
  09:00 AM - 10:00 AM | Team Standup
  02:00 PM - 03:30 PM | Client Meeting

Processing meeting request from John Smith
Message: Hi, I'd like to discuss the Q1 project proposal. Can we meet for an hour?

📋 Extracted Information:
   Duration: 60 minutes
   Purpose: discuss the Q1 project proposal

💡 Available Time Slots:
   1. Monday, December 30, 2024 at 10:00 AM
   2. Monday, December 30, 2024 at 11:00 AM
   3. Tuesday, December 31, 2024 at 09:00 AM
   ...

✅ Meeting Confirmed!
   With: John Smith
   Time: Monday, December 30, 2024 at 10:00 AM
   Duration: 60 minutes
```

## 🧪 Testing

The agent includes automatic dummy data generation with:
- 2-4 meetings per weekday
- Various meeting types (standups, reviews, 1-on-1s)
- Realistic time slots (9 AM - 5 PM)
- 14 days of calendar data

## 📁 Project Structure

```
ai-calendar-agent/
├── agent.py              # Main agent implementation
├── config.py             # Configuration settings
├── requirements.txt      # Dependencies (none required)
├── README.md            # This file
└── tests/
    └── test_agent.py    # Unit tests (optional)
```

## 🔧 Configuration

Edit `config.py` to customize:
- Working hours (default: 9 AM - 5 PM)
- Search range (default: 14 days)
- Number of suggestions (default: 5)
- Default meeting duration (default: 60 min)

## 📈 Future Enhancements

- [ ] Email integration (SMTP/IMAP)
- [ ] Google Calendar API integration
- [ ] Time zone support
- [ ] Recurring meetings
- [ ] Meeting cancellation
- [ ] Reminder notifications
- [ ] Multi-participant scheduling
- [ ] AI-powered conflict resolution

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👤 Author

Divyank Malik

## 🙏 Acknowledgments

- Built with Python's standard library
- No external dependencies required
- Designed for simplicity and extensibility

⭐ Star this repo if you find it helpful!
"""
