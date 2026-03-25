#!/usr/bin/env python3
"""Kimi K2.5 CLI Test"""

from openai import OpenAI

client = OpenAI(
    api_key="sk-V9fu4RZdxLADmp9q9G7VgHGCdGxMwAFFeEX2cuF4VkuUybXc",
    base_url="https://api.moonshot.ai/v1"
)

print("Kimi K2.5 Test")
print("=" * 40)

# Tool tanımı
tools = [{
    "type": "function",
    "function": {
        "name": "write_code",
        "description": "Kod yaz ve dosyaya kaydet",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "code": {"type": "string"}
            },
            "required": ["filename", "code"]
        }
    }
}]

response = client.chat.completions.create(
    model="kimi-k2.5",
    messages=[
        {"role": "system", "content": "Sen bir kod asistanisin. Turkce yanit ver."},
        {"role": "user", "content": "Basit bir Python hello world kodu yaz"}
    ],
    tools=tools,
    max_tokens=2000
)

msg = response.choices[0].message

if msg.tool_calls:
    print("[Tool Call]")
    for tc in msg.tool_calls:
        print(f"  {tc.function.name}: {tc.function.arguments[:100]}...")
else:
    print("[Yanit]")
    print(msg.content[:500] if msg.content else "(bos)")

print(f"\n[Model]: {response.model}")
print(f"[Tokens]: {response.usage.total_tokens}")
