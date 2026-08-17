"""
Integration tests for signup/unregister endpoints.

Tests the POST /activities/{activity}/signup and DELETE /activities/{activity}/signup endpoints.
All tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestSignupPostEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self, client):
        """
        ARRANGE: Client fixture with sample activities (student not yet signed up)
        ACT: POST signup request with new email
        ASSERT: Signup succeeds with 200 status and correct message
        """
        # ARRANGE: Setup test parameters
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # ACT: Send signup request
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Verify successful signup
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client):
        """
        ARRANGE: Client fixture with sample activities
        ACT: POST signup request, then GET activities to verify
        ASSERT: New participant appears in the activity's participant list
        """
        # ARRANGE: Setup test data
        activity_name = "Programming Class"
        email = "newdev@mergington.edu"
        
        # ACT: Sign up the student
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ACT: Retrieve updated activities
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT: Verify participant was added
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_email_returns_400(self, client):
        """
        ARRANGE: Client fixture; student already signed up (in default data)
        ACT: Try to signup the same email again
        ASSERT: Second signup fails with 400 status and error message
        """
        # ARRANGE: Use an email already signed up (from default data)
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club participants
        
        # ACT: Try to sign up with duplicate email
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Verify we get a 400 error
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        ARRANGE: Client fixture with sample activities
        ACT: Try to signup for an activity that doesn't exist
        ASSERT: Request fails with 404 status
        """
        # ARRANGE: Setup test data with non-existent activity
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # ACT: Try to sign up for non-existent activity
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Verify we get a 404 error
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestUnregisterDeleteEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_existing_participant_success(self, client):
        """
        ARRANGE: Client fixture; student already signed up
        ACT: DELETE unregister request for existing participant
        ASSERT: Unregister succeeds with 200 status
        """
        # ARRANGE: Setup - use default participant from Chess Club
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants
        
        # ACT: Unregister the student
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Verify successful unregister
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
    
    def test_unregister_removes_participant_from_activity(self, client):
        """
        ARRANGE: Client fixture
        ACT: Signup a student, then unregister them, then GET activities
        ASSERT: Participant is no longer in the activity's participant list
        """
        # ARRANGE: Setup test data
        activity_name = "Soccer Team"
        email = "removeme@mergington.edu"
        
        # ACT: First sign up the student
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ACT: Then unregister them
        delete_response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Verify unregister was successful
        assert delete_response.status_code == 200
        
        # ACT: Get updated activities list
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT: Verify participant was removed
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_nonexistent_participant_returns_404(self, client):
        """
        ARRANGE: Client fixture
        ACT: Try to unregister someone who never signed up
        ASSERT: Request fails with 404 status
        """
        # ARRANGE: Setup test data with participant not signed up
        activity_name = "Art Club"
        email = "never-signed-up@mergington.edu"
        
        # ACT: Try to unregister a non-participant
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Verify we get a 404 error
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        ARRANGE: Client fixture with sample activities
        ACT: Try to unregister from an activity that doesn't exist
        ASSERT: Request fails with 404 status
        """
        # ARRANGE: Setup test data
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # ACT: Try to unregister from non-existent activity
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Verify we get a 404 error
        assert response.status_code == 404


class TestSignupUnregisterSequence:
    """Tests for signup/unregister flow sequences"""
    
    def test_signup_unregister_signup_again(self, client):
        """
        ARRANGE: Client fixture
        ACT: Sign up -> Unregister -> Sign up again for same activity
        ASSERT: All operations succeed (ensures removal was complete)
        """
        # ARRANGE: Setup test data
        activity_name = "Drama Club"
        email = "flowtest@mergington.edu"
        
        # ACT & ASSERT: First signup succeeds
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response1.status_code == 200
        
        # ACT & ASSERT: Unregister succeeds
        response2 = client.delete(f"/activities/{activity_name}/signup?email={email}")
        assert response2.status_code == 200
        
        # ACT & ASSERT: Second signup also succeeds (should not be duplicate)
        response3 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response3.status_code == 200
        
        # ASSERT: Final state - participant should be in the list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
    
    def test_multiple_participants_signup(self, client):
        """
        ARRANGE: Client fixture
        ACT: Sign up multiple different students for the same activity
        ASSERT: All signups succeed and all participants appear in the list
        """
        # ARRANGE: Setup test data
        activity_name = "Science Club"
        emails = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        
        # ACT: Sign up multiple students
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            # ASSERT: Each signup succeeds
            assert response.status_code == 200
        
        # ACT: Get updated activities
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT: All students are in the participant list
        for email in emails:
            assert email in activities[activity_name]["participants"]
