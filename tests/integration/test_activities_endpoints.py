"""
Integration tests for activities endpoints.

Tests the GET /activities endpoint that returns all activities with participants.
All tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """
        ARRANGE: Client fixture provides app with default activities
        ACT: Make GET request to /activities
        ASSERT: Response contains all expected activities
        """
        # ARRANGE is implicit - client fixture provides fresh app with sample data
        
        # ACT: Get all activities
        response = client.get("/activities")
        
        # ASSERT: Verify successful response
        assert response.status_code == 200
        activities = response.json()
        
        # ASSERT: Verify expected activities are present
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Soccer Team", "Art Club",
            "Drama Club", "Debate Team", "Science Club"
        ]
        for activity in expected_activities:
            assert activity in activities
    
    def test_get_activities_has_required_fields(self, client):
        """
        ARRANGE: Client fixture provides fresh app
        ACT: Make GET request to /activities
        ASSERT: Each activity has required fields (description, schedule, participants, max_participants)
        """
        # ACT: Get all activities
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT: Verify structure of each activity
        required_fields = {"description", "schedule", "participants", "max_participants"}
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
            assert required_fields.issubset(activity_data.keys()), \
                f"{activity_name} missing required fields"
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants should be a list"
    
    def test_get_activities_participants_list_populated(self, client):
        """
        ARRANGE: Client provides app with default activities (some have participants)
        ACT: Make GET request to /activities
        ASSERT: Activities have expected participants from default data
        """
        # ACT: Get all activities
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT: Verify Chess Club has initial participants
        assert "Chess Club" in activities
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
    
    def test_get_activities_empty_app_returns_empty_dict(self, empty_client):
        """
        ARRANGE: empty_client fixture provides app with no activities
        ACT: Make GET request to /activities
        ASSERT: Response is empty dictionary (not None or error)
        """
        # ACT: Get activities from empty app
        response = empty_client.get("/activities")
        
        # ASSERT: Successful response with empty dict
        assert response.status_code == 200
        activities = response.json()
        assert activities == {}
    
    def test_get_activities_response_content_type(self, client):
        """
        ARRANGE: Client fixture
        ACT: Make GET request to /activities
        ASSERT: Response is JSON with correct content-type header
        """
        # ACT: Get activities
        response = client.get("/activities")
        
        # ASSERT: Verify JSON content type
        assert response.headers.get("content-type") == "application/json"
