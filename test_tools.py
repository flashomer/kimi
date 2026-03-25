#!/usr/bin/env python3
"""Tool Calling Testi"""

import requests
import json

API_URL = "http://localhost:8000"

print("=" * 50)
print("Kimi Tool Calling Testi")
print("=" * 50)

# Tool gerektiren istek
print("\n[1] Dosya listeleme istegi gonderiliyor...")
try:
    r = requests.post(
        f"{API_URL}/chat",
        json={
            "message": "Mevcut dizindeki dosyalari listele",
            "workspace": "/app"
        },
        timeout=60
    )
    data = r.json()

    print(f"\n[2] Sonuc:")
    print(f"    Session: {data.get('session_id', 'N/A')[:8]}...")

    response = data.get('response', '')
    print(f"\n[Kimi Yaniti]:\n{response[:500]}")

    tool_calls = data.get('tool_calls', [])
    if tool_calls:
        print(f"\n[Kullanilan Toollar]: {len(tool_calls)} adet")
        for tc in tool_calls:
            print(f"    - {tc['name']}: {tc.get('result', '')[:100]}")

except Exception as e:
    print(f"    HATA: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
