"""
Unit Tests for AI Calendar Scheduling Agent
============================================

Run tests with:
    python -m pytest test_agent.py -v
    
Or without pytest:
    python test_agent.py

Coverage:
    python -m pytest test_agent.py --cov=agent --cov-report=html
"""

import unittest
import sys
from datetime import datetime, timedelta
from io import StringIO

# Import the agent module
# If agent.py is in parent directory, adjust import
try:
    from agent import (
        CalendarEvent, 
        MeetingRequest, 
        CalendarDatabase,
        NaturalLanguageProcessor,
        SchedulingAgent,
        MeetingStatus
    )
except ImportError:
    # Try importing from parent directory
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agent import (
        CalendarEvent, 
        MeetingRequest, 
        CalendarDatabase,
        NaturalLanguageProcessor,
        SchedulingAgent,
        MeetingStatus
    )


class TestCalendarEvent(unittest.TestCase):
    """Test CalendarEvent data structure"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_time = datetime(2024, 12, 30, 9, 0)
        self.event = CalendarEvent(
            id="test_1",
            title="Test Meeting",
            start_time=self.test_time,
            end_time=self.test_time + timedelta(hours=1),
            attendees=["user1@test.com", "user2@test.com"],
            status="confirmed"
        )
    
    def test_event_creation(self):
        """Test creating a calendar event"""
        self.assertEqual(self.event.id, "test_1")
        self.assertEqual(self.event.title, "Test Meeting")
        self.assertEqual(len(self.event.attendees), 2)
    
    def test_event_to_dict(self):
        """Test converting event to dictionary"""
        event_dict = self.event.to_dict()
        
        self.assertIsInstance(event_dict, dict)
        self.assertEqual(event_dict['id'], "test_1")
        self.assertEqual(event_dict['title'], "Test Meeting")
        self.assertIn('start_time', event_dict)
        self.assertIn('end_time', event_dict)
        
    def test_event_time_duration(self):
        """Test event duration calculation"""
        duration = self.event.end_time - self.event.start_time
        self.assertEqual(duration.total_seconds(), 3600)  # 1 hour


class TestMeetingRequest(unittest.TestCase):
    """Test MeetingRequest data structure"""
    
    def test_request_creation(self):
        """Test creating a meeting request"""
        request = MeetingRequest(
            requester_name="John Doe",
            requester_email="john@test.com",
            purpose="Project Discussion",
            duration_minutes=60
        )
        
        self.assertEqual(request.requester_name, "John Doe")
        self.assertEqual(request.duration_minutes, 60)
        self.assertIsNone(request.preferred_dates)
    
    def test_request_with_preferences(self):
        """Test request with preferred dates"""
        preferred = [datetime(2024, 12, 30, 10, 0)]
        request = MeetingRequest(
            requester_name="Jane Smith",
            requester_email="jane@test.com",
            purpose="Code Review",
            duration_minutes=30,
            preferred_dates=preferred
        )
        
        self.assertEqual(len(request.preferred_dates), 1)
        self.assertIsInstance(request.preferred_dates[0], datetime)


class TestCalendarDatabase(unittest.TestCase):
    """Test CalendarDatabase functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.db = CalendarDatabase()
    
    def test_database_initialization(self):
        """Test database initializes with dummy data"""
        self.assertIsInstance(self.db.events, list)
        self.assertGreater(len(self.db.events), 0)
    
    def test_add_event(self):
        """Test adding an event"""
        initial_count = len(self.db.events)
        
        new_event = CalendarEvent(
            id="test_new",
            title="New Meeting",
            start_time=datetime(2025, 1, 15, 10, 0),
            end_time=datetime(2025, 1, 15, 11, 0),
            attendees=["user@test.com"],
            status="confirmed"
        )
        
        # Suppress print output during test
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        self.db.add_event(new_event)
        
        sys.stdout = old_stdout
        
        self.assertEqual(len(self.db.events), initial_count + 1)
        self.assertIn(new_event, self.db.events)
    
    def test_get_events_in_range(self):
        """Test retrieving events within a date range"""
        start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        
        events = self.db.get_events_in_range(start, end)
        
        self.assertIsInstance(events, list)
        # All returned events should be within range
        for event in events:
            self.assertGreaterEqual(event.start_time, start)
            self.assertLessEqual(event.end_time, end)
    
    def test_is_time_slot_available_empty_calendar(self):
        """Test availability check on empty calendar"""
        # Create empty database
        empty_db = CalendarDatabase()
        empty_db.events = []
        
        start = datetime(2025, 1, 15, 10, 0)
        end = datetime(2025, 1, 15, 11, 0)
        
        self.assertTrue(empty_db.is_time_slot_available(start, end))
    
    def test_is_time_slot_available_with_conflict(self):
        """Test availability check with conflicting event"""
        db = CalendarDatabase()
        db.events = []
        
        # Add an event from 10:00 to 11:00
        existing = CalendarEvent(
            id="existing",
            title="Existing Meeting",
            start_time=datetime(2025, 1, 15, 10, 0),
            end_time=datetime(2025, 1, 15, 11, 0),
            attendees=["user@test.com"],
            status="confirmed"
        )
        db.events.append(existing)
        
        # Test overlapping time slot (10:30 to 11:30)
        start = datetime(2025, 1, 15, 10, 30)
        end = datetime(2025, 1, 15, 11, 30)
        
        self.assertFalse(db.is_time_slot_available(start, end))
    
    def test_is_time_slot_available_no_conflict(self):
        """Test availability check without conflict"""
        db = CalendarDatabase()
        db.events = []
        
        # Add an event from 10:00 to 11:00
        existing = CalendarEvent(
            id="existing",
            title="Existing Meeting",
            start_time=datetime(2025, 1, 15, 10, 0),
            end_time=datetime(2025, 1, 15, 11, 0),
            attendees=["user@test.com"],
            status="confirmed"
        )
        db.events.append(existing)
        
        # Test non-overlapping time slot (11:00 to 12:00)
        start = datetime(2025, 1, 15, 11, 0)
        end = datetime(2025, 1, 15, 12, 0)
        
        self.assertTrue(db.is_time_slot_available(start, end))
    
    def test_conflict_detection_edge_cases(self):
        """Test various edge cases for conflict detection"""
        db = CalendarDatabase()
        db.events = []
        
        # Event from 10:00 to 11:00
        existing = CalendarEvent(
            id="existing",
            title="Existing Meeting",
            start_time=datetime(2025, 1, 15, 10, 0),
            end_time=datetime(2025, 1, 15, 11, 0),
            attendees=["user@test.com"],
            status="confirmed"
        )
        db.events.append(existing)
        
        # Test cases
        test_cases = [
            # (start, end, should_be_available, description)
            (datetime(2025, 1, 15, 9, 0), datetime(2025, 1, 15, 10, 0), True, "Before, touching"),
            (datetime(2025, 1, 15, 9, 0), datetime(2025, 1, 15, 10, 30), False, "Before, overlapping"),
            (datetime(2025, 1, 15, 10, 0), datetime(2025, 1, 15, 11, 0), False, "Exact match"),
            (datetime(2025, 1, 15, 10, 30), datetime(2025, 1, 15, 11, 30), False, "Overlapping end"),
            (datetime(2025, 1, 15, 11, 0), datetime(2025, 1, 15, 12, 0), True, "After, touching"),
            (datetime(2025, 1, 15, 12, 0), datetime(2025, 1, 15, 13, 0), True, "After, separate"),
        ]
        
        for start, end, expected, desc in test_cases:
            result = db.is_time_slot_available(start, end)
            self.assertEqual(result, expected, f"Failed: {desc}")


