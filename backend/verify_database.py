"""
Check what tables exist in the Supabase database
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def check_database_tables():
    """Check which tables exist in the database"""
    print("=" * 60)
    print("Checking Database Tables")
    print("=" * 60)

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    supabase = create_client(url, key)

    # Expected tables
    expected_tables = [
        'shipments',
        'drug_protocols',
        'treatments',
        'treatment_drugs',
        'daily_observations',
        'followup_assessments',
        'ai_knowledge'
    ]

    print("\nChecking tables:")
    for table in expected_tables:
        try:
            # Try to query the table
            result = supabase.table(table).select("*").limit(1).execute()
            print(f"  [OK] {table} - exists")
        except Exception as e:
            print(f"  [X] {table} - not found")

    # Check drug protocols
    print("\nChecking sample data:")
    try:
        result = supabase.table('drug_protocols').select("drug_name").execute()
        if result.data:
            print(f"  [OK] drug_protocols has {len(result.data)} records")
            for drug in result.data:
                print(f"       - {drug['drug_name']}")
        else:
            print("  [!] drug_protocols table exists but is empty")
    except Exception as e:
        print(f"  [X] Could not check drug_protocols: {str(e)}")

    print("\n" + "=" * 60)
    print("Database check complete!")
    print("=" * 60)

if __name__ == "__main__":
    check_database_tables()
