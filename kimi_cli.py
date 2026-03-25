#!/usr/bin/env python3
"""
Kimi 2.5 CLI Agent - Claude Code benzeri terminal aracı
Moonshot AI Kimi K2.5 API kullanır
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

try:
    from openai import OpenAI
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
except ImportError:
    print("Paketler yukleniyor...")
    subprocess.run([sys.executable, "-m", "pip", "install", "openai>=1.0", "rich", "-q"], check=True)
    from openai import OpenAI
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text

console = Console()

CONFIG_DIR = Path.home() / ".kimi-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"

@dataclass
class Config:
    api_key: str = ""
    base_url: str = "https://api.moonshot.ai/v1"
    model: str = "kimi-k2.5"
    thinking_enabled: bool = True
    max_tokens: int = 16384
    temperature: float = 1.0

    @classmethod
    def load(cls) -> "Config":
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                valid = {f.name for f in cls.__dataclass_fields__.values()}
                return cls(**{k: v for k, v in data.items() if k in valid})
            except:
                pass
        return cls()

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(self.__dict__, indent=2), encoding="utf-8")


class FileManager:
    @staticmethod
    def read_file(path: str) -> str:
        try:
            p = Path(path)
            if not p.exists():
                return f"[HATA] Dosya yok: {path}"
            content = p.read_text(encoding="utf-8")
            return f"[OK] {path} ({len(content)} karakter)\n\n{content}"
        except Exception as e:
            return f"[HATA] {e}"

    @staticmethod
    def write_file(path: str, content: str) -> str:
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"[OK] {path} yazildi ({len(content)} karakter)"
        except Exception as e:
            return f"[HATA] {e}"

    @staticmethod
    def edit_file(path: str, old_text: str, new_text: str) -> str:
        try:
            p = Path(path)
            content = p.read_text(encoding="utf-8")
            if old_text not in content:
                return f"[HATA] Metin bulunamadi"
            p.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
            return f"[OK] {path} duzenlendi"
        except Exception as e:
            return f"[HATA] {e}"

    @staticmethod
    def list_files(path: str = ".", pattern: str = "*") -> str:
        try:
            files = list(Path(path).glob(pattern))[:50]
            if not files:
                return "[INFO] Dosya bulunamadi"
            result = []
            for f in sorted(files):
                t = "D" if f.is_dir() else "F"
                s = f.stat().st_size if f.is_file() else 0
                result.append(f"[{t}] {f.name:40} {s:>8} bytes")
            return "\n".join(result)
        except Exception as e:
            return f"[HATA] {e}"

    @staticmethod
    def search_files(pattern: str, path: str = ".", file_pattern: str = "*") -> str:
        try:
            results = []
            for f in Path(path).rglob(file_pattern):
                if f.is_file():
                    try:
                        for i, line in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                results.append(f"{f}:{i}: {line.strip()[:80]}")
                    except:
                        pass
            return "\n".join(results[:30]) if results else "[INFO] Bulunamadi"
        except Exception as e:
            return f"[HATA] {e}"


class ShellExecutor:
    @staticmethod
    def run(command: str, timeout: int = 120) -> str:
        try:
            r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout, cwd=os.getcwd())
            out = (r.stdout + r.stderr)[:5000]
            status = "OK" if r.returncode == 0 else f"HATA({r.returncode})"
            return f"[{status}]\n{out}"
        except subprocess.TimeoutExpired:
            return "[HATA] Timeout"
        except Exception as e:
            return f"[HATA] {e}"


TOOLS = [
    {"type": "function", "function": {"name": "read_file", "description": "Dosya oku", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Dosya yaz", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "edit_file", "description": "Dosya duzenle", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}}},
    {"type": "function", "function": {"name": "list_files", "description": "Dosyalari listele", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "pattern": {"type": "string"}}}}},
    {"type": "function", "function": {"name": "search_files", "description": "Dosyalarda ara", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}, "file_pattern": {"type": "string"}}, "required": ["pattern"]}}},
    {"type": "function", "function": {"name": "run_command", "description": "Shell komutu calistir", "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "timeout": {"type": "integer"}}, "required": ["command"]}}},
]


def execute_tool(name: str, args: dict) -> str:
    fm, sh = FileManager(), ShellExecutor()
    if name == "read_file": return fm.read_file(args["path"])
    if name == "write_file": return fm.write_file(args["path"], args["content"])
    if name == "edit_file": return fm.edit_file(args["path"], args["old_text"], args["new_text"])
    if name == "list_files": return fm.list_files(args.get("path", "."), args.get("pattern", "*"))
    if name == "search_files": return fm.search_files(args["pattern"], args.get("path", "."), args.get("file_pattern", "*"))
    if name == "run_command": return sh.run(args["command"], args.get("timeout", 120))
    return f"[HATA] Bilinmeyen: {name}"


class KimiAgent:
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        self.messages: List[Dict] = []
        self.cwd = os.getcwd()

    def _system_prompt(self) -> str:
        return f"""Sen Kimi, guclu bir AI kodlama asistanisin. Terminal uzerinden calisiyorsun.
