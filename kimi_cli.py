#!/usr/bin/env python3
"""Kimi K2.5 CLI - Claude Code Style"""

import os, sys, json, subprocess, difflib
from pathlib import Path
from dataclasses import dataclass

if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from openai import OpenAI
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.table import Table
    from rich.text import Text
    from rich import box
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "openai>=1.0", "rich", "-q"])
    from openai import OpenAI
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.table import Table
    from rich.text import Text
    from rich import box

console = Console(force_terminal=True, color_system="auto")
CONFIG_FILE = Path.home() / ".kimi-cli" / "config.json"

# Renkler
COLORS = {
    "tool": "bold cyan",
    "success": "bold green",
    "error": "bold red",
    "warning": "bold yellow",
    "info": "bold blue",
    "dim": "dim white",
    "file": "bold magenta",
}

@dataclass
class Config:
    api_key: str = ""
    base_url: str = "https://api.moonshot.ai/v1"
    model: str = "kimi-k2.5"
    max_tokens: int = 16384

    @classmethod
    def load(cls):
        if CONFIG_FILE.exists():
            try:
                d = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
                return cls(**{k:v for k,v in d.items() if hasattr(cls, k)})
            except: pass
        return cls()

    def save(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(self.__dict__, indent=2), encoding='utf-8')


def get_lang(path):
    ext = Path(path).suffix.lower()
    return {
        '.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.jsx': 'jsx', '.tsx': 'tsx',
        '.html': 'html', '.htm': 'html', '.css': 'css', '.scss': 'scss', '.less': 'less',
        '.json': 'json', '.xml': 'xml', '.yaml': 'yaml', '.yml': 'yaml',
        '.md': 'markdown', '.sql': 'sql', '.sh': 'bash', '.bat': 'batch',
        '.php': 'php', '.rb': 'ruby', '.go': 'go', '.rs': 'rust',
        '.java': 'java', '.c': 'c', '.cpp': 'cpp', '.h': 'c', '.cs': 'csharp',
        '.vue': 'vue', '.svelte': 'svelte',
    }.get(ext, 'text')


def show_file_content(content, path, is_new=True):
    """Dosya içeriğini Claude Code tarzı göster"""
    lang = get_lang(path)

    # Başlık
    icon = "+" if is_new else "~"
    color = "green" if is_new else "yellow"
    title = f"[bold {color}]{icon} {path}[/bold {color}]"

    # Syntax highlighting
    syntax = Syntax(
        content,
        lang,
        theme="monokai",
        line_numbers=True,
        word_wrap=True,
        indent_guides=True,
        background_color="default"
    )

    console.print()
    console.print(Panel(
        syntax,
        title=title,
        title_align="left",
        border_style=color,
        box=box.ROUNDED,
        padding=(0, 1)
    ))


def show_diff(old_content, new_content, path):
    """Değişiklikleri Claude Code diff tarzında göster"""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    diff = list(difflib.unified_diff(old_lines, new_lines, fromfile=path, tofile=path, lineterm=''))

    if not diff:
        console.print(f"[dim]Degisiklik yok[/dim]")
        return

    console.print()
    console.print(f"[bold yellow]~ {path}[/bold yellow]")
    console.print()

    for line in diff:
        line = line.rstrip('\n')
        if line.startswith('+++') or line.startswith('---'):
            console.print(f"[bold white]{line}[/bold white]")
        elif line.startswith('@@'):
            console.print(f"[cyan]{line}[/cyan]")
        elif line.startswith('+'):
            # Yeşil arka plan
            text = Text(line)
            text.stylize("white on dark_green")
            console.print(text)
        elif line.startswith('-'):
            # Kırmızı arka plan
            text = Text(line)
            text.stylize("white on dark_red")
            console.print(text)
        else:
            console.print(f"[dim]{line}[/dim]")

    console.print()


# ==================== TOOLS ====================

