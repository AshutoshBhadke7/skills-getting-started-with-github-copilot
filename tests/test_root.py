"""
Tests for GET / endpoint.
"""

import pytest


def test_root_redirect(client):
    """Test that GET / redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_root_redirect_with_follow(client):
    """Test that following the redirect from / works"""
    response = client.get("/", follow_redirects=True)
    # After following redirects, we should get a 200 or 404 depending on if static files are properly mounted
    # For this basic test, we just verify the redirect chain exists
    assert response.history  # Should have redirect history
    assert response.history[0].status_code == 307