Calisma dizini: {self.cwd}
Turkce yanit ver. Kisa ve oz ol. Kod yazarken aciklama ekle."""

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})
        messages = [{"role": "system", "content": self._system_prompt()}] + self.messages[-20:]

        try:
            # İlk istek
            console.print("[dim]● Istek gonderiliyor...[/dim]")

            # K2.5 için thinking mode kapalı (tool calling ile uyumsuz)
            extra = {}
            if "k2" in self.config.model:
                extra["extra_body"] = {"thinking": {"type": "disabled"}}

            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                **extra
            )

            msg = response.choices[0].message

            # Tool loop
            while msg.tool_calls:
                console.print(f"[cyan]● {len(msg.tool_calls)} tool calisiyor...[/cyan]")

                tool_results = []
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments) if tc.function.arguments else {}

                    # Tool bilgisi göster
                    args_str = ", ".join(f"{k}={repr(v)[:30]}" for k, v in args.items())
                    console.print(f"  [yellow]► {name}[/yellow]({args_str})")

                    # Çalıştır
                    result = execute_tool(name, args)

                    # Sonuç önizleme
                    preview = result[:150].replace('\n', ' ')
                    if len(result) > 150:
                        preview += "..."
                    console.print(f"    [dim]{preview}[/dim]")

                    tool_results.append({"role": "tool", "tool_call_id": tc.id, "content": result})

                # Mesajları güncelle
                self.messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in msg.tool_calls]
                })
                self.messages.extend(tool_results)

                # Devam et
                console.print("[dim]● Yanit aliniyor...[/dim]")
                messages = [{"role": "system", "content": self._system_prompt()}] + self.messages[-20:]
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    **extra
                )
                msg = response.choices[0].message

            # Son yanıt
            content = msg.content or ""
            self.messages.append({"role": "assistant", "content": content})
            return content

        except Exception as e:
            console.print(f"[red]API Hatasi: {e}[/red]")
            return ""

    def reset(self):
        self.messages = []


def setup_config() -> Config:
    console.print(Panel("[cyan]Kimi CLI - Ilk Kurulum[/cyan]"))
    api_key = Prompt.ask("Moonshot API Key")
    config = Config(api_key=api_key)
    config.save()
    console.print("[green]Kaydedildi![/green]")
    return config


def print_help():
    console.print(Panel("""[bold]Kimi CLI Komutlari[/bold]

[cyan]/help[/cyan]   - Yardim
[cyan]/clear[/cyan]  - Sohbeti temizle
[cyan]/config[/cyan] - Ayarlar
[cyan]/model[/cyan]  - Model degistir
[cyan]/shell[/cyan]  - Shell modu
[cyan]/swarm[/cyan]  - Agent Swarm
[cyan]/exit[/cyan]   - Cikis

