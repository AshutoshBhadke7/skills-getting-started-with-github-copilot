"""
Tests for DELETE /activities/{activity_name}/unregister endpoint.
"""

import pytest


class TestUnregisterHappyPath:
    """Tests for successful unregister scenarios"""
    
    def test_unregister_existing_student_success(self, client, sample_activity):
        """Test successfully unregistering an existing participant from an activity"""
        activity_name = sample_activity["name"]
        email = sample_activity["existing_participant"]
        
        # Verify participant exists before unregister
        activities_before = client.get("/activities").json()
        assert email in activities_before[activity_name]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_unregister_verifies_participant_removed(self, client, sample_activity):
        """Test that participant is actually removed from the activity"""
        activity_name = sample_activity["name"]
        email = sample_activity["existing_participant"]
        
        # Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_after = client.get("/activities").json()
        assert email not in activities_after[activity_name]["participants"]
    
    def test_unregister_multiple_participants_from_same_activity(self, client):
        """Test unregistering multiple participants from the same activity"""
        activity_name = "Chess Club"
        
        # Get initial participants
        activities_before = client.get("/activities").json()
        initial_participants = activities_before[activity_name]["participants"].copy()
        
        # Unregister first participant
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": initial_participants[0]}
        )
        assert response1.status_code == 200
        
        # Unregister second participant
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": initial_participants[1]}
        )
        assert response2.status_code == 200
        
        # Verify both are removed
        activities_after = client.get("/activities").json()
        assert len(activities_after[activity_name]["participants"]) == \
               len(initial_participants) - 2
    
    def test_unregister_then_signup_again(self, client):
        """Test that a student can sign up again after being unregistered"""
        activity_name = "Programming Class"
        email = "student@school.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify student is signed up
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]


class TestUnregisterErrors:
    """Tests for unregister error scenarios"""
    
    def test_unregister_activity_not_found(self, client, sample_activity):
        """Test unregister with non-existent activity returns 404"""
        invalid_activity = sample_activity["invalid_name"]
        email = sample_activity["participant"]
        
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_unregister_student_not_registered(self, client, sample_activity):
        """Test unregistering a student who is not registered returns 400"""
        activity_name = sample_activity["name"]
        email = sample_activity["participant"]  # This student is not registered
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"]
    
    def test_unregister_same_student_twice_fails_second_time(self, client):
        """Test that unregistering the same student twice fails the second time"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Initially registered
        
        # First unregister should succeed
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "not registered" in response2.json()["detail"]


class TestUnregisterEdgeCases:
    """Tests for unregister edge cases"""
    
    def test_unregister_activity_with_single_participant(self, client):
        """Test unregistering when activity has only one participant"""
        # First, sign up a single student to an activity that has many
        activity_name = "Art Club"
        email = "solo@school.edu"
        
        # Clear all participants from an activity and add only one
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Get current state
        activities = client.get("/activities").json()
        initial_count = len(activities[activity_name]["participants"])
        
        # Unregister one
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify count decreased by 1
        activities_after = client.get("/activities").json()
        assert len(activities_after[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_with_special_characters_in_email(self, client):
        """Test unregister with special characters in email"""
        activity_name = "Basketball Team"
        email = "student+special@school.edu"
        
        # Sign up first
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Then unregister
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
    
    def test_unregister_case_sensitive_activity_name(self, client):
        """Test that activity names are case-sensitive for unregister"""
        email = "michael@mergington.edu"
        
        # Correct case should succeed
        response_correct = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response_correct.status_code == 200
        
        # Incorrect case should return 404
        response_wrong = client.delete(
            "/activities/chess club/unregister",
            params={"email": email}
        )
        assert response_wrong.status_code == 404
    
    def test_unregister_case_sensitive_email(self, client):
        """Test that emails are case-sensitive for unregister"""
        activity_name = "Chess Club"
        original_email = "michael@mergington.edu"
        wrong_case_email = "MICHAEL@MERGINGTON.EDU"
        
        # Try to unregister with wrong case
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": wrong_case_email}
        )
        # Should fail because the email doesn't match exactly
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_empty_email(self, client):
        """Test unregister with empty email"""
        activity_name = "Chess Club"
        email = ""
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        # Empty email won't be in participants, so should fail
        assert response.status_code == 400


class TestUnregisterIntegration:
    """Integration tests for unregister with other operations"""
    
    def test_unregister_affects_availability_count(self, client):
        """Test that unregistering increases available spots"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Get initial availability
        activities_before = client.get("/activities").json()
        initial_available = activities_before[activity_name]["max_participants"] - \
                           len(activities_before[activity_name]["participants"])
        
        # Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Get updated availability
        activities_after = client.get("/activities").json()
        new_available = activities_after[activity_name]["max_participants"] - \
                       len(activities_after[activity_name]["participants"])
        
        # Should have one more available spot
        assert new_available == initial_available + 1
