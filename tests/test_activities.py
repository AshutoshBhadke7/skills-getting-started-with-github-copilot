"""
Tests for GET /activities endpoint.
"""

import pytest


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) == 9
    
    # Verify all expected activities are present
    expected_activities = [
        "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
        "Swimming Club", "Art Club", "Drama Club", "Math Olympiad", "Science Club"
    ]
    for activity_name in expected_activities:
        assert activity_name in activities


def test_get_activities_has_required_fields(client):
    """Test that each activity has the required fields"""
    response = client.get("/activities")
    activities = response.json()
    
    required_fields = ["description", "schedule", "max_participants", "participants"]
    
    for activity_name, activity_details in activities.items():
        for field in required_fields:
            assert field in activity_details, f"Activity '{activity_name}' is missing field '{field}'"


def test_get_activities_fields_have_correct_types(client):
    """Test that activity fields have the correct data types"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_details in activities.items():
        assert isinstance(activity_details["description"], str), \
            f"Activity '{activity_name}' description should be a string"
        assert isinstance(activity_details["schedule"], str), \
            f"Activity '{activity_name}' schedule should be a string"
        assert isinstance(activity_details["max_participants"], int), \
            f"Activity '{activity_name}' max_participants should be an integer"
        assert isinstance(activity_details["participants"], list), \
            f"Activity '{activity_name}' participants should be a list"


def test_get_activities_participants_are_strings(client):
    """Test that all participant entries are strings (emails)"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_details in activities.items():
        for participant in activity_details["participants"]:
            assert isinstance(participant, str), \
                f"Participant in '{activity_name}' should be a string"
            assert "@" in participant, \
                f"Participant '{participant}' in '{activity_name}' should be an email address"


def test_get_activities_participants_count_within_limit(client):
    """Test that current participant count doesn't exceed max_participants"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_details in activities.items():
        participants_count = len(activity_details["participants"])
        max_participants = activity_details["max_participants"]
        assert participants_count <= max_participants, \
            f"Activity '{activity_name}' has more participants than max allowed"


def test_get_activities_has_initial_participants(client):
    """Test that activities have initial participants from seed data"""
    response = client.get("/activities")
    activities = response.json()
    
    # All activities should have at least 2 initial participants
    for activity_name, activity_details in activities.items():
        assert len(activity_details["participants"]) >= 2, \
            f"Activity '{activity_name}' should have at least 2 initial participants"


def test_get_activities_response_contains_specific_activity_details(client):
    """Test that GET /activities includes specific activity details"""
    response = client.get("/activities")
    activities = response.json()
    
    chess_club = activities.get("Chess Club")
    assert chess_club is not None
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert chess_club["max_participants"] == 12
    assert "michael@mergington.edu" in chess_club["participants"]