class TestNaturalLanguageProcessor(unittest.TestCase):
    """Test NLP functionality"""
    
    def setUp(self):
        """Set up NLP processor"""
        self.nlp = NaturalLanguageProcessor()
    
    def test_extract_duration_minutes(self):
        """Test extracting duration in minutes"""
        test_cases = [
            ("Let's meet for 30 minutes", 30),
            ("Can we talk for 45 min?", 45),
            ("15 minutes should be enough", 15),
        ]
        
        for text, expected_duration in test_cases:
            result = self.nlp.extract_meeting_info(text)
            self.assertEqual(result['duration'], expected_duration)
    
    def test_extract_duration_hours(self):
        """Test extracting duration in hours"""
        test_cases = [
            ("Need 1 hour for this", 60),
            ("Let's schedule 2 hours", 120),
            ("an hour should work", 60),
        ]
        
        for text, expected_duration in test_cases:
            result = self.nlp.extract_meeting_info(text)
            self.assertEqual(result['duration'], expected_duration)
    
    def test_extract_duration_special_cases(self):
        """Test special duration phrases"""
        test_cases = [
            ("half hour meeting", 30),
            ("an hour discussion", 60),
        ]
        
        for text, expected_duration in test_cases:
            result = self.nlp.extract_meeting_info(text)
            self.assertEqual(result['duration'], expected_duration)
    
    def test_extract_duration_default(self):
        """Test default duration when not specified"""
        text = "Let's meet to discuss the project"
        result = self.nlp.extract_meeting_info(text)
        self.assertEqual(result['duration'], 60)  # Default is 60 minutes
    
    def test_extract_purpose(self):
        """Test extracting meeting purpose"""
        test_cases = [
            ("Let's discuss the API integration", "discuss"),
            ("Talk about the new features", "about"),
            ("Meeting regarding budget planning", "regarding"),
        ]
        
        for text, keyword in test_cases:
            result = self.nlp.extract_meeting_info(text)
            self.assertIn(keyword, result['purpose'].lower())
    
    def test_extract_purpose_default(self):
        """Test default purpose when keywords not found"""
        text = "Let's meet tomorrow"
        result = self.nlp.extract_meeting_info(text)
        self.assertEqual(result['purpose'], "General Meeting")


