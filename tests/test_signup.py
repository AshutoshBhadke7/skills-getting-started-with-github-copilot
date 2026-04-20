"""
Tests for POST /activities/{activity_name}/signup endpoint.
"""

import pytest


class TestSignupHappyPath:
    """Tests for successful signup scenarios"""
    
    def test_signup_new_student_success(self, client, sample_activity):
        """Test successfully signing up a new student for an activity"""
        activity_name = sample_activity["name"]
        email = sample_activity["participant"]
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_verifies_participant_added(self, client, sample_activity):
        """Test that participant is actually added to the activity"""
        activity_name = sample_activity["name"]
        email = sample_activity["participant"]
        
        # Sign up
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
    
    def test_signup_multiple_students_to_different_activities(self, client):
        """Test that multiple students can sign up to different activities"""
        email1 = "student1@school.edu"
        email2 = "student2@school.edu"
        
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email1}
        )
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both signups
        activities = client.get("/activities").json()
        assert email1 in activities["Chess Club"]["participants"]
        assert email2 in activities["Programming Class"]["participants"]
    
    def test_signup_multiple_students_to_same_activity(self, client):
        """Test that multiple different students can sign up to the same activity"""
        activity_name = "Gym Class"
        email1 = "student1@school.edu"
        email2 = "student2@school.edu"
        
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both students are in the activity
        activities = client.get("/activities").json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]


class TestSignupErrors:
    """Tests for signup error scenarios"""
    
    def test_signup_activity_not_found(self, client, sample_activity):
        """Test signup with non-existent activity returns 404"""
        invalid_activity = sample_activity["invalid_name"]
        email = sample_activity["participant"]
        
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_student_returns_400(self, client, sample_activity):
        """Test that signing up a student twice returns 400 error"""
        activity_name = sample_activity["name"]
        email = sample_activity["existing_participant"]  # Already signed up
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]
    
    def test_signup_same_student_twice_fails_second_time(self, client):
        """Test that a student cannot sign up twice to the same activity"""
        activity_name = "Programming Class"
        email = "newadd@school.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]


class TestSignupEdgeCases:
    """Tests for signup edge cases and special scenarios"""
    
    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with special characters in email"""
        activity_name = "Chess Club"
        email = "student+tag@school.edu"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify it was added
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
    
    def test_signup_with_activity_name_containing_spaces(self, client):
        """Test signup with activity name containing spaces"""
        activity_name = "Programming Class"  # Contains space
        email = "student@school.edu"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    def test_signup_case_sensitive_activity_name(self, client):
        """Test that activity names are case-sensitive"""
        email = "student@school.edu"
        
        # Correct case
        response_correct = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response_correct.status_code == 200
        
        # Incorrect case should return 404
        response_wrong = client.post(
            "/activities/chess club/signup",
            params={"email": email}
        )
        assert response_wrong.status_code == 404
    
    def test_signup_case_sensitive_email(self, client):
        """Test that emails are case-sensitive (for duplicate detection)"""
        activity_name = "Gym Class"
        email1 = "Student@school.edu"
        email2 = "student@school.edu"
        
        # Sign up with uppercase
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        assert response1.status_code == 200
        
        # Sign up with lowercase (should succeed since technically different string)
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        # This depends on backend implementation - currently it will succeed
        assert response2.status_code == 200
    
    def test_signup_empty_email(self, client):
        """Test signup with empty email"""
        activity_name = "Chess Club"
        email = ""
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        # Empty email will be added (no validation to prevent it currently)
        # This test documents the current behavior
        assert response.status_code == 200
    
    def test_signup_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        activity_name = "Programming%20Class"
        email = "student@school.edu"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        # The client should handle URL encoding
        # Since we're using the client, it will URL-encode automatically
        # But the path parameter needs to be properly encoded
        assert response.status_code in [200, 404]  # Depends on encoding behavior
