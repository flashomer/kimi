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
import asyncio
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
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.live import Live
except ImportError:
    print("Gerekli paketler yükleniyor...")
    subprocess.run([sys.executable, "-m", "pip", "install", "openai>=1.0", "rich"], check=True)
    from openai import OpenAI
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.live import Live

console = Console()

# Konfigürasyon
CONFIG_DIR = Path.home() / ".kimi-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"

@dataclass
class Config:
    api_key: str = ""
    base_url: str = "https://api.moonshot.ai/v1"
    model: str = "kimi-k2.5"  # 256K context, thinking mode, coding optimized
    thinking_enabled: bool = True
    max_tokens: int = 16384
    temperature: float = 0.6

    @classmethod
    def load(cls) -> "Config":
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                # Eski config dosyalarıyla uyumluluk
                valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
                filtered_data = {k: v for k, v in data.items() if k in valid_fields}
                return cls(**filtered_data)
            except:
                pass
        return cls()

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(self.__dict__, indent=2), encoding="utf-8")


class FileManager:
    """Dosya işlemleri yöneticisi"""

    @staticmethod
    def read_file(path: str) -> str:
        """Dosya oku"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return f"[OK] {path} okundu ({len(content)} karakter)\n\n{content}"
        except Exception as e:
            return f"[HATA] Dosya okunamadı: {e}"

    @staticmethod
    def write_file(path: str, content: str) -> str:
        """Dosya yaz"""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"[OK] {path} yazıldı ({len(content)} karakter)"
        except Exception as e:
            return f"[HATA] Dosya yazılamadı: {e}"

    @staticmethod
    def edit_file(path: str, old_text: str, new_text: str) -> str:
        """Dosyada metin değiştir"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            if old_text not in content:
                return f"[HATA] '{old_text[:50]}...' metni dosyada bulunamadı"

            new_content = content.replace(old_text, new_text, 1)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return f"[OK] {path} düzenlendi"
        except Exception as e:
            return f"[HATA] Dosya düzenlenemedi: {e}"

    @staticmethod
    def list_files(path: str = ".", pattern: str = "*") -> str:
        """Dosyaları listele"""
        try:
            p = Path(path)
            files = list(p.glob(pattern))
            if not files:
                return f"[INFO] '{pattern}' ile eşleşen dosya bulunamadı"

            result = []
            for f in sorted(files)[:50]:
                stat = f.stat()
                size = stat.st_size
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                ftype = "D" if f.is_dir() else "F"
                result.append(f"[{ftype}] {f.name:40} {size:>10} bytes  {mtime}")

            return "\n".join(result)
        except Exception as e:
            return f"[HATA] Dosyalar listelenemedi: {e}"

    @staticmethod
    def search_in_files(pattern: str, path: str = ".", file_pattern: str = "*") -> str:
        """Dosyalarda arama yap"""
        try:
            p = Path(path)
            results = []
            for f in p.rglob(file_pattern):
                if f.is_file():
                    try:
                        content = f.read_text(encoding="utf-8")
                        for i, line in enumerate(content.split("\n"), 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                results.append(f"{f}:{i}: {line.strip()[:100]}")
                    except:
                        pass

            if not results:
                return f"[INFO] '{pattern}' bulunamadı"
            return "\n".join(results[:30])
        except Exception as e:
            return f"[HATA] Arama yapılamadı: {e}"


class ShellExecutor:
    """Kabuk komutu çalıştırıcı"""

    @staticmethod
    def run(command: str, timeout: int = 120) -> str:
        """Komut çalıştır"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            output = result.stdout + result.stderr
            status = "OK" if result.returncode == 0 else f"HATA (kod: {result.returncode})"
            return f"[{status}]\n{output[:5000]}"
        except subprocess.TimeoutExpired:
            return f"[HATA] Komut zaman aşımına uğradı ({timeout}s)"
        except Exception as e:
            return f"[HATA] Komut çalıştırılamadı: {e}"


# Tool tanımları - Kimi API için
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Bir dosyayı oku ve içeriğini döndür",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Okunacak dosyanın yolu"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Bir dosyaya içerik yaz (üzerine yazar)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Yazılacak dosyanın yolu"},
                    "content": {"type": "string", "description": "Yazılacak içerik"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Bir dosyada metin değiştir",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Düzenlenecek dosyanın yolu"},
                    "old_text": {"type": "string", "description": "Değiştirilecek metin"},
                    "new_text": {"type": "string", "description": "Yeni metin"}
                },
                "required": ["path", "old_text", "new_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Bir dizindeki dosyaları listele",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Dizin yolu", "default": "."},
                    "pattern": {"type": "string", "description": "Glob pattern (örn: *.py)", "default": "*"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Dosyalarda metin ara",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Aranacak regex pattern"},
                    "path": {"type": "string", "description": "Arama yapılacak dizin", "default": "."},
                    "file_pattern": {"type": "string", "description": "Dosya pattern (örn: *.py)", "default": "*"}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Kabuk komutu çalıştır",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Çalıştırılacak komut"},
                    "timeout": {"type": "integer", "description": "Zaman aşımı (saniye)", "default": 120}
                },
                "required": ["command"]
            }
        }
    }
]


def execute_tool(name: str, args: dict) -> str:
    """Tool çalıştır"""
    fm = FileManager()
    sh = ShellExecutor()

    if name == "read_file":
        return fm.read_file(args["path"])
    elif name == "write_file":
        return fm.write_file(args["path"], args["content"])
    elif name == "edit_file":
        return fm.edit_file(args["path"], args["old_text"], args["new_text"])
    elif name == "list_files":
        return fm.list_files(args.get("path", "."), args.get("pattern", "*"))
    elif name == "search_files":
        return fm.search_files(args["pattern"], args.get("path", "."), args.get("file_pattern", "*"))
    elif name == "run_command":
        return sh.run(args["command"], args.get("timeout", 120))
    else:
        return f"[HATA] Bilinmeyen tool: {name}"


class KimiAgent:
    """Kimi 2.5 CLI Agent"""

    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.messages: List[Dict[str, Any]] = []
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        cwd = os.getcwd()
        return f"""Sen Kimi, güçlü bir AI kodlama asistanısın. Terminal üzerinden çalışıyorsun.

## Yeteneklerin
- Dosya okuma, yazma ve düzenleme
- Kabuk komutları çalıştırma
- Kod analizi ve debugging
- Proje yapısı anlama

## Mevcut Çalışma Dizini
{cwd}

## Kurallar
1. Önce dosyaları oku, sonra değişiklik yap
2. Değişikliklerden önce kullanıcıya danış
3. Kısa ve öz yanıtlar ver
4. Hata durumunda detaylı açıklama yap
5. Güvenli olmayan komutları çalıştırma

## Format
- Kod blokları için ```dil kullan
- Dosya yollarını tam ver
- İşlem sonuçlarını raporla"""

    def chat(self, user_message: str) -> str:
        """Kullanıcı mesajını işle"""
        self.messages.append({"role": "user", "content": user_message})

        # İlk mesaj için system prompt ekle
        messages_to_send = [{"role": "system", "content": self.system_prompt}] + self.messages

        try:
            # API çağrısı
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages_to_send,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )

            assistant_message = response.choices[0].message

            # Tool çağrısı varsa işle
            while assistant_message.tool_calls:
                # Tool çağrılarını işle
                tool_results = []
                for tool_call in assistant_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    console.print(f"[dim]> {func_name}({', '.join(f'{k}={repr(v)[:30]}' for k, v in func_args.items())})[/dim]")

                    result = execute_tool(func_name, func_args)
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })

                    # Sonucu göster (kısa)
                    preview = result[:200] + "..." if len(result) > 200 else result
                    console.print(f"[dim]{preview}[/dim]")

                # Mesajları güncelle
                self.messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })
                self.messages.extend(tool_results)

                # Devam et
                messages_to_send = [{"role": "system", "content": self.system_prompt}] + self.messages
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages_to_send,
                    tools=TOOLS,
                    tool_choice="auto",
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
                assistant_message = response.choices[0].message

            # Son yanıtı kaydet
            final_content = assistant_message.content or ""
            self.messages.append({"role": "assistant", "content": final_content})

            return final_content

        except Exception as e:
            error_msg = f"API Hatası: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg

    def reset(self):
        """Konuşmayı sıfırla"""
        self.messages = []


def setup_config() -> Config:
    """İlk kurulum"""
    console.print(Panel.fit(
        "[bold cyan]Kimi 2.5 CLI Agent[/bold cyan]\n"
        "İlk kurulum gerekiyor",
        title="Hoş Geldiniz"
    ))

    api_key = Prompt.ask("Moonshot API Key'inizi girin")

    config = Config(api_key=api_key)
    config.save()

    console.print("[green]Konfigürasyon kaydedildi![/green]")
    return config


def print_help():
    """Yardım mesajı"""
    help_text = """
[bold]Kimi 2.5 CLI Agent - Komutlar[/bold]

[cyan]/help[/cyan]     - Bu yardım mesajını göster
[cyan]/clear[/cyan]    - Konuşma geçmişini temizle
[cyan]/config[/cyan]   - Ayarları göster/değiştir
[cyan]/shell[/cyan]    - Shell moduna geç (Ctrl+D ile çık)
[cyan]/swarm[/cyan]    - Agent Swarm modu (paralel ajanlar)
[cyan]/model[/cyan]    - Model değiştir
[cyan]/exit[/cyan]     - Çıkış

[bold]Modeller:[/bold]
- moonshot-v1-8k/32k/128k - Hızlı, stabil
- kimi-k2.5               - 256K context, thinking
- kimi-k2-turbo-preview   - Hızlı K2

[bold]Örnekler:[/bold]
- "Bu dizindeki Python dosyalarını listele"
- "main.py dosyasını oku ve özetle"
- "Yeni bir Flask uygulaması oluştur"
- /swarm Kapsamlı bir e-ticaret sitesi planla
"""
    console.print(Panel(help_text, title="Yardım"))


def shell_mode():
    """Doğrudan shell modu"""
    console.print("[yellow]Shell modu aktif. Ctrl+D veya 'exit' ile çık.[/yellow]")
    while True:
        try:
            cmd = Prompt.ask("[shell]$")
            if cmd.lower() in ("exit", "quit"):
                break
            result = ShellExecutor.run(cmd)
            console.print(result)
        except (EOFError, KeyboardInterrupt):
            break
    console.print("[yellow]Shell modundan çıkıldı.[/yellow]")


def main():
    """Ana fonksiyon"""
    console.print(Panel.fit(
        "[bold magenta]Kimi 2.5 CLI Agent[/bold magenta]\n"
        "[dim]Moonshot AI K2.5 ile güçlendirilmiş terminal ajanı[/dim]",
        border_style="magenta"
    ))

    # Konfigürasyon yükle
    config = Config.load()
    if not config.api_key:
        config = setup_config()

    # Agent başlat
    agent = KimiAgent(config)
    console.print(f"[dim]Çalışma dizini: {os.getcwd()}[/dim]")
    console.print("[dim]Yardım için /help yazın[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]>[/bold cyan]")

            if not user_input.strip():
                continue

            # Özel komutlar
            if user_input.startswith("/"):
                cmd = user_input.lower().strip()

                if cmd == "/help":
                    print_help()
                elif cmd == "/clear":
                    agent.reset()
                    console.print("[green]Konuşma temizlendi.[/green]")
                elif cmd == "/config":
                    table = Table(title="Ayarlar")
                    table.add_column("Ayar")
                    table.add_column("Değer")
                    table.add_row("Model", config.model)
                    table.add_row("Base URL", config.base_url)
                    table.add_row("Max Tokens", str(config.max_tokens))
                    table.add_row("API Key", config.api_key[:8] + "..." if config.api_key else "Yok")
                    console.print(table)
                elif cmd == "/shell":
                    shell_mode()
                elif cmd.startswith("/swarm"):
                    # Agent Swarm modu
                    task = user_input[6:].strip()
                    if not task:
                        task = Prompt.ask("[cyan]Swarm görevi[/cyan]")
                    if task:
                        try:
                            from agent_swarm import AgentSwarm
                            swarm = AgentSwarm(max_agents=5)
                            with console.status("[bold magenta]Agent Swarm çalışıyor..."):
                                result = swarm.execute(task)
                            console.print(Markdown(result))
                        except ImportError:
                            console.print("[red]agent_swarm.py bulunamadı![/red]")
                        except Exception as e:
                            console.print(f"[red]Swarm hatası: {e}[/red]")
                elif cmd.startswith("/model"):
                    # Model değiştir
                    models = ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k",
                              "kimi-k2.5", "kimi-k2-turbo-preview", "kimi-k2-thinking-turbo"]
                    console.print("[bold]Mevcut modeller:[/bold]")
                    for i, m in enumerate(models, 1):
                        marker = " [cyan](aktif)[/cyan]" if m == config.model else ""
                        console.print(f"  {i}. {m}{marker}")
                    choice = Prompt.ask("Model numarası", default="1")
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(models):
                            config.model = models[idx]
                            config.save()
                            agent.config = config
                            console.print(f"[green]Model değiştirildi: {config.model}[/green]")
                    except:
                        console.print("[red]Geçersiz seçim[/red]")
                elif cmd in ("/exit", "/quit"):
                    console.print("[yellow]Güle güle![/yellow]")
                    break
                else:
                    console.print(f"[red]Bilinmeyen komut: {cmd}[/red]")
                continue

            # Normal mesaj - AI'a gönder
            with console.status("[bold green]Düşünüyor..."):
                response = agent.chat(user_input)

            # Yanıtı göster
            console.print()
            console.print(Markdown(response))
            console.print()

        except KeyboardInterrupt:
            console.print("\n[yellow]Ctrl+C algılandı. /exit ile çıkabilirsiniz.[/yellow]")
        except EOFError:
            break


if __name__ == "__main__":
    import sys
    import webbrowser

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd in ["--version", "-v"]:
            print("Kimi CLI v1.0.0 - Moonshot AI K2.5")
            sys.exit(0)

        elif cmd in ["--help", "-h"]:
            print("""
Kimi 2.5 CLI Agent
==================
Kullanım: kimi [komut] [seçenekler]

Komutlar:
  (boş)            CLI'yı başlat
  web              Web arayüzünü aç
  login            API yapılandırması
  swarm <görev>    Agent Swarm ile çalıştır

Seçenekler:
  -v, --version    Versiyon göster
  -h, --help       Bu yardımı göster

CLI Komutları:
  /help            Yardım
  /clear           Sohbeti temizle
  /config          Ayarları göster
  /shell           Shell moduna geç
  /swarm           Agent Swarm modu
  /model           Model değiştir
  /exit            Çıkış

Örnekler:
  kimi                  # CLI başlat
  kimi web              # Web UI aç
  kimi swarm "plan yap" # Paralel ajan çalıştır
""")
            sys.exit(0)

        elif cmd == "web":
            print("Web arayüzü açılıyor...")
            print("Frontend: http://localhost:3000")
            print("Backend:  http://localhost:8000")
            webbrowser.open("http://localhost:3000")
            sys.exit(0)

        elif cmd == "login":
            config = Config.load()
            api_key = input("Moonshot API Key: ").strip()
            if api_key:
                config.api_key = api_key
                config.save()
                print("API Key kaydedildi!")
            sys.exit(0)

        elif cmd == "swarm":
            task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else input("Görev: ")
            if task:
                try:
                    from agent_swarm import AgentSwarm
                    swarm = AgentSwarm(max_agents=5)
                    result = swarm.execute(task)
                    print("\n" + result)
                except Exception as e:
                    print(f"Hata: {e}")
            sys.exit(0)

    main()
