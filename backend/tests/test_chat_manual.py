"""
Manual test script for the /chat evaluation endpoint
Run this script to manually test the endpoint with various questions
"""
import requests
import json

# Backend URL
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/chat"


def test_endpoint(question: str, description: str = ""):
    """Test the /chat endpoint with a question"""
    print(f"\n{'='*80}")
    if description:
        print(f"Test: {description}")
    print(f"Question: {question}")
    print("-" * 80)

    try:
        # Send request
        response = requests.post(
            CHAT_ENDPOINT,
            json={"question": question},
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        # Check response
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if "answer" in data:
                print(f"\n✅ SUCCESS - Response format is correct")
                print(f"\nAnswer:\n{data['answer']}")
            else:
                print(f"\n❌ FAILED - Response missing 'answer' field")
                print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"\n❌ FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR - Make sure the backend is running on {BASE_URL}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def main():
    """Run all manual tests"""
    print("="*80)
    print("TESTING /chat EVALUATION ENDPOINT")
    print("="*80)

    # Check if backend is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print(f"\n✅ Backend is running at {BASE_URL}")
        else:
            print(f"\n⚠️  Backend returned status {health_response.status_code}")
    except:
        print(f"\n❌ Cannot connect to backend at {BASE_URL}")
        print("Please start the backend first: cd backend && python main.py")
        return

    # Test cases
    test_cases = [
        {
            "question": "Je veux visiter le 29 août, que me conseilles-tu?",
            "description": "Visit planning question (should use RAG, NOT weather)"
        },
        {
            "question": "Quels sont les horaires d'ouverture du château?",
            "description": "Opening hours question"
        },
        {
            "question": "Quel est le tarif pour un enfant de 10 ans?",
            "description": "Ticket price question"
        },
        {
            "question": "Comment se rendre au château depuis Paris?",
            "description": "Transportation question"
        },
        {
            "question": "Quel temps fera-t-il demain à Versailles?",
            "description": "Weather question (should use weather tool)"
        },
        {
            "question": "What are the opening hours?",
            "description": "English question (should respond in English)"
        },
        {
            "question": "Quelles sont les attractions principales?",
            "description": "Attractions question"
        },
    ]

    for test_case in test_cases:
        test_endpoint(
            question=test_case["question"],
            description=test_case["description"]
        )

    print(f"\n{'='*80}")
    print("ALL TESTS COMPLETED")
    print("="*80)


if __name__ == "__main__":
    main()