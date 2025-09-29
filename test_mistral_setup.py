#!/usr/bin/env python3
"""
Test Mistral AI setup and environment
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_setup():
    """Test if Mistral AI is properly configured"""
    
    print("🔧 Testing Mistral AI Setup")
    print("-" * 40)
    
    # Check for API key
    mistral_key = os.getenv('MISTRAL_API_KEY')
    
    if not mistral_key:
        print("❌ MISTRAL_API_KEY not found in .env file")
        print("\n📝 Please add your Mistral API key to .env file:")
        print("   MISTRAL_API_KEY=your_actual_mistral_key_here")
        print("\n💡 Get your API key from: https://console.mistral.ai/")
        return False
    
    if mistral_key == "your_mistral_api_key_here":
        print("⚠️  MISTRAL_API_KEY is still set to placeholder value")
        print("\n📝 Please update it with your actual API key in .env file")
        print("\n💡 Get your API key from: https://console.mistral.ai/")
        return False
    
    print(f"✅ MISTRAL_API_KEY found: {mistral_key[:8]}...")
    
    # Check model configuration
    model = os.getenv('MISTRAL_MODEL', 'mistral-large-latest')
    print(f"✅ Using model: {model}")
    
    # Test import
    try:
        from mistralai.async_client import MistralAsyncClient
        print("✅ Mistral AI library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Mistral AI library: {e}")
        print("\n📦 Please install dependencies:")
        print("   pip install -r requirements.txt")
        return False
    
    print("\n✅ Setup looks good! Ready to run the research agent.")
    return True

if __name__ == "__main__":
    test_setup()
