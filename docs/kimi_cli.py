#!/usr/bin/env python3
"""Kimi K2.5 CLI Agent"""

import os, sys, json, re, subprocess
from pathlib import Path
from dataclasses import dataclass

try:
    from openai import OpenAI
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.table import Table
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "openai>=1.0", "rich", "-q"])
    from openai import OpenAI
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.table import Table

console = Console()
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
                d = json.loads(CONFIG_FILE.read_text())
                return cls(**{k:v for k,v in d.items() if hasattr(cls, k)})
            except: pass
        return cls()

    def save(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(self.__dict__, indent=2))

# Tools
def read_file(path):
    try:
        return f"[OK]\n{Path(path).read_text(encoding='utf-8')}"
    except Exception as e:
        return f"[HATA] {e}"

def write_file(path, content):
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(content, encoding='utf-8')
        return f"[OK] {path} ({len(content)} byte)"
    except Exception as e:
        return f"[HATA] {e}"

def list_files(path=".", pattern="*"):
    try:
        files = list(Path(path).glob(pattern))[:30]
        return "\n".join(f.name for f in files) or "[BOŞ]"
    except Exception as e:
        return f"[HATA] {e}"

def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return (r.stdout + r.stderr)[:3000] or "[OK]"
    except Exception as e:
        return f"[HATA] {e}"

TOOLS = [
    {"type":"function","function":{"name":"read_file","description":"Dosya oku","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function","function":{"name":"write_file","description":"Dosya yaz","parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}}},
    {"type":"function","function":{"name":"list_files","description":"Dosya listele","parameters":{"type":"object","properties":{"path":{"type":"string"},"pattern":{"type":"string"}}}}},
    {"type":"function","function":{"name":"run_cmd","description":"Komut calistir","parameters":{"type":"object","properties":{"cmd":{"type":"string"}},"required":["cmd"]}}},
]

def run_tool(name, args):
    console.print(f"  [yellow]► {name}[/yellow]", end=" ")
    if name == "read_file": r = read_file(args.get("path",""))
    elif name == "write_file": r = write_file(args.get("path",""), args.get("content",""))
    elif name == "list_files": r = list_files(args.get("path","."), args.get("pattern","*"))
    elif name == "run_cmd": r = run_cmd(args.get("cmd",""))
    else: r = "[?]"
    console.print(f"[dim]{r[:60]}...[/dim]" if len(r)>60 else f"[dim]{r}[/dim]")
    return r

class Agent:
    def __init__(self, cfg):
        self.cfg = cfg
        self.client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)
        self.msgs = []

    def chat(self, text):
        self.msgs.append({"role":"user","content":text})

        sys_msg = f"Sen Kimi, kodlama asistanisin. Dizin: {os.getcwd()}. Turkce yaz."
        msgs = [{"role":"system","content":sys_msg}] + self.msgs[-10:]

        # K2.5 thinking mode kapat
        extra = {"extra_body":{"thinking":{"type":"disabled"}}} if "k2" in self.cfg.model else {}

        try:
            console.print("[cyan]● Kimi dusunuyor...[/cyan]")

            res = self.client.chat.completions.create(
                model=self.cfg.model, messages=msgs, tools=TOOLS,
                max_tokens=self.cfg.max_tokens, temperature=1.0, **extra
            )
            msg = res.choices[0].message

            # Tool loop
            loop = 0
            while msg.tool_calls and loop < 10:
                loop += 1
                console.print(f"[cyan]● Tool calistiriliyor ({len(msg.tool_calls)})...[/cyan]")

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

                console.print("[cyan]● Devam ediyor...[/cyan]")
                msgs = [{"role":"system","content":sys_msg}] + self.msgs[-10:]
                res = self.client.chat.completions.create(
                    model=self.cfg.model, messages=msgs, tools=TOOLS,
                    max_tokens=self.cfg.max_tokens, temperature=1.0, **extra
                )
                msg = res.choices[0].message

            content = msg.content or ""
            self.msgs.append({"role":"assistant","content":content})
            return content

        except Exception as e:
            console.print(f"[red]Hata: {e}[/red]")
            return ""

def main():
    console.print(Panel.fit("[bold magenta]Kimi K2.5 CLI[/bold magenta]", border_style="magenta"))

    cfg = Config.load()
    if not cfg.api_key:
        cfg.api_key = Prompt.ask("API Key")
        cfg.save()

    agent = Agent(cfg)
    console.print(f"[dim]{os.getcwd()}[/dim]\n")

    while True:
        try:
            inp = Prompt.ask("[cyan]>[/cyan]")
            if not inp.strip(): continue

            if inp.startswith("/"):
                c = inp.lower()
                if c == "/help":
                    console.print("/help /clear /model /exit")
                elif c == "/clear":
                    agent.msgs = []
                    console.print("[green]OK[/green]")
                elif c.startswith("/model"):
                    ms = ["moonshot-v1-8k","moonshot-v1-32k","moonshot-v1-128k","kimi-k2.5","kimi-k2-turbo-preview"]
                    for i,m in enumerate(ms,1): console.print(f"{i}. {m}" + (" *" if m==cfg.model else ""))
                    n = Prompt.ask("Sec","4")
                    try: cfg.model = ms[int(n)-1]; cfg.save(); console.print(f"[green]{cfg.model}[/green]")
                    except: pass
                elif c in ["/exit","/quit"]:
                    break
                continue

            r = agent.chat(inp)
            if r:
                console.print()
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
        if c == "login": cfg=Config.load(); cfg.api_key=input("Key: "); cfg.save(); print("OK"); sys.exit()
    main()
