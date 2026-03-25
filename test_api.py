#!/usr/bin/env python3
"""Kimi API Bağlantı Testi"""

from openai import OpenAI

API_KEY = "sk-V9fu4RZdxLADmp9q9G7VgHGCdGxMwAFFeEX2cuF4VkuUybXc"
BASE_URL = "https://api.moonshot.ai/v1"

print("=" * 50)
print("Kimi 2.5 API Baglanti Testi")
print("=" * 50)

try:
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )

    print("\n[1] Mevcut modelleri kontrol ediyorum...")

    # Mevcut modelleri listele
    try:
        models = client.models.list()
        print("Mevcut modeller:")
        for m in models.data[:10]:
            print(f"  - {m.id}")
    except Exception as e:
        print(f"Model listesi alinamadi: {e}")

    print("\n[2] API'ye baglaniliyor (moonshot-v1-8k modeli)...")

    # moonshot-v1-8k modeli ile test (daha stabil)
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": "Sen yardimci bir AI asistanisin. Turkce yanit ver."},
            {"role": "user", "content": "Merhaba! 2+2 kac eder? Tek cumleyle yanitla."}
        ],
        max_tokens=100,
        temperature=0.7
    )

    content = response.choices[0].message.content
    print("[3] Yanit alindi!")
    print(f"\n[Kimi]: {content}")
    print(f"\n[Model]: {response.model}")
    print(f"[Tokens]: {response.usage.total_tokens}")

    print("\n" + "=" * 50)
    print("TEST BASARILI!")
    print("=" * 50)

except Exception as e:
    print(f"\n[HATA]: {type(e).__name__}: {e}")

    import traceback
    traceback.print_exc()
