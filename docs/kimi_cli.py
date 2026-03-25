#!/usr/bin/env python3
"""Kimi K2.5 CLI Agent - Claude Code Style"""

import os, sys, json, subprocess
from pathlib import Path
from dataclasses import dataclass

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from openai import OpenAI
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.text import Text
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "openai>=1.0", "rich", "-q"])
    from openai import OpenAI
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.text import Text

console = Console(force_terminal=True)
CONFIG_FILE = Path.home() / ".kimi-cli" / "config.json"

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


def get_file_type(path):
    """Dosya uzantısına göre dil döndür"""
    ext = Path(path).suffix.lower()
    types = {
        '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
        '.html': 'html', '.css': 'css', '.json': 'json',
        '.md': 'markdown', '.sql': 'sql', '.sh': 'bash',
        '.jsx': 'jsx', '.tsx': 'tsx', '.vue': 'vue',
        '.php': 'php', '.rb': 'ruby', '.go': 'go',
        '.rs': 'rust', '.java': 'java', '.c': 'c', '.cpp': 'cpp'
    }
    return types.get(ext, 'text')


def show_code(content, path, title=""):
    """Kodu syntax highlighting ile göster"""
    lang = get_file_type(path)
    syntax = Syntax(content, lang, theme="monokai", line_numbers=True, word_wrap=True)
    panel_title = title or f"[bold green]{path}[/bold green]"
    console.print(Panel(syntax, title=panel_title, border_style="green"))


def show_diff(old_content, new_content, path):
    """Değişiklikleri diff formatında göster"""
    old_lines = old_content.split('\n') if old_content else []
    new_lines = new_content.split('\n')

    console.print(f"\n[bold yellow]--- {path}[/bold yellow]")

    # Basit diff gösterimi
    import difflib
    diff = difflib.unified_diff(old_lines, new_lines, lineterm='', n=3)

    for line in diff:
        if line.startswith('+++') or line.startswith('---'):
            continue
        elif line.startswith('@@'):
            console.print(f"[cyan]{line}[/cyan]")
        elif line.startswith('+'):
            console.print(f"[green on dark_green]{line}[/green on dark_green]")
        elif line.startswith('-'):
            console.print(f"[red on dark_red]{line}[/red on dark_red]")
        else:
            console.print(f"[dim]{line}[/dim]")

    console.print()


def read_file(path):
    try:
        content = Path(path).read_text(encoding='utf-8')
        console.print(f"\n[bold blue]Okunuyor: {path}[/bold blue]")
        show_code(content, path, f"[blue]{path}[/blue]")
        return f"[OK]\n{content}"
    except Exception as e:
        console.print(f"[red]Okunamadi: {e}[/red]")
        return f"[HATA] {e}"


def write_file(path, content):
    try:
        p = Path(path)
        old_content = ""
        is_new = not p.exists()

        if p.exists():
            old_content = p.read_text(encoding='utf-8')

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')

        if is_new:
            console.print(f"\n[bold green]+ Yeni dosya: {path}[/bold green]")
            show_code(content, path, f"[green]+ {path}[/green]")
        else:
            console.print(f"\n[bold yellow]~ Guncellendi: {path}[/bold yellow]")
            show_diff(old_content, content, path)

        return f"[OK] {path} ({len(content)} byte)"
    except Exception as e:
        console.print(f"[red]Yazilamadi: {e}[/red]")
        return f"[HATA] {e}"


def edit_file(path, old_text, new_text):
    try:
        p = Path(path)
        if not p.exists():
            return f"[HATA] Dosya yok: {path}"

        content = p.read_text(encoding='utf-8')
        if old_text not in content:
            return f"[HATA] Metin bulunamadi"

        new_content = content.replace(old_text, new_text, 1)
        p.write_text(new_content, encoding='utf-8')

        console.print(f"\n[bold yellow]~ Duzenlendi: {path}[/bold yellow]")
        show_diff(content, new_content, path)

        return f"[OK] {path} duzenlendi"
    except Exception as e:
        console.print(f"[red]Duzenlenemedi: {e}[/red]")
        return f"[HATA] {e}"


def list_files(path=".", pattern="*"):
    try:
        files = list(Path(path).glob(pattern))[:30]
        if not files:
            console.print(f"[dim]Dosya bulunamadi: {pattern}[/dim]")
            return "[BOS]"

        console.print(f"\n[bold blue]Dosyalar ({path}/{pattern}):[/bold blue]")
        for f in sorted(files):
            icon = "[DIR]" if f.is_dir() else "[FILE]"
            size = f.stat().st_size if f.is_file() else 0
            console.print(f"  {icon} {f.name} [dim]({size} byte)[/dim]")

        return "\n".join(f.name for f in files)
    except Exception as e:
        return f"[HATA] {e}"


def run_cmd(cmd):
    try:
        console.print(f"\n[bold magenta]$ {cmd}[/bold magenta]")
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        output = (r.stdout + r.stderr)[:3000]

        if r.returncode == 0:
            console.print(f"[green]{output}[/green]" if output else "[green][OK][/green]")
        else:
            console.print(f"[red]{output}[/red]" if output else f"[red]Exit code: {r.returncode}[/red]")

        return output or "[OK]"
    except Exception as e:
        console.print(f"[red]Komut hatasi: {e}[/red]")
        return f"[HATA] {e}"