class TestSchedulingAgent(unittest.TestCase):
    """Test SchedulingAgent functionality"""
    
    def setUp(self):
        """Set up scheduling agent"""
        # Suppress print output during tests
        self.old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        self.agent = SchedulingAgent()
    
    def tearDown(self):
        """Restore stdout"""
        sys.stdout = self.old_stdout
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertIsInstance(self.agent.calendar, CalendarDatabase)
        self.assertIsInstance(self.agent.nlp, NaturalLanguageProcessor)
        self.assertIsInstance(self.agent.pending_requests, dict)
        self.assertEqual(len(self.agent.pending_requests), 0)
    
    def test_process_meeting_request_success(self):
        """Test processing a valid meeting request"""
        result = self.agent.process_meeting_request(
            requester_name="Test User",
            requester_email="test@example.com",
            message="Can we meet for 30 minutes to discuss the project?"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('request_id', result)
        self.assertIn('available_slots', result)
        self.assertGreater(len(result['available_slots']), 0)
    
    def test_process_meeting_request_creates_pending(self):
        """Test that processing creates a pending request"""
        initial_count = len(self.agent.pending_requests)
        
        result = self.agent.process_meeting_request(
            requester_name="Test User",
            requester_email="test@example.com",
            message="Let's meet for 1 hour"
        )
        
        self.assertEqual(len(self.agent.pending_requests), initial_count + 1)
        self.assertIn(result['request_id'], self.agent.pending_requests)
    
    def test_find_available_slots(self):
        """Test finding available time slots"""
        slots = self.agent._find_available_slots(duration_minutes=60, num_slots=3)
        
        self.assertIsInstance(slots, list)
        self.assertGreater(len(slots), 0)
        
        # All slots should be datetime objects
        for slot in slots:
            self.assertIsInstance(slot, datetime)
    
    def test_find_available_slots_respects_count(self):
        """Test that slot finding respects requested count"""
        num_requested = 5
        slots = self.agent._find_available_slots(duration_minutes=30, num_slots=num_requested)
        
        self.assertLessEqual(len(slots), num_requested)
    
    def test_find_available_slots_working_hours(self):
        """Test that slots are within working hours"""
        slots = self.agent._find_available_slots(duration_minutes=60, num_slots=10)
        
        for slot in slots:
            self.assertGreaterEqual(slot.hour, 9)  # Not before 9 AM
            # Meeting shouldn't end after 5 PM
            end_time = slot + timedelta(minutes=60)
            self.assertLessEqual(end_time.hour, 17)
    
    def test_find_available_slots_skips_weekends(self):
        """Test that slots don't fall on weekends"""
        slots = self.agent._find_available_slots(duration_minutes=60, num_slots=20)
        
        for slot in slots:
            # Monday = 0, Sunday = 6
            self.assertLess(slot.weekday(), 5)  # Not weekend
    
    def test_confirm_meeting_success(self):
        """Test confirming a meeting successfully"""
        # First create a request
        result = self.agent.process_meeting_request(
            requester_name="Test User",
            requester_email="test@example.com",
            message="Let's meet for 30 minutes"
        )
        
        request_id = result['request_id']
        initial_event_count = len(self.agent.calendar.events)
        
        # Confirm the meeting
        confirm_result = self.agent.confirm_meeting(request_id, slot_index=0)
        
        self.assertEqual(confirm_result['status'], 'success')
        self.assertIn('event', confirm_result)
        self.assertEqual(len(self.agent.calendar.events), initial_event_count + 1)
        self.assertNotIn(request_id, self.agent.pending_requests)
    
    def test_confirm_meeting_invalid_request_id(self):
        """Test confirming with invalid request ID"""
        result = self.agent.confirm_meeting("invalid_id", slot_index=0)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Request ID not found', result['message'])
    
    def test_confirm_meeting_invalid_slot_index(self):
        """Test confirming with invalid slot index"""
        # Create a request
        result = self.agent.process_meeting_request(
            requester_name="Test User",
            requester_email="test@example.com",
            message="Let's meet"
        )
        
        request_id = result['request_id']
        
        # Try to confirm with invalid index
        confirm_result = self.agent.confirm_meeting(request_id, slot_index=999)
        
        self.assertEqual(confirm_result['status'], 'error')
        self.assertIn('Invalid slot index', confirm_result['message'])
    
    def test_confirm_meeting_removes_from_pending(self):
        """Test that confirming removes request from pending"""
        result = self.agent.process_meeting_request(
            requester_name="Test User",
            requester_email="test@example.com",
            message="Let's meet"
        )
        
        request_id = result['request_id']
        self.assertIn(request_id, self.agent.pending_requests)
        
        self.agent.confirm_meeting(request_id, slot_index=0)
        
        self.assertNotIn(request_id, self.agent.pending_requests)
    
    def test_view_calendar_no_errors(self):
        """Test viewing calendar doesn't raise errors"""
        try:
            self.agent.view_calendar(days=7)
            # If no exception, test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"view_calendar raised exception: {e}")


class TestIntegrationWorkflow(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        """Set up for integration tests"""
        self.old_stdout = sys.stdout
        sys.stdout = StringIO()
        self.agent = SchedulingAgent()
    
    def tearDown(self):
        """Restore stdout"""
        sys.stdout = self.old_stdout
    
    def test_complete_booking_workflow(self):
        """Test complete workflow from request to confirmation"""
        # Step 1: User requests meeting
        request_result = self.agent.process_meeting_request(
            requester_name="John Smith",
            requester_email="john@example.com",
            message="Can we meet for 30 minutes to discuss the API integration?"
        )
        
        # Verify request was processed
        self.assertEqual(request_result['status'], 'success')
        self.assertGreater(len(request_result['available_slots']), 0)
        
        request_id = request_result['request_id']
        
        # Step 2: User confirms a time slot
        confirm_result = self.agent.confirm_meeting(request_id, slot_index=0)
        
        # Verify confirmation
        self.assertEqual(confirm_result['status'], 'success')
        self.assertEqual(confirm_result['event']['attendees'][0], "john@example.com")
        self.assertIn("John Smith", confirm_result['event']['title'])
        
        # Step 3: Verify meeting is in calendar
        calendar_events = self.agent.calendar.events
        meeting_found = False
        for event in calendar_events:
            if "John Smith" in event.title:
                meeting_found = True
                break
        
        self.assertTrue(meeting_found)
    
    def test_multiple_bookings_no_conflicts(self):
        """Test booking multiple meetings without conflicts"""
        requests = [
            ("Alice", "alice@example.com", "30 minute meeting"),
            ("Bob", "bob@example.com", "1 hour discussion"),
            ("Charlie", "charlie@example.com", "45 min chat"),
        ]
        
        confirmed_events = []
        
        for name, email, message in requests:
            # Request meeting
            result = self.agent.process_meeting_request(name, email, message)
            self.assertEqual(result['status'], 'success')
            
            # Confirm meeting
            confirm = self.agent.confirm_meeting(result['request_id'], slot_index=0)
            self.assertEqual(confirm['status'], 'success')
            
            confirmed_events.append(confirm['event'])
        
        # Verify all meetings are confirmed
        self.assertEqual(len(confirmed_events), 3)
        
        # Verify no time conflicts between confirmed meetings
        for i, event1 in enumerate(confirmed_events):
            for event2 in confirmed_events[i+1:]:
                start1 = datetime.fromisoformat(event1['start_time'])
                end1 = datetime.fromisoformat(event1['end_time'])
                start2 = datetime.fromisoformat(event2['start_time'])
                end2 = datetime.fromisoformat(event2['end_time'])
                
                # Check no overlap
                has_conflict = (start1 < end2 and end1 > start2)
                self.assertFalse(has_conflict, "Found conflicting meetings")
    
    def test_nlp_to_calendar_integration(self):
        """Test that NLP extraction works with calendar booking"""
        # Request with specific duration
        result = self.agent.process_meeting_request(
            requester_name="Test User",
            requester_email="test@example.com",
            message="Need a 45 minute meeting to discuss the database migration"
        )
        
        # Get the pending request
        request_id = result['request_id']
        meeting_request, _ = self.agent.pending_requests[request_id]
        
        # Verify NLP extracted duration correctly
        self.assertEqual(meeting_request.duration_minutes, 45)
        self.assertIn("database", meeting_request.purpose.lower())


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up for edge case tests"""
        self.old_stdout = sys.stdout
        sys.stdout = StringIO()
        self.agent = SchedulingAgent()
    
    def tearDown(self):
        """Restore stdout"""
        sys.stdout = self.old_stdout
    
    def test_very_long_meeting_duration(self):
        """Test handling very long meeting durations"""
        # 4 hour meeting
        slots = self.agent._find_available_slots(duration_minutes=240, num_slots=5)
        
        # Should still find some slots (morning slots)
        self.assertGreater(len(slots), 0)
        
        # All slots should allow meeting to complete by 5 PM
        for slot in slots:
            end_time = slot + timedelta(minutes=240)
            self.assertLessEqual(end_time.hour, 17)
    
    def test_empty_message(self):
        """Test handling empty meeting message"""
        result = self.agent.process_meeting_request(
            requester_name="Test User",
            requester_email="test@example.com",
            message=""
        )
        
        # Should still work with defaults
        self.assertEqual(result['status'], 'success')
    
    def test_message_with_no_keywords(self):
        """Test message without any NLP keywords"""
        result = self.agent.process_meeting_request(
            requester_name="Test User",
            requester_email="test@example.com",
            message="Hi there, when are you free?"
        )
        
        # Should use defaults
        self.assertEqual(result['status'], 'success')
        request_id = result['request_id']
        meeting_request, _ = self.agent.pending_requests[request_id]
        
        self.assertEqual(meeting_request.duration_minutes, 60)  # Default
        self.assertEqual(meeting_request.purpose, "General Meeting")  # Default


def run_tests_with_summary():
    """Run tests and print summary"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCalendarEvent))
    suite.addTests(loader.loadTestsFromTestCase(TestMeetingRequest))
    suite.addTests(loader.loadTestsFromTestCase(TestCalendarDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestNaturalLanguageProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestSchedulingAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result


if __name__ == '__main__':
    # Run with detailed output
    run_tests_with_summary()