#!/usr/bin/env python3
"""Hızlı CLI testi - tool calling ile"""

import json
from openai import OpenAI

API_KEY = "sk-V9fu4RZdxLADmp9q9G7VgHGCdGxMwAFFeEX2cuF4VkuUybXc"
BASE_URL = "https://api.moonshot.ai/v1"

# Basit tool tanımı
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Mevcut saat bilgisini döndürür",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Matematiksel işlem yapar",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Hesaplanacak ifade"}
                },
                "required": ["expression"]
            }
        }
    }
]

def execute_tool(name, args):
    if name == "get_current_time":
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif name == "calculate":
        try:
            result = eval(args.get("expression", "0"))
            return str(result)
        except:
            return "Hesaplanamadı"
    return "Bilinmeyen tool"

print("=" * 50)
print("Kimi Tool Calling Testi")
print("=" * 50)

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

messages = [
    {"role": "system", "content": "Sen yardımcı bir asistansın. Türkçe yanıt ver."},
    {"role": "user", "content": "25 * 4 kaç eder? Hesapla."}
]

print("\n[1] İlk istek gönderiliyor...")

response = client.chat.completions.create(
    model="moonshot-v1-128k",
    messages=messages,
    tools=TOOLS,
    tool_choice="auto",
    max_tokens=1000,
    temperature=0.7
)

msg = response.choices[0].message
print(f"[2] Yanıt alındı. Tool calls: {msg.tool_calls is not None}")

if msg.tool_calls:
    print("\n[3] Tool çağrıları işleniyor...")
    for tc in msg.tool_calls:
        func_name = tc.function.name
        func_args = json.loads(tc.function.arguments) if tc.function.arguments else {}
        print(f"    > {func_name}({func_args})")

        result = execute_tool(func_name, func_args)
        print(f"    < {result}")

        # Tool sonucunu ekle
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": func_name, "arguments": tc.function.arguments}}]
        })
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": result
        })

    # Son yanıt
    print("\n[4] Son yanıt alınıyor...")
    response = client.chat.completions.create(
        model="moonshot-v1-128k",
        messages=messages,
        max_tokens=1000,
        temperature=0.7
    )
    final = response.choices[0].message.content
    print(f"\n[Kimi]: {final}")
else:
    print(f"\n[Kimi]: {msg.content}")

print("\n" + "=" * 50)
print("TEST TAMAMLANDI!")
print("=" * 50)
