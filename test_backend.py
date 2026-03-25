#!/usr/bin/env python3
"""Backend API Testi"""

import requests
import json

API_URL = "http://localhost:8000"

print("=" * 50)
print("Kimi Backend API Testi")
print("=" * 50)

# 1. Health check
print("\n[1] Health Check...")
try:
    r = requests.get(f"{API_URL}/health")
    print(f"    Status: {r.json()}")
except Exception as e:
    print(f"    HATA: {e}")

# 2. Chat test
print("\n[2] Chat API Testi...")
try:
    r = requests.post(
        f"{API_URL}/chat",
        json={
            "message": "Merhaba! 5+3 kac eder?",
            "workspace": "."
        }
    )
    data = r.json()
    print(f"    Session: {data.get('session_id', 'N/A')[:8]}...")
    print(f"    Response: {data.get('response', 'N/A')[:200]}")
    print(f"    Tool Calls: {len(data.get('tool_calls', []))}")
except Exception as e:
    print(f"    HATA: {e}")

# 3. Sessions list
print("\n[3] Sessions...")
try:
    r = requests.get(f"{API_URL}/sessions")
    sessions = r.json()
    print(f"    Toplam session: {len(sessions)}")
except Exception as e:
    print(f"    HATA: {e}")

print("\n" + "=" * 50)
print("TEST TAMAMLANDI!")
print("=" * 50)
print("\nFrontend: http://localhost:3000")
print("API Docs: http://localhost:8000/docs")
