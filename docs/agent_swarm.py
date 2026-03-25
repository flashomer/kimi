#!/usr/bin/env python3
"""
Kimi Agent Swarm - Paralel Çoklu Ajan Sistemi
Büyük görevleri alt görevlere böler ve paralel çalıştırır
"""

import asyncio
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI

API_KEY = "sk-V9fu4RZdxLADmp9q9G7VgHGCdGxMwAFFeEX2cuF4VkuUybXc"
BASE_URL = "https://api.moonshot.ai/v1"


@dataclass
class SubTask:
    """Alt görev tanımı"""
    id: int
    description: str
    agent_type: str  # "researcher", "coder", "writer", "analyzer"
    status: str = "pending"
    result: str = ""


class AgentSwarm:
    """Paralel ajan yöneticisi"""

    def __init__(self, max_agents: int = 5):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.max_agents = max_agents
        self.subtasks: List[SubTask] = []

    def decompose_task(self, main_task: str) -> List[SubTask]:
        """Ana görevi alt görevlere böl"""
        print(f"[Swarm] Görev ayrıştırılıyor: {main_task[:50]}...")

        response = self.client.chat.completions.create(
            model="moonshot-v1-32k",
            messages=[
                {
                    "role": "system",
                    "content": """Sen bir görev yöneticisisin. Verilen görevi paralel çalıştırılabilecek alt görevlere böl.
Her alt görev için şu formatı kullan:
{"subtasks": [
  {"id": 1, "description": "alt görev açıklaması", "agent_type": "researcher|coder|writer|analyzer"},
  ...
]}

Agent tipleri:
- researcher: Araştırma, bilgi toplama
- coder: Kod yazma, debugging
- writer: Döküman, rapor yazma
- analyzer: Analiz, değerlendirme

Maksimum 5 alt görev oluştur. JSON formatında yanıt ver."""
                },
                {"role": "user", "content": f"Görevi alt görevlere böl: {main_task}"}
            ],
            max_tokens=1000,
            temperature=0.3
        )

        try:
            content = response.choices[0].message.content
            # JSON'u parse et
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(content[start:end])
                self.subtasks = [
                    SubTask(
                        id=st["id"],
                        description=st["description"],
                        agent_type=st.get("agent_type", "analyzer")
                    )
                    for st in data.get("subtasks", [])
                ]
        except Exception as e:
            print(f"[Swarm] Parse hatası: {e}")
            # Fallback: tek görev
            self.subtasks = [SubTask(id=1, description=main_task, agent_type="analyzer")]

        print(f"[Swarm] {len(self.subtasks)} alt görev oluşturuldu")
        return self.subtasks

    def _get_agent_prompt(self, agent_type: str) -> str:
        """Ajan tipine göre system prompt"""
        prompts = {
            "researcher": "Sen bir araştırmacısın. Bilgi topla, kaynak bul, detaylı araştır.",
            "coder": "Sen bir yazılım geliştiricisisin. Kod yaz, hataları düzelt, optimize et.",
            "writer": "Sen bir yazarsın. Açık, anlaşılır ve profesyonel içerik üret.",
            "analyzer": "Sen bir analistsin. Verileri analiz et, sonuçları değerlendir, öneriler sun."
        }
        return prompts.get(agent_type, prompts["analyzer"])

    def _run_agent(self, subtask: SubTask) -> SubTask:
        """Tek bir ajanı çalıştır"""
        print(f"  [Agent-{subtask.id}] Başlıyor: {subtask.description[:40]}...")
        subtask.status = "running"

        try:
            response = self.client.chat.completions.create(
                model="moonshot-v1-32k",
                messages=[
                    {"role": "system", "content": self._get_agent_prompt(subtask.agent_type)},
                    {"role": "user", "content": subtask.description}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            subtask.result = response.choices[0].message.content or ""
            subtask.status = "completed"
            print(f"  [Agent-{subtask.id}] Tamamlandı ({len(subtask.result)} karakter)")
        except Exception as e:
            subtask.result = f"Hata: {str(e)}"
            subtask.status = "failed"
            print(f"  [Agent-{subtask.id}] Hata: {e}")

        return subtask

    def run_parallel(self) -> List[SubTask]:
        """Tüm alt görevleri paralel çalıştır"""
        print(f"\n[Swarm] {len(self.subtasks)} ajan paralel başlatılıyor...")

        with ThreadPoolExecutor(max_workers=self.max_agents) as executor:
            results = list(executor.map(self._run_agent, self.subtasks))

        self.subtasks = results
        return results

    def synthesize_results(self, main_task: str) -> str:
        """Sonuçları birleştir"""
        print("\n[Swarm] Sonuçlar birleştiriliyor...")

        # Alt görev sonuçlarını topla
        results_text = "\n\n".join([
            f"## Alt Görev {st.id}: {st.description}\n{st.result}"
            for st in self.subtasks if st.status == "completed"
        ])

        # Son sentez
        response = self.client.chat.completions.create(
            model="moonshot-v1-32k",
            messages=[
                {
                    "role": "system",
                    "content": "Sen bir koordinatörsün. Alt görev sonuçlarını analiz edip kapsamlı bir özet oluştur."
                },
                {
                    "role": "user",
                    "content": f"""Ana Görev: {main_task}

Alt Görev Sonuçları:
{results_text}

Tüm sonuçları birleştirip kapsamlı bir yanıt oluştur."""
                }
            ],
            max_tokens=4000,
            temperature=0.5
        )

        return response.choices[0].message.content or ""

    def execute(self, task: str) -> str:
        """Tam swarm akışı"""
        print("=" * 60)
        print("KIMI AGENT SWARM")
        print("=" * 60)

        # 1. Görevi böl
        self.decompose_task(task)

        # 2. Paralel çalıştır
        self.run_parallel()

        # 3. Sonuçları birleştir
        final_result = self.synthesize_results(task)

        print("\n" + "=" * 60)
        print("SWARM TAMAMLANDI")
        print("=" * 60)

        return final_result


def main():
    """Test"""
    import sys

    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("Görev girin: ")

    swarm = AgentSwarm(max_agents=5)
    result = swarm.execute(task)

    print("\n" + "=" * 60)
    print("SONUÇ:")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
