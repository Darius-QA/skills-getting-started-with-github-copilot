"""
End-to-end workflow tests for the activities management system.

Tests complete user workflows that span multiple endpoints.
All tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestUserSignupWorkflow:
    """Tests for complete user signup workflows"""
    
    def test_user_discovers_activities_and_signs_up(self, client):
        """
        ARRANGE: Client fixture with fresh app
        ACT: User gets list of activities, then signs up for one
        ASSERT: Signup completes and user appears in the activity
        """
        # ARRANGE: Client is ready
        
        # ACT: User views available activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # ASSERT: Activities are available
        assert activities_response.status_code == 200
        assert len(activities) > 0
        activity_name = list(activities.keys())[0]  # Pick first activity
        
        # ACT: User signs up for an activity
        email = "new-user@test.edu"
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Signup succeeds
        assert signup_response.status_code == 200
        
        # ACT: User views activities again to verify signup
        updated_response = client.get("/activities")
        updated_activities = updated_response.json()
        
        # ASSERT: User appears in the activity's participant list
        assert email in updated_activities[activity_name]["participants"]
    
    def test_user_signs_up_and_changes_mind(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: User signs up, then realizes they changed their mind and unregisters
        ASSERT: User is properly removed and can sign up again if desired
        """
        # ARRANGE: Setup
        activity_name = "Debate Team"
        email = "indecisive@test.edu"
        
        # ACT: User signs up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ACT: User checks activities and sees themselves
        response = client.get("/activities")
        activities = response.json()
        initial_count = len(activities[activity_name]["participants"])
        
        # ASSERT: User is in the activity
        assert email in activities[activity_name]["participants"]
        
        # ACT: User changes mind and unregisters
        unregister_response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Unregister succeeds
        assert unregister_response.status_code == 200
        
        # ACT: User checks activities again
        response = client.get("/activities")
        activities = response.json()
        final_count = len(activities[activity_name]["participants"])
        
        # ASSERT: User is no longer in the activity
        assert email not in activities[activity_name]["participants"]
        # ASSERT: Participant count decreased by 1
        assert final_count == initial_count - 1


class TestMultipleUserWorkflows:
    """Tests for workflows with multiple users"""
    
    def test_multiple_users_sign_up_same_activity(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: Multiple users sign up for the same activity
        ASSERT: All users appear in the activity's participant list
        """
        # ARRANGE: Setup
        activity_name = "Art Club"
        users = [
            "artist1@test.edu",
            "artist2@test.edu",
            "artist3@test.edu"
        ]
        
        # ACT: Each user signs up
        for email in users:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            # ASSERT: Each signup succeeds
            assert response.status_code == 200
        
        # ACT: Check final state
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # ASSERT: All users are in the activity
        for email in users:
            assert email in activities[activity_name]["participants"]
    
    def test_different_users_sign_up_different_activities(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: Different users sign up for different activities
        ASSERT: Each user appears only in their chosen activity
        """
        # ARRANGE: Setup
        signups = {
            "Basketball Team": "player1@test.edu",
            "Art Club": "artist1@test.edu",
            "Science Club": "scientist1@test.edu"
        }
        
        # ACT: Each user signs up for their activity
        for activity_name, email in signups.items():
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # ACT: Get all activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # ASSERT: Each user is in their activity
        for activity_name, email in signups.items():
            assert email in activities[activity_name]["participants"], \
                f"{email} should be in {activity_name}"
        
        # ASSERT: Users are not in other activities
        for activity_name, email in signups.items():
            for other_activity in activities:
                if other_activity != activity_name:
                    assert email not in activities[other_activity]["participants"], \
                        f"{email} should not be in {other_activity}"
    
    def test_user_signup_multiple_activities(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: Same user signs up for multiple activities
        ASSERT: User appears in all activities they signed up for
        """
        # ARRANGE: Setup
        email = "multi@test.edu"
        activities_to_join = ["Chess Club", "Drama Club", "Science Club"]
        
        # ACT: User signs up for multiple activities
        for activity_name in activities_to_join:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # ACT: Get all activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # ASSERT: User is in all activities they signed up for
        for activity_name in activities_to_join:
            assert email in activities[activity_name]["participants"]


class TestActivityBrowsingAndNavigation:
    """Tests for browsing and navigating activities"""
    
    def test_user_views_root_then_activities(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: User visits root, follows redirect to static page, then accesses API
        ASSERT: Both static page and API work seamlessly
        """
        # ACT: User visits root
        root_response = client.get("/", follow_redirects=True)
        
        # ASSERT: Root redirect works
        assert root_response.status_code == 200
        
        # ACT: User then accesses activities API
        activities_response = client.get("/activities")
        
        # ASSERT: API works after static page
        assert activities_response.status_code == 200
        activities = activities_response.json()
        assert len(activities) > 0
    
    def test_user_views_activities_multiple_times(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: User makes multiple GET /activities requests
        ASSERT: Consistency - same data returned (until modified)
        """
        # ACT: First activity view
        response1 = client.get("/activities")
        activities1 = response1.json()
        count1 = sum(len(a["participants"]) for a in activities1.values())
        
        # ACT: Second activity view
        response2 = client.get("/activities")
        activities2 = response2.json()
        count2 = sum(len(a["participants"]) for a in activities2.values())
        
        # ASSERT: Same data returned (no change)
        assert count1 == count2
        
        # ACT: User modifies something (signup)
        email = "viewer@test.edu"
        activity_name = list(activities1.keys())[0]
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ACT: Third activity view
        response3 = client.get("/activities")
        activities3 = response3.json()
        count3 = sum(len(a["participants"]) for a in activities3.values())
        
        # ASSERT: Different count after modification
        assert count3 == count2 + 1
