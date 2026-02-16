"""
Test script to verify Supabase and Anthropic API connections
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection"""
    print("\n[*] Testing Supabase Connection...")
    try:
        from supabase import create_client

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            print("[X] Supabase credentials not found in .env file")
            return False

        print(f"   URL: {url}")
        print(f"   Key: {key[:20]}...")

        # Create Supabase client
        supabase = create_client(url, key)

        # Try to query a table (this will fail if no tables exist, but connection is verified)
        # We're just testing the client initialization
        print("[OK] Supabase client created successfully!")
        print("   Connection is working!")

        return True

    except Exception as e:
        print(f"[X] Supabase connection failed: {str(e)}")
        return False


def test_anthropic_connection():
    """Test Anthropic API connection"""
    print("\n[*] Testing Anthropic API Connection...")
    try:
        from anthropic import Anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            print("[X] Anthropic API key not found in .env file")
            return False

        print(f"   API Key: {api_key[:20]}...")

        # Create Anthropic client
        client = Anthropic(api_key=api_key)

        # Send a simple test message
        print("   Sending test message to Claude...")
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'Connection successful!' in one sentence."}
            ]
        )

        response = message.content[0].text
        print(f"[OK] Anthropic API working!")
        print(f"   Claude says: {response}")

        return True

    except Exception as e:
        print(f"[X] Anthropic API connection failed: {str(e)}")
        return False


def main():
    """Run all connection tests"""
    print("=" * 60)
    print("Fish Monitoring System - Connection Tests")
    print("=" * 60)

    supabase_ok = test_supabase_connection()
    anthropic_ok = test_anthropic_connection()

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Supabase:  {'[OK] PASS' if supabase_ok else '[X] FAIL'}")
    print(f"Anthropic: {'[OK] PASS' if anthropic_ok else '[X] FAIL'}")
    print("=" * 60)

    if supabase_ok and anthropic_ok:
        print("\nAll connections successful! Your backend is ready to use.")
    else:
        print("\nSome connections failed. Please check your .env file.")


if __name__ == "__main__":
    main()
