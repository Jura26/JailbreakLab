import pytest
from fastapi.testclient import TestClient

# Try to import the app, but skip if there are import issues with guardrails
try:
    from main import app
    client = TestClient(app)
    APP_AVAILABLE = True
except ImportError as e:
    if "DetectJailbreak" in str(e):
        APP_AVAILABLE = False
        print("Skipping tests due to missing Guardrails DetectJailbreak validator")
    else:
        raise

@pytest.mark.skipif(not APP_AVAILABLE, reason="App not available due to missing dependencies")
def test_root_endpoint():
    """Test the root endpoint returns a welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Backend is running" in response.json()["message"]

@pytest.mark.skipif(not APP_AVAILABLE, reason="App not available due to missing dependencies")
def test_invalid_endpoint():
    """Test accessing an invalid endpoint returns 404"""
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404

@pytest.mark.skipif(not APP_AVAILABLE, reason="App not available due to missing dependencies")
def test_prompt_stream_endpoint_requires_post():
    """Test that prompt stream endpoint requires POST method"""
    response = client.get("/api/prompt/stream")
    assert response.status_code == 405  # Method Not Allowed

@pytest.mark.skipif(not APP_AVAILABLE, reason="App not available due to missing dependencies")
def test_prompt_stream_endpoint_requires_data():
    """Test that prompt stream endpoint requires proper data"""
    response = client.post("/api/prompt/stream", json={})
    # This might return an error due to missing required fields, but should not be 405
    assert response.status_code != 405