[bold]Ornekler:[/bold]
> Bu dizindeki dosyalari listele
> index.html olustur, modern tasarim
> pip install flask komutunu calistir
""", title="Yardim"))


def shell_mode():
    console.print("[yellow]Shell modu (exit ile cik)[/yellow]")
    while True:
        try:
            cmd = Prompt.ask("[shell]$")
            if cmd.lower() in ("exit", "quit"): break
            console.print(ShellExecutor.run(cmd))
        except (EOFError, KeyboardInterrupt):
            break


def main():
    console.print(Panel.fit(
        "[bold magenta]Kimi 2.5 CLI Agent[/bold magenta]\n[dim]Moonshot AI K2.5 ile guclendirilmis terminal ajani[/dim]",
        border_style="magenta"
    ))

    config = Config.load()
    if not config.api_key:
        config = setup_config()

    agent = KimiAgent(config)
    console.print(f"[dim]Calisma dizini: {os.getcwd()}[/dim]")
    console.print("[dim]Yardim icin /help yazin[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]>[/bold cyan]")
            if not user_input.strip():
                continue

            # Komutlar
            if user_input.startswith("/"):
                cmd = user_input.lower().strip()

                if cmd == "/help":
                    print_help()
                elif cmd == "/clear":
                    agent.reset()
                    console.print("[green]Temizlendi[/green]")
                elif cmd == "/config":
                    t = Table(title="Ayarlar")
                    t.add_column("Ayar"); t.add_column("Deger")
                    t.add_row("Model", config.model)
                    t.add_row("API Key", config.api_key[:10] + "...")
                    t.add_row("Temperature", str(config.temperature))
                    console.print(t)
                elif cmd.startswith("/model"):
                    models = ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k", "kimi-k2.5", "kimi-k2-turbo-preview"]
                    console.print("[bold]Modeller:[/bold]")
                    for i, m in enumerate(models, 1):
                        mark = " [cyan](aktif)[/cyan]" if m == config.model else ""
                        console.print(f"  {i}. {m}{mark}")
                    c = Prompt.ask("Secim", default="4")
                    try:
                        config.model = models[int(c)-1]
                        config.temperature = 1.0 if "k2" in config.model else 0.7
                        config.save()
                        agent.config = config
                        console.print(f"[green]Model: {config.model}[/green]")
                    except:
                        pass
                elif cmd == "/shell":
                    shell_mode()
                elif cmd.startswith("/swarm"):
                    task = user_input[6:].strip() or Prompt.ask("Gorev")
                    if task:
                        try:
                            from agent_swarm import AgentSwarm
                            swarm = AgentSwarm(max_agents=5)
                            result = swarm.execute(task)
                            console.print(Markdown(result))
                        except Exception as e:
                            console.print(f"[red]Swarm hatasi: {e}[/red]")
                elif cmd in ("/exit", "/quit"):
                    console.print("[yellow]Gule gule![/yellow]")
                    break
                else:
                    console.print(f"[red]Bilinmeyen: {cmd}[/red]")
                continue

            # Normal mesaj
            response = agent.chat(user_input)
            if response:
                console.print()
                console.print(Markdown(response))
                console.print()

        except KeyboardInterrupt:
            console.print("\n[yellow]Ctrl+C. /exit ile cikin.[/yellow]")
        except EOFError:
            break


if __name__ == "__main__":
    import sys
    import webbrowser

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ["--version", "-v"]:
            print("Kimi CLI v1.0.0")
            sys.exit(0)
        elif cmd in ["--help", "-h"]:
            print("Kullanim: kimi [web|login|swarm|--help]")
            sys.exit(0)
        elif cmd == "web":
            webbrowser.open("http://localhost:3000")
            sys.exit(0)
        elif cmd == "login":
            config = Config.load()
            config.api_key = input("API Key: ").strip()
            config.save()
            print("Kaydedildi!")
            sys.exit(0)
        elif cmd == "swarm":
            task = " ".join(sys.argv[2:]) or input("Gorev: ")
            if task:
                from agent_swarm import AgentSwarm
                print(AgentSwarm(5).execute(task))
            sys.exit(0)
    main()