def tool_read_file(path):
    """Dosya oku ve göster"""
    console.print(f"\n[{COLORS['info']}]Reading {path}...[/{COLORS['info']}]")

    try:
        p = Path(path)
        if not p.exists():
            console.print(f"[{COLORS['error']}]File not found: {path}[/{COLORS['error']}]")
            return f"[ERROR] File not found: {path}"

        content = p.read_text(encoding='utf-8')
        show_file_content(content, path, is_new=False)
        return content

    except Exception as e:
        console.print(f"[{COLORS['error']}]Error: {e}[/{COLORS['error']}]")
        return f"[ERROR] {e}"


def tool_write_file(path, content):
    """Dosya yaz ve göster"""
    try:
        p = Path(path)
        is_new = not p.exists()
        old_content = ""

        if p.exists():
            old_content = p.read_text(encoding='utf-8')

        # Yaz
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')

        # Göster
        if is_new:
            console.print(f"\n[{COLORS['success']}]Created {path}[/{COLORS['success']}]")
            show_file_content(content, path, is_new=True)
        else:
            console.print(f"\n[{COLORS['warning']}]Updated {path}[/{COLORS['warning']}]")
            show_diff(old_content, content, path)

        return f"[OK] Wrote {len(content)} bytes to {path}"

    except Exception as e:
        console.print(f"[{COLORS['error']}]Write error: {e}[/{COLORS['error']}]")
        return f"[ERROR] {e}"


def tool_edit_file(path, old_text, new_text):
    """Dosyada değişiklik yap ve diff göster"""
    try:
        p = Path(path)
        if not p.exists():
            console.print(f"[{COLORS['error']}]File not found: {path}[/{COLORS['error']}]")
            return f"[ERROR] File not found"

        old_content = p.read_text(encoding='utf-8')

        if old_text not in old_content:
            console.print(f"[{COLORS['error']}]Text not found in file[/{COLORS['error']}]")
            return f"[ERROR] Text not found"

        new_content = old_content.replace(old_text, new_text, 1)
        p.write_text(new_content, encoding='utf-8')

        console.print(f"\n[{COLORS['warning']}]Edited {path}[/{COLORS['warning']}]")
        show_diff(old_content, new_content, path)

        return f"[OK] Edited {path}"

    except Exception as e:
        console.print(f"[{COLORS['error']}]Edit error: {e}[/{COLORS['error']}]")
        return f"[ERROR] {e}"


def tool_list_files(path=".", pattern="*"):
    """Dosyaları listele"""
    try:
        p = Path(path)
        files = sorted(p.glob(pattern))[:50]

        if not files:
            console.print(f"[{COLORS['dim']}]No files found[/{COLORS['dim']}]")
            return "[EMPTY]"

        console.print()
        table = Table(title=f"[bold]{path}/{pattern}[/bold]", box=box.SIMPLE, show_header=True)
        table.add_column("Type", style="cyan", width=6)
        table.add_column("Name", style="white")
        table.add_column("Size", justify="right", style="dim")

        result = []
        for f in files:
            ftype = "DIR" if f.is_dir() else "FILE"
            size = f"{f.stat().st_size:,}" if f.is_file() else "-"
            table.add_row(ftype, f.name, size)
            result.append(f.name)

        console.print(table)
        return "\n".join(result)

    except Exception as e:
        console.print(f"[{COLORS['error']}]List error: {e}[/{COLORS['error']}]")
        return f"[ERROR] {e}"


def tool_run_cmd(cmd):
    """Komut çalıştır"""
    console.print(f"\n[{COLORS['file']}]$ {cmd}[/{COLORS['file']}]")

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=120, cwd=os.getcwd()
        )

        output = result.stdout + result.stderr

        if result.returncode == 0:
            if output.strip():
                console.print(f"[green]{output[:2000]}[/green]")
            else:
                console.print(f"[{COLORS['success']}]Command completed[/{COLORS['success']}]")
        else:
            console.print(f"[{COLORS['error']}]{output[:2000]}[/{COLORS['error']}]")

        return output[:3000] or "[OK]"

    except subprocess.TimeoutExpired:
        console.print(f"[{COLORS['error']}]Command timed out[/{COLORS['error']}]")
        return "[ERROR] Timeout"
    except Exception as e:
        console.print(f"[{COLORS['error']}]Command error: {e}[/{COLORS['error']}]")
        return f"[ERROR] {e}"


