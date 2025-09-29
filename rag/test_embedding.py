#!/usr/bin/env python3
"""
Test Qwen3-Embedding-8B with Hugging Face InferenceClient
"""
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()

def test_qwen_embedding():
    """Test the embedding API"""
    try:
        # Get token from environment
        hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_TOKEN")

        if not hf_token:
            print("❌ No HF_TOKEN or HUGGINGFACE_API_TOKEN found in environment!")
            return False

        # Initialize client with Nebius provider
        client = InferenceClient(
            provider="nebius",
            api_key=hf_token,
        )

        # Test text
        text = "Today is a sunny day and I will get some ice cream."
        print(f"Testing with text: {text}")

        # Get embedding
        result = client.feature_extraction(
            text,
            model="Qwen/Qwen3-Embedding-4B",
        )

        print(f"✅ Success!")
        print(f"Embedding shape: {len(result)} dimensions")
        print(f"First 5 values: {result[:5]}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🏰 Testing Qwen3-Embedding-8B via Nebius provider...")
    test_qwen_embedding()