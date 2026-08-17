"""
Edge case and boundary condition tests.

Tests unusual inputs, boundary conditions, and error scenarios.
All tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestEmailValidationEdgeCases:
    """Tests for edge cases in email handling"""
    
    def test_signup_with_minimal_valid_email(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: Sign up with minimal valid email format (a@b.c)
        ASSERT: Signup succeeds (email is valid)
        """
        # ARRANGE: Minimal email format
        activity_name = "Chess Club"
        email = "a@b.c"
        
        # ACT: Sign up with minimal email
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Signup succeeds (minimal format is valid)
        assert response.status_code == 200
    
    def test_signup_with_special_characters_in_email(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: Sign up with special characters in email (allowed in local part)
        ASSERT: Signup succeeds
        """
        # ARRANGE: Email with special chars
        activity_name = "Science Club"
        email = "user+tag.name@example.co.uk"
        
        # ACT: Sign up with special char email
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Signup succeeds
        assert response.status_code == 200
    
    def test_signup_case_sensitive_email(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: Sign up with email, then try same email in different case
        ASSERT: Case is preserved but email matching is case-sensitive
        """
        # ARRANGE: Setup
        activity_name = "Drama Club"
        email_lower = "testuser@example.com"
        email_upper = "TESTUSER@EXAMPLE.COM"
        
        # ACT: Sign up with lowercase email
        response1 = client.post(f"/activities/{activity_name}/signup?email={email_lower}")
        assert response1.status_code == 200
        
        # ACT: Try to sign up with uppercase version
        response2 = client.post(f"/activities/{activity_name}/signup?email={email_upper}")
        
        # ASSERT: Second signup should succeed (case-sensitive comparison)
        # This tests the actual behavior - if emails are case-sensitive
        # Comment: Adjust based on actual implementation intent
        assert response2.status_code == 200  # They're treated as different emails
    
    def test_signup_with_whitespace_email(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: Try to sign up with email containing whitespace
        ASSERT: Email is treated as-is (no automatic trimming)
        """
        # ARRANGE: Email with spaces
        activity_name = "Debate Team"
        email = "user with spaces@example.com"
        
        # ACT: Sign up with whitespace email
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Email is accepted as literal (implementation-dependent)
        # System accepts the email as provided
        assert response.status_code == 200


class TestActivityNameEdgeCases:
    """Tests for edge cases in activity name handling"""
    
    def test_activity_name_case_sensitive(self, client):
        """
        ARRANGE: Client with sample activities (e.g., "Chess Club")
        ACT: Try to signup for same activity with different case
        ASSERT: Activity names are case-sensitive
        """
        # ARRANGE: Setup
        email = "test@example.com"
        correct_name = "Chess Club"
        wrong_case = "chess club"
        
        # ACT: Try signup with correct case
        response1 = client.post(f"/activities/{correct_name}/signup?email={email}")
        
        # ASSERT: Correct case works
        assert response1.status_code == 200
        
        # ACT: Try signup with wrong case
        response2 = client.post(f"/activities/{wrong_case}/signup?email={email}2")
        
        # ASSERT: Wrong case fails
        assert response2.status_code == 404
    
    def test_empty_string_activity_name(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: Try to signup for activity with empty string name
        ASSERT: Request fails (no matching activity)
        """
        # ARRANGE: Setup
        email = "test@example.com"
        activity_name = ""
        
        # ACT: Try signup with empty activity name
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Should fail (empty activity doesn't exist)
        assert response.status_code == 404


class TestParticipantCountBoundaries:
    """Tests for participant count boundaries"""
    
    def test_activity_with_single_participant(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: Sign up one user for an activity (which may already have participants)
        ASSERT: Participant count increases appropriately
        """
        # ARRANGE: Setup
        activity_name = "Basketball Team"
        email = "newplayer@test.edu"
        
        # ACT: Get initial state
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # ACT: Add one participant
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ACT: Get final state
        response = client.get("/activities")
        final_count = len(response.json()[activity_name]["participants"])
        
        # ASSERT: Count increased by exactly 1
        assert final_count == initial_count + 1
    
    def test_signup_order_is_preserved(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: Sign up multiple users in specific order
        ASSERT: Participants appear in the order they signed up
        """
        # ARRANGE: Setup
        activity_name = "Soccer Team"
        users = ["user1@test.edu", "user2@test.edu", "user3@test.edu"]
        
        # ACT: Sign up users in order
        for email in users:
            client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ACT: Get final list
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        # ASSERT: Our new users appear in the order we added them
        # Find their indices
        indices = [participants.index(email) for email in users]
        # ASSERT: Indices are in increasing order (order preserved)
        assert indices == sorted(indices)


class TestDuplicateAndConflictScenarios:
    """Tests for duplicate and conflicting operations"""
    
    def test_rapid_duplicate_signup_attempts(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: Make two rapid signup requests for the same email
        ASSERT: First succeeds, second fails with 400
        """
        # ARRANGE: Setup
        activity_name = "Art Club"
        email = "duplicate@test.edu"
        
        # ACT: First signup
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response1.status_code == 200
        
        # ACT: Immediate second signup
        response2 = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Second signup fails
        assert response2.status_code == 400
    
    def test_unregister_then_immediate_signup(self, client):
        """
        ARRANGE: Client with fresh app
        ACT: Sign up, unregister, then immediately sign up again
        ASSERT: All operations succeed (no race condition issues)
        """
        # ARRANGE: Setup
        activity_name = "Science Club"
        email = "flipflop@test.edu"
        
        # ACT: Sign up
        r1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert r1.status_code == 200
        
        # ACT: Unregister
        r2 = client.delete(f"/activities/{activity_name}/signup?email={email}")
        assert r2.status_code == 200
        
        # ACT: Sign up again immediately
        r3 = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT: Third signup succeeds
        assert r3.status_code == 200


class TestEmptyAndSpecialActivityStates:
    """Tests for activities in special states"""
    
    def test_view_empty_activity(self, empty_client):
        """
        ARRANGE: empty_client fixture with no activities
        ACT: Make GET /activities request
        ASSERT: Response is empty dict (valid response)
        """
        # ACT: Get activities from empty app
        response = empty_client.get("/activities")
        
        # ASSERT: Response is valid but empty
        assert response.status_code == 200
        assert response.json() == {}
    
    def test_signup_to_nonexistent_activity_in_empty_app(self, empty_client):
        """
        ARRANGE: empty_client with no activities
        ACT: Try to sign up for any activity
        ASSERT: All signup attempts fail with 404
        """
        # ARRANGE: Setup
        email = "test@example.com"
        
        # ACT: Try to signup for any activity (none exist)
        response = empty_client.post(f"/activities/SomeActivity/signup?email={email}")
        
        # ASSERT: Fails with 404
        assert response.status_code == 404
