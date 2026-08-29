"""
Diagnostic script to test the API directly
"""

import os
from dotenv import load_dotenv

# Load env
load_dotenv()

print("="*70)
print("🔍 CPIP API DIAGNOSTIC")
print("="*70)

# Check 1: RAPIDAPI_KEY
api_key = os.environ.get("RAPIDAPI_KEY")
print(f"\n1️⃣  RAPIDAPI_KEY: ", end="")
if api_key:
    print(f"✅ FOUND ({len(api_key)} chars)")
else:
    print(f"❌ NOT SET - ADD TO .env FILE")

# Check 2: Test direct API call
print(f"\n2️⃣  Testing direct API call...")
try:
    import requests
    
    response = requests.get(
        "https://active-jobs-db.p.rapidapi.com/active-ats",
        headers={
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "active-jobs-db.p.rapidapi.com"
        },
        params={
            "title": "backend developer",
            "location": "India",
            "limit": 5,
        },
        timeout=30,
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            print(f"   ✅ API returned list with {len(data)} jobs")
        else:
            print(f"   Data returned: {type(data)}")
            print(f"   Content: {str(data)[:200]}")
    else:
        print(f"   ❌ API error: {response.text[:200]}")

except Exception as e:
    print(f"   ❌ Error: {e}")

# Check 3: Student data
print(f"\n3️⃣  Checking student data...")
try:
    from app.data import seed_data
    student = seed_data.get_student(1)
    if student:
        print(f"   ✅ Student found: {student.get('name')}")
        print(f"   Target role: '{student.get('target_role')}'")
        print(f"   Skills: {student.get('skills')}")
    else:
        print(f"   ❌ Student 1 not found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check 4: Query builder
print(f"\n4️⃣  Testing query builder...")
try:
    from app.services.semantic_query_builder import build_semantic_query
    query = build_semantic_query(
        target_role="Backend Developer",
        resume_skills=["Python", "FastAPI"],
        resume_text="Built APIs"
    )
    print(f"   ✅ Query built: '{query}'")
except Exception as e:
    print(f"   ❌ Error: {e}")

print(f"\n{'='*70}")