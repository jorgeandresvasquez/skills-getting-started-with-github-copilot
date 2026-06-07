"""
Integration tests for FastAPI endpoints.

Tests HTTP endpoints with real request/response cycle using AAA pattern:
- Arrange: Set up test client and request parameters
- Act: Make HTTP request
- Assert: Verify response status, headers, and body
"""

import pytest


class TestRootEndpoint:
    """Test GET / endpoint for root redirect."""

    def test_root_redirects_to_static_index(self, client):
        """
        Test: GET / redirects to static index page.
        AAA Pattern:
        - Arrange: Create test client
        - Act: Send GET request to root
        - Assert: Response is redirect (307) to /static/index.html
        """
        # Arrange
        expected_status = 307
        expected_location = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == expected_status
        assert response.headers.get("location") == expected_location

    def test_root_redirect_with_follow(self, client):
        """
        Test: Following redirect from / leads to static files.
        AAA Pattern:
        - Arrange: Prepare to follow redirects
        - Act: GET / with follow_redirects=True
        - Assert: Final response contains expected HTML
        """
        # Arrange
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert - Should get 200 and HTML content (not a 404)
        assert response.status_code == 200


class TestGetActivitiesEndpoint:
    """Test GET /activities endpoint."""

    def test_get_all_activities_returns_dict(self, client):
        """
        Test: GET /activities returns all activities.
        AAA Pattern:
        - Arrange: Prepare request
        - Act: Send GET request to /activities
        - Assert: Response is 200 with activities dict
        """
        # Arrange
        expected_status = 200
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == expected_status
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_get_activities_includes_all_required_fields(self, client):
        """
        Test: Each activity has required fields.
        AAA Pattern:
        - Arrange: Define required fields
        - Act: Fetch activities and check structure
        - Assert: All fields present in all activities
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            for field in required_fields:
                assert field in activity_data, f"Missing {field} in {activity_name}"

    def test_get_activities_participants_is_list(self, client):
        """
        Test: Participants field is always a list.
        AAA Pattern:
        - Arrange: Prepare to check structure
        - Act: Get activities and examine participants
        - Assert: Participants are lists in all activities
        """
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants should be a list"

    def test_get_activities_chess_club_has_initial_participants(self, client):
        """
        Test: Chess Club has pre-populated participants.
        AAA Pattern:
        - Arrange: Know Chess Club initial state
        - Act: Fetch Chess Club from activities
        - Assert: Contains expected participants
        """
        # Arrange
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities.get("Chess Club", {})
        
        # Assert
        assert chess_club.get("participants") == expected_participants


class TestSignupEndpoint:
    """Test POST /activities/{activity}/signup endpoint."""

    def test_signup_valid_student_returns_success(self, client):
        """
        Test: Valid signup for new student returns 200.
        AAA Pattern:
        - Arrange: Prepare signup with valid activity and new email
        - Act: POST signup request
        - Assert: Returns 200 with success message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """
        Test: Signup adds participant to activity list.
        AAA Pattern:
        - Arrange: Choose activity and new email
        - Act: Sign up, then fetch activities
        - Assert: Participant appears in activity
        """
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        
        # Act: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Get activities to verify
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Test: Signup for non-existent activity returns 404.
        AAA Pattern:
        - Arrange: Use non-existent activity name
        - Act: Attempt signup
        - Assert: Returns 404 with error detail
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_email_returns_400(self, client):
        """
        Test: Duplicate signup returns 400.
        AAA Pattern:
        - Arrange: Use already-enrolled student
        - Act: Attempt to sign up same email twice
        - Assert: Second attempt returns 400
        """
        # Arrange
        activity_name = "Chess Club"
        duplicate_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": duplicate_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_multiple_students_different_activities(self, client):
        """
        Test: Multiple students can sign up for different activities.
        AAA Pattern:
        - Arrange: Prepare different activities and emails
        - Act: Sign up students to different activities
        - Assert: All signups succeed independently
        """
        # Arrange
        signups = [
            ("Chess Club", "student1@mergington.edu"),
            ("Programming Class", "student2@mergington.edu"),
            ("Gym Class", "student3@mergington.edu"),
        ]
        
        # Act & Assert
        for activity_name, email in signups:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

    def test_signup_same_student_different_activities(self, client):
        """
        Test: Same student can signup for multiple activities.
        AAA Pattern:
        - Arrange: Prepare activities and single email
        - Act: Sign up same student to multiple activities
        - Assert: All signups succeed
        """
        # Arrange
        email = "versatile@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Drama Club"]
        
        # Act & Assert
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200


class TestUnregisterEndpoint:
    """Test DELETE /activities/{activity}/participants/{email} endpoint."""

    def test_unregister_existing_participant_returns_success(self, client):
        """
        Test: Unregister existing participant returns 200.
        AAA Pattern:
        - Arrange: Choose activity with known participant
        - Act: DELETE request to unregister
        - Assert: Returns 200 with success message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Pre-populated participant
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email in response.json()["message"]

    def test_unregister_removes_participant_from_list(self, client):
        """
        Test: Unregister removes participant from activity.
        AAA Pattern:
        - Arrange: Identify participant in activity
        - Act: Unregister, then fetch activities
        - Assert: Participant no longer in activity list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Verify participant exists initially
        activities_before = client.get("/activities").json()
        assert email in activities_before[activity_name]["participants"]
        
        # Act: Unregister
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Get activities after unregister
        activities_after = client.get("/activities").json()
        
        # Assert
        assert response.status_code == 200
        assert email not in activities_after[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Test: Unregister from non-existent activity returns 404.
        AAA Pattern:
        - Arrange: Use non-existent activity
        - Act: Attempt DELETE
        - Assert: Returns 404
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_nonexistent_participant_returns_400(self, client):
        """
        Test: Unregister non-existent participant returns 400.
        AAA Pattern:
        - Arrange: Use valid activity but non-existent email
        - Act: Attempt DELETE
        - Assert: Returns 400
        """
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "notinlist@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_twice_returns_error_on_second(self, client):
        """
        Test: Unregistering same student twice returns error on second attempt.
        AAA Pattern:
        - Arrange: Prepare participant to unregister twice
        - Act: First DELETE succeeds, second DELETE fails
        - Assert: First is 200, second is 400
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act: First unregister
        first_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Second unregister attempt
        second_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert first_response.status_code == 200
        assert second_response.status_code == 400

    def test_unregister_specific_participant_leaves_others(self, client):
        """
        Test: Unregistering one participant doesn't affect others.
        AAA Pattern:
        - Arrange: Note all participants in activity
        - Act: Unregister one specific participant
        - Assert: Other participants remain in list
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        activities_before = client.get("/activities").json()
        original_participants = activities_before[activity_name]["participants"].copy()
        
        # Act: Unregister one
        response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # Get updated activities
        activities_after = client.get("/activities").json()
        remaining_participants = activities_after[activity_name]["participants"]
        
        # Assert
        assert response.status_code == 200
        assert email_to_remove not in remaining_participants
        # Others should still be there
        for email in original_participants:
            if email != email_to_remove:
                assert email in remaining_participants