# Tool definitions
TOOLS = [
    {"type":"function","function":{"name":"read_file","description":"Read a file","parameters":{"type":"object","properties":{"path":{"type":"string","description":"File path"}},"required":["path"]}}},
    {"type":"function","function":{"name":"write_file","description":"Write/create a file","parameters":{"type":"object","properties":{"path":{"type":"string","description":"File path"},"content":{"type":"string","description":"File content"}},"required":["path","content"]}}},
    {"type":"function","function":{"name":"edit_file","description":"Edit a file by replacing text","parameters":{"type":"object","properties":{"path":{"type":"string","description":"File path"},"old_text":{"type":"string","description":"Text to replace"},"new_text":{"type":"string","description":"New text"}},"required":["path","old_text","new_text"]}}},
    {"type":"function","function":{"name":"list_files","description":"List files in directory","parameters":{"type":"object","properties":{"path":{"type":"string","description":"Directory path"},"pattern":{"type":"string","description":"Glob pattern"}}}}},
    {"type":"function","function":{"name":"run_cmd","description":"Run shell command","parameters":{"type":"object","properties":{"cmd":{"type":"string","description":"Command to run"}},"required":["cmd"]}}},
]


def execute_tool(name, args):
    """Tool çalıştır"""
    # Tool başlığı
    args_preview = {k: (v[:50]+"..." if isinstance(v,str) and len(v)>50 else v) for k,v in args.items() if k != 'content'}
    if 'content' in args:
        args_preview['content'] = f"<{len(args['content'])} chars>"

    console.print(f"\n[{COLORS['tool']}]▶ {name}[/{COLORS['tool']}] [dim]{args_preview}[/dim]")

    if name == "read_file":
        return tool_read_file(args.get("path", ""))
    elif name == "write_file":
        return tool_write_file(args.get("path", ""), args.get("content", ""))
    elif name == "edit_file":
        return tool_edit_file(args.get("path", ""), args.get("old_text", ""), args.get("new_text", ""))
    elif name == "list_files":
        return tool_list_files(args.get("path", "."), args.get("pattern", "*"))
    elif name == "run_cmd":
        return tool_run_cmd(args.get("cmd", ""))

    return "[ERROR] Unknown tool"


class KimiAgent:
    def __init__(self, cfg):
        self.cfg = cfg
        self.client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)
        self.messages = []

    def chat(self, user_input):
        self.messages.append({"role": "user", "content": user_input})

        system = f"""Sen Kimi, profesyonel bir yazilim gelistirme asistanisin.
Calisma dizini: {os.getcwd()}

Kurallar:
- Turkce yanit ver
- Dosya olusturmak/duzenlemek icin MUTLAKA tool kullan
- Kod yazarken modern ve temiz kod yaz
- Her dosyayi ayri tool call ile olustur"""

        msgs = [{"role": "system", "content": system}] + self.messages[-12:]
        extra = {"extra_body": {"thinking": {"type": "disabled"}}} if "k2" in self.cfg.model else {}

        try:
            console.print(f"\n[bold cyan]◆ Kimi[/bold cyan] [dim]({self.cfg.model})[/dim]")

            response = self.client.chat.completions.create(
                model=self.cfg.model,
                messages=msgs,
                tools=TOOLS,
                max_tokens=self.cfg.max_tokens,
                temperature=0.6,
                **extra
            )

            msg = response.choices[0].message
            iterations = 0

            while msg.tool_calls and iterations < 20:
                iterations += 1

                tool_results = []
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                    result = execute_tool(tc.function.name, args)
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result
                    })

                # Mesajları güncelle
                self.messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [
                        {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                        for tc in msg.tool_calls
                    ]
                })
                self.messages.extend(tool_results)

                # Devam et
                msgs = [{"role": "system", "content": system}] + self.messages[-12:]
                response = self.client.chat.completions.create(
                    model=self.cfg.model,
                    messages=msgs,
                    tools=TOOLS,
                    max_tokens=self.cfg.max_tokens,
                    temperature=0.6,
                    **extra
                )
                msg = response.choices[0].message

            content = msg.content or ""
            self.messages.append({"role": "assistant", "content": content})
            return content

        except Exception as e:
            console.print(f"\n[{COLORS['error']}]API Error: {e}[/{COLORS['error']}]")
            return ""

    def clear(self):
        self.messages = []