TOOLS = [
    {"type":"function","function":{"name":"read_file","description":"Dosya oku","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function","function":{"name":"write_file","description":"Dosya yaz/olustur","parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}}},
    {"type":"function","function":{"name":"edit_file","description":"Dosyada metin degistir","parameters":{"type":"object","properties":{"path":{"type":"string"},"old_text":{"type":"string"},"new_text":{"type":"string"}},"required":["path","old_text","new_text"]}}},
    {"type":"function","function":{"name":"list_files","description":"Dosya listele","parameters":{"type":"object","properties":{"path":{"type":"string"},"pattern":{"type":"string"}}}}},
    {"type":"function","function":{"name":"run_cmd","description":"Komut calistir","parameters":{"type":"object","properties":{"cmd":{"type":"string"}},"required":["cmd"]}}},
]


def run_tool(name, args):
    console.print(f"\n[cyan]>> {name}[/cyan]", end="")
    if args:
        args_str = ", ".join(f"{k}={repr(v)[:30]}" for k,v in args.items() if k != 'content')
        console.print(f"[dim]({args_str})[/dim]")
    else:
        console.print()

    if name == "read_file":
        return read_file(args.get("path",""))
    elif name == "write_file":
        return write_file(args.get("path",""), args.get("content",""))
    elif name == "edit_file":
        return edit_file(args.get("path",""), args.get("old_text",""), args.get("new_text",""))
    elif name == "list_files":
        return list_files(args.get("path","."), args.get("pattern","*"))
    elif name == "run_cmd":
        return run_cmd(args.get("cmd",""))
    return "[?]"


class Agent:
    def __init__(self, cfg):
        self.cfg = cfg
        self.client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)
        self.msgs = []

    def chat(self, text):
        self.msgs.append({"role":"user","content":text})
        sys_msg = f"""Sen Kimi, uzman bir kodlama asistanisin.
Calisma dizini: {os.getcwd()}
Turkce yanit ver. Dosya olustururken veya duzenlerken mutlaka ilgili tool'u kullan."""

        msgs = [{"role":"system","content":sys_msg}] + self.msgs[-10:]
        extra = {"extra_body":{"thinking":{"type":"disabled"}}} if "k2" in self.cfg.model else {}

        try:
            console.print("\n[bold cyan]Kimi calisiyor...[/bold cyan]")

            res = self.client.chat.completions.create(
                model=self.cfg.model, messages=msgs, tools=TOOLS,
                max_tokens=self.cfg.max_tokens, temperature=0.6, **extra
            )
            msg = res.choices[0].message

            loop = 0
            while msg.tool_calls and loop < 15:
                loop += 1

                results = []
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                    r = run_tool(tc.function.name, args)
                    results.append({"role":"tool","tool_call_id":tc.id,"content":r})

                self.msgs.append({"role":"assistant","content":msg.content,"tool_calls":[
                    {"id":tc.id,"type":"function","function":{"name":tc.function.name,"arguments":tc.function.arguments}}
                    for tc in msg.tool_calls
                ]})
                self.msgs.extend(results)

                msgs = [{"role":"system","content":sys_msg}] + self.msgs[-10:]
                res = self.client.chat.completions.create(
                    model=self.cfg.model, messages=msgs, tools=TOOLS,
                    max_tokens=self.cfg.max_tokens, temperature=0.6, **extra
                )
                msg = res.choices[0].message

            content = msg.content or ""
            self.msgs.append({"role":"assistant","content":content})
            return content

        except Exception as e:
            console.print(f"[bold red]Hata: {e}[/bold red]")
            return ""


def main():
    console.print(Panel.fit(
        "[bold magenta]Kimi K2.5 CLI[/bold magenta]\n[dim]Claude Code Style Terminal Agent[/dim]",
        border_style="magenta"
    ))

    cfg = Config.load()
    if not cfg.api_key:
        cfg.api_key = Prompt.ask("Moonshot API Key")
        cfg.save()

    agent = Agent(cfg)
    console.print(f"[dim]Dizin: {os.getcwd()}[/dim]")
    console.print("[dim]/help ile komutlari gor[/dim]\n")

    while True:
        try:
            inp = Prompt.ask("[bold cyan]>[/bold cyan]")
            if not inp.strip(): continue

            if inp.startswith("/"):
                c = inp.lower().strip()
                if c == "/help":
                    console.print(Panel("""[cyan]/help[/cyan]  - Yardim
[cyan]/clear[/cyan] - Sohbeti temizle
[cyan]/model[/cyan] - Model degistir
[cyan]/exit[/cyan]  - Cikis""", title="Komutlar"))
                elif c == "/clear":
                    agent.msgs = []
                    console.print("[green]Temizlendi[/green]")
                elif c.startswith("/model"):
                    ms = ["moonshot-v1-8k","moonshot-v1-32k","moonshot-v1-128k","kimi-k2.5","kimi-k2-turbo-preview"]
                    console.print("\n[bold]Modeller:[/bold]")
                    for i,m in enumerate(ms,1):
                        mark = " [cyan](aktif)[/cyan]" if m==cfg.model else ""
                        console.print(f"  {i}. {m}{mark}")
                    n = Prompt.ask("\nSec", default="4")
                    try:
                        cfg.model = ms[int(n)-1]
                        cfg.save()
                        console.print(f"[green]Model: {cfg.model}[/green]")
                    except: pass
                elif c in ["/exit","/quit"]:
                    console.print("[yellow]Gule gule![/yellow]")
                    break
                continue

            r = agent.chat(inp)
            if r:
                console.print("\n" + "="*50)
                console.print(Markdown(r))
                console.print()

        except KeyboardInterrupt:
            console.print()
        except EOFError:
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        c = sys.argv[1]
        if c in ["-v","--version"]: print("Kimi CLI v1.0"); sys.exit()
        if c in ["-h","--help"]: print("kimi [web|login]"); sys.exit()
        if c == "web": __import__("webbrowser").open("http://localhost:3000"); sys.exit()
        if c == "login":
            cfg=Config.load()
            cfg.api_key=input("API Key: ")
            cfg.save()
            print("Kaydedildi!")
            sys.exit()
    main()
