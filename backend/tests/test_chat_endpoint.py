"""
Tests for the /chat evaluation endpoint using real HTTP calls
NOTE: Backend must be running on http://localhost:8000 before running these tests
Start backend with: cd backend && python main.py
"""
import pytest
import requests
import time

# Backend configuration
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/chat"
HEALTH_ENDPOINT = f"{BASE_URL}/health"


@pytest.fixture(scope="session", autouse=True)
def check_server_running():
    """Check if backend server is running before tests"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code != 200:
            pytest.exit(f"❌ Backend health check failed. Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        pytest.exit(f"❌ Cannot connect to backend at {BASE_URL}\n"
                   f"Please start the backend first:\n"
                   f"  cd backend\n"
                   f"  python main.py")
    except Exception as e:
        pytest.exit(f"❌ Error checking backend: {str(e)}")

    print(f"\n✅ Backend is running at {BASE_URL}\n")


@pytest.fixture
def client():
    """Provide session for making HTTP requests"""
    return requests.Session()


class TestChatEndpoint:
    """Test suite for the /chat evaluation endpoint"""

    def test_chat_endpoint_exists(self, client):
        """Test that the /chat endpoint exists and accepts POST requests"""
        response = client.post(CHAT_ENDPOINT, json={"question": "Test"}, timeout=120)
        assert response.status_code == 200

    def test_chat_endpoint_format(self, client):
        """Test that the endpoint accepts the correct request format"""
        request_data = {"question": "Quels sont les horaires d'ouverture?"}
        response = client.post(CHAT_ENDPOINT, json=request_data, timeout=120)

        assert response.status_code == 200
        assert "answer" in response.json()

    def test_chat_endpoint_response_format(self, client):
        """Test that the endpoint returns the correct response format"""
        request_data = {"question": "Quel est le tarif pour un enfant?"}
        response = client.post(CHAT_ENDPOINT, json=request_data, timeout=120)

        assert response.status_code == 200
        data = response.json()

        # Check response has 'answer' field
        assert "answer" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0

    def test_chat_endpoint_with_visit_question(self, client):
        """Test the endpoint with a visit planning question"""
        request_data = {"question": "Je veux visiter le 29 août, que me conseilles-tu?"}
        response = client.post(CHAT_ENDPOINT, json=request_data, timeout=120)

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 0

    def test_chat_endpoint_with_ticket_question(self, client):
        """Test the endpoint with a ticket question"""
        request_data = {"question": "Combien coûte un billet?"}
        response = client.post(CHAT_ENDPOINT, json=request_data, timeout=120)

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 0

    def test_chat_endpoint_with_hours_question(self, client):
        """Test the endpoint with opening hours question"""
        request_data = {"question": "Quels sont les horaires d'ouverture du château?"}
        response = client.post(CHAT_ENDPOINT, json=request_data, timeout=120)

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 0

    def test_chat_endpoint_with_empty_question(self, client):
        """Test the endpoint with an empty question"""
        request_data = {"question": ""}
        response = client.post(CHAT_ENDPOINT, json=request_data, timeout=120)

        # Should still return 200 with a response
        assert response.status_code == 200
        assert "answer" in response.json()

    def test_chat_endpoint_missing_question_field(self, client):
        """Test the endpoint with missing 'question' field"""
        request_data = {}
        response = client.post(CHAT_ENDPOINT, json=request_data, timeout=120)

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_chat_endpoint_wrong_field_name(self, client):
        """Test the endpoint with wrong field name"""
        request_data = {"query": "Test question"}
        response = client.post(CHAT_ENDPOINT, json=request_data, timeout=120)

        # Should return 422 for validation error (missing 'question' field)
        assert response.status_code == 422

    def test_chat_endpoint_multiple_questions(self, client):
        """Test the endpoint with multiple consecutive questions"""
        questions = [
            "Quels sont les horaires?",
            "Quel est le tarif?",
            "Comment y aller?",
        ]

        for question in questions:
            response = client.post(CHAT_ENDPOINT, json={"question": question}, timeout=120)
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert len(data["answer"]) > 0

    def test_chat_endpoint_french_response(self, client):
        """Test that the endpoint responds in French for French questions"""
        request_data = {"question": "Bonjour, quels sont les tarifs?"}
        response = client.post(CHAT_ENDPOINT, json=request_data, timeout=120)

        assert response.status_code == 200
        data = response.json()
        answer = data["answer"]

        # Check that response is in French (contains French words)
        french_indicators = ["le", "la", "les", "de", "du", "des", "à", "et", "un", "une"]
        assert any(word in answer.lower() for word in french_indicators)

    def test_chat_endpoint_english_response(self, client):
        """Test that the endpoint responds in English for English questions"""
        request_data = {"question": "What are the opening hours?"}
        response = client.post(CHAT_ENDPOINT, json=request_data, timeout=120)

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 0

    def test_health_endpoint(self, client):
        """Test the health endpoint to ensure backend is working"""
        response = client.get(HEALTH_ENDPOINT, timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])