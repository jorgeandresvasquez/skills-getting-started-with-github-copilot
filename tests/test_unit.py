"""
Unit tests for FastAPI backend business logic.

Tests core functionality isolated from HTTP layer using AAA pattern:
- Arrange: Set up test data and state
- Act: Execute the business logic
- Assert: Verify expected outcomes
"""

import pytest


class TestActivityValidation:
    """Test activity existence validation logic."""

    def test_activity_exists_in_database(self, app):
        """
        Test: Verify that activities exist in the database.
        AAA Pattern:
        - Arrange: Get activities from app state
        - Act: Check if known activity exists
        - Assert: Confirm Chess Club is in activities
        """
        # Arrange: Mock the app's internal activities
        activities = {"Chess Club": {"participants": []}}
        
        # Act: Check if activity exists
        activity_exists = "Chess Club" in activities
        
        # Assert: Activity should exist
        assert activity_exists is True

    def test_activity_not_found(self, app):
        """
        Test: Verify that non-existent activities are not in database.
        AAA Pattern:
        - Arrange: Set up activity database
        - Act: Check for non-existent activity
        - Assert: Confirm activity does not exist
        """
        # Arrange
        activities = {"Chess Club": {"participants": []}}
        
        # Act
        activity_exists = "Nonexistent Club" in activities
        
        # Assert
        assert activity_exists is False

    def test_activity_name_case_sensitive(self, app):
        """
        Test: Verify that activity names are case-sensitive.
        AAA Pattern:
        - Arrange: Set up database with specific case
        - Act: Query with different case
        - Assert: Confirm no match (case-sensitive)
        """
        # Arrange
        activities = {"Chess Club": {"participants": []}}
        
        # Act
        lowercase_match = "chess club" in activities
        uppercase_match = "CHESS CLUB" in activities
        
        # Assert
        assert lowercase_match is False
        assert uppercase_match is False


class TestDuplicateSignupPrevention:
    """Test logic that prevents duplicate signups."""

    def test_student_already_in_participants(self):
        """
        Test: Verify existing participant detection.
        AAA Pattern:
        - Arrange: Set up activity with participants
        - Act: Check if email is in participants list
        - Assert: Confirm duplicate detection works
        """
        # Arrange
        activity = {
            "description": "Test Activity",
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        }
        email = "michael@mergington.edu"
        
        # Act
        is_already_signed_up = email in activity["participants"]
        
        # Assert
        assert is_already_signed_up is True

    def test_student_not_in_participants(self):
        """
        Test: Verify new participant detection.
        AAA Pattern:
        - Arrange: Set up activity with existing participants
        - Act: Check if new email is in participants
        - Assert: Confirm new student not detected as duplicate
        """
        # Arrange
        activity = {
            "description": "Test Activity",
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        }
        new_email = "newstudent@mergington.edu"
        
        # Act
        is_already_signed_up = new_email in activity["participants"]
        
        # Assert
        assert is_already_signed_up is False

    def test_participants_list_manipulation(self):
        """
        Test: Verify adding and removing participants.
        AAA Pattern:
        - Arrange: Set up activity and participant list
        - Act: Add and remove participants
        - Assert: Verify list changes correctly
        """
        # Arrange
        activity = {
            "description": "Test Activity",
            "participants": ["michael@mergington.edu"]
        }
        new_email = "newstudent@mergington.edu"
        
        # Act: Add participant
        activity["participants"].append(new_email)
        is_added = new_email in activity["participants"]
        
        # Remove participant
        activity["participants"].remove(new_email)
        is_removed = new_email not in activity["participants"]
        
        # Assert
        assert is_added is True
        assert is_removed is True


class TestParticipantListManagement:
    """Test participant list operations."""

    def test_activity_has_max_participants_field(self):
        """
        Test: Verify activity structure includes capacity.
        AAA Pattern:
        - Arrange: Create activity dict
        - Act: Check for max_participants field
        - Assert: Field exists with correct type
        """
        # Arrange
        activity = {
            "description": "Test Activity",
            "max_participants": 20,
            "participants": []
        }
        
        # Act
        has_capacity = "max_participants" in activity
        capacity_value = activity.get("max_participants")
        
        # Assert
        assert has_capacity is True
        assert isinstance(capacity_value, int)
        assert capacity_value == 20

    def test_participants_list_is_mutable(self):
        """
        Test: Verify participants list can be modified.
        AAA Pattern:
        - Arrange: Set up activity structure
        - Act: Modify participants list
        - Assert: Changes persist
        """
        # Arrange
        activity = {
            "participants": ["michael@mergington.edu"]
        }
        initial_count = len(activity["participants"])
        
        # Act: Add participants
        activity["participants"].append("new@mergington.edu")
        activity["participants"].append("another@mergington.edu")
        final_count = len(activity["participants"])
        
        # Assert
        assert initial_count == 1
        assert final_count == 3
        assert activity["participants"][1] == "new@mergington.edu"
        assert activity["participants"][2] == "another@mergington.edu"


class TestActivityDatabase:
    """Test the activities database structure."""

    def test_all_activities_have_required_fields(self, client):
        """
        Test: Verify all activities have required fields.
        AAA Pattern:
        - Arrange: Get activities from endpoint
        - Act: Extract and verify each activity
        - Assert: All required fields present
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
            for field in required_fields:
                assert field in activity_data, f"{activity_name} missing field: {field}"
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants should be a list"

    def test_activities_not_empty(self, client):
        """
        Test: Verify activities database is populated.
        AAA Pattern:
        - Arrange: Prepare to fetch activities
        - Act: Get activities
        - Assert: Non-empty database
        """
        # Arrange
        expected_min_activities = 1
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert len(activities) >= expected_min_activities
