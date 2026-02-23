"""
Tests for Mergington High School API endpoints

All tests follow the AAA (Arrange-Act-Assert) pattern for clarity and consistency.
"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Tests for the root endpoint (/)"""

    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to /static/index.html"""
        # Arrange: (no setup needed)

        # Act: Make GET request to root
        response = client.get("/", follow_redirects=False)

        # Assert: Verify redirect response
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_success(self, client):
        """Test that GET /activities returns 200 OK"""
        # Arrange: (activities are loaded via reset_activities fixture)

        # Act: Request all activities
        response = client.get("/activities")

        # Assert: Verify successful response
        assert response.status_code == status.HTTP_200_OK

    def test_get_all_activities_returns_correct_structure(self, client):
        """Test that all activities have required fields"""
        # Arrange: Expected fields for each activity
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act: Get activities
        response = client.get("/activities")
        activities = response.json()

        # Assert: Verify structure
        assert len(activities) == 9  # Should have 9 activities
        for activity_name, activity_data in activities.items():
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)

    def test_get_activities_includes_initial_participants(self, client):
        """Test that initial participants are included in response"""
        # Arrange: (initial data loaded via fixture)

        # Act: Get activities
        response = client.get("/activities")
        activities = response.json()

        # Assert: Verify Chess Club has 2 initial participants
        assert "Chess Club" in activities
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]


class TestActivitySignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        # Arrange: Student email and activity with available spots
        email = "new.student@mergington.edu"
        activity = "Basketball Team"

        # Act: Sign up for activity
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert: Verify success
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == f"Signed up {email} for {activity}"

    def test_signup_adds_participant_to_list(self, client):
        """Test that signup actually adds participant to the activity"""
        # Arrange: New student and activity
        email = "test@mergington.edu"
        activity = "Tennis Club"

        # Act: Sign up
        client.post(f"/activities/{activity}/signup?email={email}")

        # Assert: Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Test that signing up for non-existent activity returns 404"""
        # Arrange: Non-existent activity
        email = "student@mergington.edu"
        activity = "Nonexistent Club"

        # Act: Attempt signup
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert: Verify 404 error
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_participant_returns_400(self, client):
        """Test that duplicate signup returns 400 error"""
        # Arrange: Sign up once
        email = "duplicate@mergington.edu"
        activity = "Art Studio"
        client.post(f"/activities/{activity}/signup?email={email}")

        # Act: Attempt duplicate signup
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert: Verify 400 error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup works with URL-encoded activity names"""
        # Arrange: Activity name with space
        email = "student@mergington.edu"
        activity = "Chess Club"
        encoded_activity = "Chess%20Club"

        # Act: Sign up using encoded name
        response = client.post(f"/activities/{encoded_activity}/signup?email={email}")

        # Assert: Verify success
        assert response.status_code == status.HTTP_200_OK


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # Arrange: Use existing participant from Chess Club
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act: Unregister
        response = client.delete(f"/activities/{activity}/participants/{email}")

        # Assert: Verify success
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == f"Unregistered {email} from {activity}"

    def test_unregister_removes_participant_from_list(self, client):
        """Test that unregister actually removes participant from activity"""
        # Arrange: Use existing participant
        email = "emma@mergington.edu"
        activity = "Programming Class"

        # Act: Unregister
        client.delete(f"/activities/{activity}/participants/{email}")

        # Assert: Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity]["participants"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from non-existent activity returns 404"""
        # Arrange: Non-existent activity
        email = "student@mergington.edu"
        activity = "Fake Club"

        # Act: Attempt unregister
        response = client.delete(f"/activities/{activity}/participants/{email}")

        # Assert: Verify 404 error
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_non_registered_participant_returns_400(self, client):
        """Test that unregistering non-registered participant returns 400"""
        # Arrange: Student not registered for this activity
        email = "notregistered@mergington.edu"
        activity = "Basketball Team"

        # Act: Attempt unregister
        response = client.delete(f"/activities/{activity}/participants/{email}")

        # Assert: Verify 400 error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Student not registered for this activity"

    def test_unregister_with_url_encoded_email(self, client):
        """Test unregister works with URL-encoded email addresses"""
        # Arrange: Use existing participant with @ sign that needs encoding
        email = "john@mergington.edu"
        activity = "Gym Class"
        encoded_email = "john%40mergington.edu"

        # Act: Unregister using encoded email
        response = client.delete(f"/activities/{activity}/participants/{encoded_email}")

        # Assert: Verify success
        assert response.status_code == status.HTTP_200_OK


class TestIntegrationScenarios:
    """Integration tests for complete user workflows"""

    def test_complete_signup_and_unregister_flow(self, client):
        """Test complete flow: signup -> verify -> unregister -> verify"""
        # Arrange: New student and activity
        email = "complete.test@mergington.edu"
        activity = "Debate Club"

        # Act & Assert: Step 1 - Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == status.HTTP_200_OK

        # Act & Assert: Step 2 - Verify participant is in list
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        initial_count = len(activities[activity]["participants"])

        # Act & Assert: Step 3 - Unregister
        unregister_response = client.delete(f"/activities/{activity}/participants/{email}")
        assert unregister_response.status_code == status.HTTP_200_OK

        # Act & Assert: Step 4 - Verify participant removed
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count - 1

    def test_participant_count_consistency(self, client):
        """Test that participant counts are consistent across operations"""
        # Arrange: Activity and multiple students
        activity = "Music Ensemble"
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]

        # Act: Get initial count
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity]["participants"])

        # Act: Sign up all students
        for student in students:
            client.post(f"/activities/{activity}/signup?email={student}")

        # Assert: Verify count increased by 3
        after_signup = client.get("/activities").json()
        assert len(after_signup[activity]["participants"]) == initial_count + 3

        # Act: Unregister one student
        client.delete(f"/activities/{activity}/participants/{students[0]}")

        # Assert: Verify count decreased by 1
        after_unregister = client.get("/activities").json()
        assert len(after_unregister[activity]["participants"]) == initial_count + 2
