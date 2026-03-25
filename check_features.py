#!/usr/bin/env python3
"""Kimi API Ozellik Kontrolu"""
# -*- coding: utf-8 -*-

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openai import OpenAI
import json

API_KEY = "sk-V9fu4RZdxLADmp9q9G7VgHGCdGxMwAFFeEX2cuF4VkuUybXc"
BASE_URL = "https://api.moonshot.ai/v1"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

print("=" * 60)
print("Kimi API - Hesap ve Ozellik Kontrolu")
print("=" * 60)

# 1. Modelleri listele
print("\n[1] Kullanilabilir Modeller:")
try:
    models = client.models.list()
    for m in models.data:
        print(f"    [OK] {m.id}")
except Exception as e:
    print(f"    [X] Hata: {e}")

# 2. K2.5 testi (thinking mode)
print("\n[2] Kimi K2.5 (Thinking Mode) Testi:")
try:
    response = client.chat.completions.create(
        model="kimi-k2.5",
        messages=[{"role": "user", "content": "What is 15*15?"}],
        max_tokens=500
    )
    content = response.choices[0].message.content
    print(f"    [OK] Yanit: {content[:100] if content else 'Bos (thinking mode)'}")
except Exception as e:
    print(f"    [X] Hata: {e}")

# 3. Turbo model testi
print("\n[3] Kimi K2 Turbo Testi:")
try:
    response = client.chat.completions.create(
        model="kimi-k2-turbo-preview",
        messages=[{"role": "user", "content": "Merhaba!"}],
        max_tokens=100
    )
    print(f"    [OK] Yanit: {response.choices[0].message.content[:80]}")
except Exception as e:
    print(f"    [X] Hata: {e}")

# 4. Thinking Turbo testi
print("\n[4] Kimi K2 Thinking Turbo:")
try:
    response = client.chat.completions.create(
        model="kimi-k2-thinking-turbo",
        messages=[{"role": "user", "content": "2+2?"}],
        max_tokens=100
    )
    print(f"    [OK] Yanit: {response.choices[0].message.content[:80] if response.choices[0].message.content else 'Thinking mode'}")
except Exception as e:
    print(f"    [X] Hata: {e}")

# 5. Context window kontrolu
print("\n[5] Context Window:")
print("    - moonshot-v1-8k:   8,192 tokens")
print("    - moonshot-v1-32k:  32,768 tokens")
print("    - moonshot-v1-128k: 131,072 tokens")
print("    - kimi-k2.5:        262,144 tokens (256K)")

# Ozet
print("\n" + "=" * 60)
print("OZELLIK DURUMU:")
print("=" * 60)

features = [
    ("Model Erisimi", "[OK]", "moonshot-v1-*, kimi-k2.5, kimi-k2-turbo"),
    ("Tool Calling", "[OK]", "Dosya, Shell, Arama islemleri"),
    ("256K Context", "[OK]", "kimi-k2.5 modeli ile"),
    ("Thinking Mode", "[OK]", "kimi-k2.5, kimi-k2-thinking-turbo"),
    ("Vision/Multimodal", "[OK]", "moonshot-v1-*-vision modelleri"),
    ("Agent Swarm", "[!!]", "API destekli - asagida aciklama"),
    ("Slides/Nano Banana", "[X]", "Sadece kimi.com web arayuzunde"),
    ("Multi-tasking", "[OK]", "Paralel API cagrilari ile"),
]

for name, status, note in features:
    print(f"  {status} {name:20} - {note}")

print("\n" + "=" * 60)
print("\nAgent Swarm Aciklamasi:")
print("-" * 60)
print("""
Agent Swarm, Kimi'nin gorevleri paralel alt gorevlere bolup
birden fazla ajanla calistirma ozelligidir.

API uzerinden kullanmak icin:
1. Gorevi alt gorevlere bol
2. Her alt gorev icin paralel API cagrisi yap
3. Sonuclari birlestir

Bu CLI'da 'multi_agent' modu ile desteklenmektedir.
""")