def main():
    # Banner
    console.print()
    console.print(Panel.fit(
        "[bold magenta]Kimi K2.5 CLI[/bold magenta]\n"
        "[dim]Claude Code Style Terminal Agent[/dim]",
        border_style="magenta",
        padding=(0, 2)
    ))

    cfg = Config.load()

    if not cfg.api_key:
        console.print(f"\n[{COLORS['warning']}]API Key gerekli[/{COLORS['warning']}]")
        cfg.api_key = Prompt.ask("Moonshot API Key")
        cfg.save()
        console.print(f"[{COLORS['success']}]Kaydedildi![/{COLORS['success']}]")

    agent = KimiAgent(cfg)

    console.print(f"\n[dim]Dizin: {os.getcwd()}[/dim]")
    console.print(f"[dim]Model: {cfg.model}[/dim]")
    console.print(f"[dim]Yardim: /help[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]>[/bold cyan]")

            if not user_input.strip():
                continue

            # Komutlar
            if user_input.startswith("/"):
                cmd = user_input.lower().strip()

                if cmd == "/help":
                    console.print(Panel(
                        "[cyan]/help[/cyan]   Yardim\n"
                        "[cyan]/clear[/cyan]  Sohbeti temizle\n"
                        "[cyan]/model[/cyan]  Model degistir\n"
                        "[cyan]/exit[/cyan]   Cikis",
                        title="[bold]Komutlar[/bold]",
                        border_style="cyan"
                    ))

                elif cmd == "/clear":
                    agent.clear()
                    console.print(f"[{COLORS['success']}]Sohbet temizlendi[/{COLORS['success']}]")

                elif cmd.startswith("/model"):
                    models = [
                        ("moonshot-v1-8k", "8K context, hizli"),
                        ("moonshot-v1-32k", "32K context"),
                        ("moonshot-v1-128k", "128K context"),
                        ("kimi-k2.5", "256K context, en guclu"),
                        ("kimi-k2-turbo-preview", "Hizli K2"),
                    ]
                    console.print("\n[bold]Modeller:[/bold]\n")
                    for i, (m, desc) in enumerate(models, 1):
                        active = " [cyan]◀ aktif[/cyan]" if m == cfg.model else ""
                        console.print(f"  {i}. [bold]{m}[/bold] [dim]- {desc}[/dim]{active}")

                    choice = Prompt.ask("\nSecim", default="4")
                    try:
                        cfg.model = models[int(choice)-1][0]
                        cfg.save()
                        console.print(f"\n[{COLORS['success']}]Model: {cfg.model}[/{COLORS['success']}]")
                    except:
                        console.print(f"[{COLORS['error']}]Gecersiz secim[/{COLORS['error']}]")

                elif cmd in ["/exit", "/quit", "/q"]:
                    console.print(f"\n[{COLORS['warning']}]Gule gule![/{COLORS['warning']}]\n")
                    break

                else:
                    console.print(f"[{COLORS['error']}]Bilinmeyen komut: {cmd}[/{COLORS['error']}]")

                continue

            # Chat
            response = agent.chat(user_input)

            if response:
                console.print()
                console.print(Markdown(response))
                console.print()

        except KeyboardInterrupt:
            console.print()
        except EOFError:
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["-v", "--version"]:
            print("Kimi CLI v1.0.0")
        elif arg in ["-h", "--help"]:
            print("Usage: kimi [command]\n\nCommands:\n  web    Open web UI\n  login  Set API key")
        elif arg == "web":
            import webbrowser
            webbrowser.open("http://localhost:3000")
        elif arg == "login":
            cfg = Config.load()
            cfg.api_key = input("API Key: ").strip()
            cfg.save()
            print("Saved!")
        sys.exit(0)

    main()
