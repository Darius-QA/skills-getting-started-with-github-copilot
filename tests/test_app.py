"""
Legacy tests migrated to use new fixture-based approach with AAA pattern.

These tests demonstrate proper test isolation using fixtures and
follow the Arrange-Act-Assert pattern for clarity.
"""

from fastapi.testclient import TestClient


def test_signup_and_unregister_participant(client):
    """
    Test the full signup and unregister flow for a participant.
    
    Demonstrates: ARRANGE via fixture, ACT with HTTP requests, ASSERT on results
    """
    # ARRANGE: Setup test data
    activity_name = "Chess Club"
    email = "student@mergington.edu"
    
    # ACT: Sign up for activity
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # ASSERT: Verify signup succeeds
    assert signup_response.status_code == 200
    
    # ACT: Unregister from activity
    unregister_response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    # ASSERT: Verify unregister succeeds
    assert unregister_response.status_code == 200
    
    # ASSERT: Verify participant was removed from the activity
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404(client):
    """
    Test that unregistering a participant who never signed up returns 404.
    
    Demonstrates: ARRANGE via fixture, ACT with edge case request, ASSERT on error
    """
    # ARRANGE: Setup test data (participant not yet signed up)
    activity_name = "Chess Club"
    email = "not-registered@mergington.edu"
    
    # ACT: Try to unregister a participant who was never signed up
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    # ASSERT: Verify we get a 404 error
    assert response.status_code == 404
