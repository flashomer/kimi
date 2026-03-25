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

    def stream_response(self, msgs, system, status_msg="Düşünüyor..."):
        """Streaming ile yanıt al ve gerçek zamanlı göster"""
        from rich.status import Status

        extra = {"extra_body": {"thinking": {"type": "disabled"}}} if "k2" in self.cfg.model else {}

        content = ""
        tool_calls_data = {}
        current_tool_id = None

        with Status(f"[cyan]{status_msg}[/cyan]", console=console, spinner="dots") as status:
            try:
                # Streaming request
                stream = self.client.chat.completions.create(
                    model=self.cfg.model,
                    messages=msgs,
                    tools=TOOLS,
                    max_tokens=self.cfg.max_tokens,
                    temperature=0.6,
                    stream=True,
                    **extra
                )

                first_content = False

                for chunk in stream:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if not delta:
                        continue

                    # Text content
                    if delta.content:
                        if not first_content:
                            first_content = True
                            status.stop()
                        content += delta.content
                        console.print(delta.content, end="")

                    # Tool calls
                    if delta.tool_calls:
                        if not first_content:
                            first_content = True
                            status.stop()
                        for tc in delta.tool_calls:
                            if tc.id:
                                current_tool_id = tc.id
                                tool_calls_data[current_tool_id] = {
                                    "id": tc.id,
                                    "name": tc.function.name if tc.function else "",
                                    "arguments": ""
                                }
                            if tc.function and tc.function.arguments and current_tool_id:
                                tool_calls_data[current_tool_id]["arguments"] += tc.function.arguments

                if content:
                    console.print()  # Newline

            except Exception as e:
                status.stop()
                raise e

        # Convert to tool_calls list
        tool_calls = []
        for tc_id, tc_data in tool_calls_data.items():
            if tc_data["name"]:
                tool_calls.append(type('ToolCall', (), {
                    'id': tc_data["id"],
                    'function': type('Function', (), {
                        'name': tc_data["name"],
                        'arguments': tc_data["arguments"]
                    })()
                })())

        return content, tool_calls

    def chat(self, user_input):
        self.messages.append({"role": "user", "content": user_input})

        system = f"""Sen Kimi, profesyonel bir yazilim gelistirme asistanisin.
Calisma dizini: {os.getcwd()}

Kurallar:
- Turkce yanit ver
- Dosya olusturmak/duzenlemek icin MUTLAKA tool kullan
- Kod yazarken modern ve temiz kod yaz
- Her dosyayi ayri tool call ile olustur
- Hizli calis, gereksiz aciklama yapma"""

        msgs = [{"role": "system", "content": system}] + self.messages[-12:]

        try:
            console.print(f"\n[bold cyan]◆ Kimi[/bold cyan] [dim]({self.cfg.model})[/dim]")

            content, tool_calls = self.stream_response(msgs, system, "Düşünüyor...")

            iterations = 0

            while tool_calls and iterations < 20:
                iterations += 1
                console.print(f"\n[dim]── Adım {iterations} ──[/dim]")

                tool_results = []
                for tc in tool_calls:
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
                    "content": content,
                    "tool_calls": [
                        {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                        for tc in tool_calls
                    ]
                })
                self.messages.extend(tool_results)

                # Devam et
                msgs = [{"role": "system", "content": system}] + self.messages[-12:]
                content, tool_calls = self.stream_response(msgs, system, "Devam ediyor...")

            self.messages.append({"role": "assistant", "content": content})
            return content

        except Exception as e:
            console.print(f"\n[{COLORS['error']}]API Error: {e}[/{COLORS['error']}]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
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

            # Magic keywords (oh-my-kimi style) - convert to slash commands
            lower_input = user_input.lower().strip()
            if lower_input.startswith("autopilot "):
                user_input = "/autopilot " + user_input[10:]
            elif lower_input.startswith("team "):
                user_input = "/team " + user_input[5:]
            elif lower_input.startswith("ralph "):
                user_input = "/ralph " + user_input[6:]
            elif lower_input.startswith("ultra "):
                user_input = "/ultra " + user_input[6:]

            # Komutlar
            if user_input.startswith("/"):
                cmd = user_input.lower().strip()

                if cmd == "/help":
                    console.print(Panel(
                        "[bold white]Temel:[/bold white]\n"
                        "[cyan]/help[/cyan]      Yardim\n"
                        "[cyan]/init[/cyan]      Proje analizi\n"
                        "[cyan]/model[/cyan]     Model degistir\n"
                        "[cyan]/login[/cyan]     API key ayarla\n"
                        "[cyan]/clear[/cyan]     Sohbeti temizle\n"
                        "[cyan]/exit[/cyan]      Cikis\n\n"
                        "[bold white]Agent Modlari:[/bold white]\n"
                        "[magenta]/autopilot[/magenta] Tam otonom calisma\n"
                        "[yellow]/team[/yellow]      Coklu agent (5 rol)\n"
                        "[red]/ralph[/red]     Durmak yok modu\n"
                        "[blue]/ultra[/blue]     Maximum hiz\n"
                        "[cyan]/swarm[/cyan]     Paralel ajanlar",
                        title="[bold]Kimi CLI Komutlari[/bold]",
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

                elif cmd == "/init":
                    console.print(f"\n[{COLORS['info']}]Proje analiz ediliyor...[/{COLORS['info']}]")

                    # Proje dosyalarını tara
                    project_files = []
                    for pattern in ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.json", "*.md", "*.yaml", "*.yml"]:
                        project_files.extend(Path(".").glob(f"**/{pattern}"))
                    project_files = [str(f) for f in project_files if ".git" not in str(f) and "node_modules" not in str(f)][:30]

                    if project_files:
                        file_list = "\n".join(f"  - {f}" for f in project_files[:20])
                        console.print(f"\n[{COLORS['success']}]Bulunan dosyalar ({len(project_files)}):[/{COLORS['success']}]\n{file_list}")

                        # AGENTS.md olustur
                        agents_content = f"""# Project Analysis

## Files Found ({len(project_files)})

{chr(10).join('- ' + f for f in project_files[:20])}

## Suggested Tasks

- Code review
- Bug fixes
- Feature development
- Documentation

Generated by Kimi CLI
"""
                        Path("AGENTS.md").write_text(agents_content, encoding="utf-8")
                        console.print(f"\n[{COLORS['success']}]AGENTS.md olusturuldu[/{COLORS['success']}]")
                    else:
                        console.print(f"[{COLORS['warning']}]Proje dosyasi bulunamadi[/{COLORS['warning']}]")

                elif cmd.startswith("/swarm"):
                    parts = user_input.split(maxsplit=1)
                    if len(parts) < 2:
                        console.print(f"[{COLORS['warning']}]Kullanim: /swarm <gorev>[/{COLORS['warning']}]")
                    else:
                        task = parts[1]
                        console.print(f"\n[{COLORS['info']}]Agent Swarm baslatiliyor...[/{COLORS['info']}]")
                        console.print(f"[dim]Gorev: {task}[/dim]\n")

                        # Paralel agent simülasyonu
                        agents = ["Planner", "Coder", "Reviewer"]
                        for i, a in enumerate(agents, 1):
                            console.print(f"[cyan]Agent {i}/{len(agents)}:[/cyan] [bold]{a}[/bold] [dim]calisiyor...[/dim]")

                        # Asıl gorevi agenta gonder
                        response = agent.chat(f"Bu gorevi tamamla: {task}\n\nOnce plan yap, sonra kodu yaz, sonra kontrol et.")
                        if response:
                            console.print()
                            console.print(Markdown(response))
                            console.print()
                        continue

                elif cmd == "/login":
                    console.print(f"\n[{COLORS['info']}]API Ayarlari[/{COLORS['info']}]")
                    new_key = Prompt.ask("API Key", default=cfg.api_key[:8]+"..." if cfg.api_key else "")
                    if new_key and not new_key.endswith("..."):
                        cfg.api_key = new_key
                        cfg.save()
                        console.print(f"[{COLORS['success']}]API Key kaydedildi![/{COLORS['success']}]")
                    else:
                        console.print(f"[dim]Degisiklik yapilmadi[/dim]")

                elif cmd.startswith("/autopilot"):
                    # oh-my-kimi: Full autonomous execution
                    parts = user_input.split(maxsplit=1)
                    if len(parts) < 2:
                        console.print(f"[{COLORS['warning']}]Kullanim: /autopilot <gorev>[/{COLORS['warning']}]")
                    else:
                        task = parts[1]
                        console.print(f"\n[bold magenta]🤖 AUTOPILOT MODE[/bold magenta]")
                        console.print(f"[dim]Gorev: {task}[/dim]\n")

                        autopilot_prompt = f"""AUTOPILOT MODE - Tam otonom calisma

GOREV: {task}

KURALLAR:
1. Gorevi tamamlanana kadar dur
2. Her adimi acikla ve uygula
3. Hatalarla karsilasirsan duzelt ve devam et
4. Bittiginde ozet ver

ADIMLAR:
1. Analiz - Gorevi analiz et
2. Plan - Adim adim plan yap
3. Uygula - Her adimi sirayla uygula
4. Dogrula - Sonucu kontrol et
5. Raporla - Ozet ver

BASLA:"""
                        response = agent.chat(autopilot_prompt)
                        if response:
                            console.print()
                            console.print(Markdown(response))
                            console.print()
                        continue

                elif cmd.startswith("/team"):
                    # oh-my-kimi: Multi-agent coordination
                    parts = user_input.split(maxsplit=1)
                    if len(parts) < 2:
                        console.print(f"[{COLORS['warning']}]Kullanim: /team <gorev>[/{COLORS['warning']}]")
                    else:
                        task = parts[1]
                        console.print(f"\n[bold yellow]👥 TEAM MODE[/bold yellow]")
                        console.print(f"[dim]Gorev: {task}[/dim]\n")

                        team_agents = [
                            ("🧠 Architect", "Mimari tasarim"),
                            ("💻 Developer", "Kod yazimi"),
                            ("🔍 Reviewer", "Kod inceleme"),
                            ("🧪 Tester", "Test yazimi"),
                            ("📝 Documenter", "Dokumantasyon"),
                        ]

                        for emoji_name, role in team_agents:
                            console.print(f"[cyan]{emoji_name}[/cyan] [dim]{role}...[/dim]")

                        team_prompt = f"""TEAM MODE - Coklu agent koordinasyonu

GOREV: {task}

TAKIMINDAKI ROLLER:
- Architect: Mimari kararlari al
- Developer: Kodu yaz
- Reviewer: Kodu incele ve iyilestir
- Tester: Test senaryolari olustur
- Documenter: Dokumantasyon ekle

Her rol icin sirasi ile calis ve sonuclari birbirine aktar.
Tum roller tamamlaninca final ciktiyi ver.

BASLA:"""
                        response = agent.chat(team_prompt)
                        if response:
                            console.print()
                            console.print(Markdown(response))
                            console.print()
                        continue

                elif cmd.startswith("/ralph"):
                    # oh-my-kimi: Persistent execution until done
                    parts = user_input.split(maxsplit=1)
                    if len(parts) < 2:
                        console.print(f"[{COLORS['warning']}]Kullanim: /ralph <gorev>[/{COLORS['warning']}]")
                    else:
                        task = parts[1]
                        console.print(f"\n[bold red]🔥 RALPH MODE - Durmak yok![/bold red]")
                        console.print(f"[dim]Gorev: {task}[/dim]\n")

                        ralph_prompt = f"""RALPH MODE - Is bitene kadar durma!

GOREV: {task}

KURALLAR:
1. ASLA pes etme
2. Hata alirsan farkli yol dene
3. Takildiysan yaratici cozumler bul
4. Is TAMAMEN bitene kadar devam et
5. Her adimda ilerleme goster

ODAKLAN VE BITIR:"""

                        max_iterations = 5
                        for i in range(max_iterations):
                            console.print(f"\n[bold red]Ralph Iteration {i+1}/{max_iterations}[/bold red]")
                            response = agent.chat(ralph_prompt if i == 0 else "Devam et, gorevi tamamla. Eksik bir sey varsa tamamla.")
                            if response:
                                console.print()
                                console.print(Markdown(response))
                            if "tamamlandi" in response.lower() or "bitti" in response.lower() or "basarili" in response.lower():
                                console.print(f"\n[{COLORS['success']}]Ralph gorevi tamamladi![/{COLORS['success']}]")
                                break
                        continue

                elif cmd.startswith("/ultra"):
                    # oh-my-kimi: Maximum parallelism
                    parts = user_input.split(maxsplit=1)
                    if len(parts) < 2:
                        console.print(f"[{COLORS['warning']}]Kullanim: /ultra <gorev>[/{COLORS['warning']}]")
                    else:
                        task = parts[1]
                        console.print(f"\n[bold blue]⚡ ULTRA MODE - Maximum performans![/bold blue]")

                        ultra_prompt = f"""ULTRA MODE - Maximum hiz ve kalite

GOREV: {task}

CALISMA SEKLI:
1. Hizli analiz yap
2. En verimli cozumu sec
3. Minimum adimda maksimum sonuc
4. Gereksiz aciklama yapma, sadece calis
5. Kod yaz, test et, bitir

HIZLI BASLA:"""
                        response = agent.chat(ultra_prompt)
                        if response:
                            console.print()
                            console.print(Markdown(response))
                            console.print()
                        continue

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
