"""
Kimi CLI Tools - Dosya ve Shell işlemleri
"""

import os
import re
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Tool tanımları - OpenAI format
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
            "description": "Bir dosyaya içerik yaz (mevcut dosyanın üzerine yazar)",
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
            "description": "Bir dosyada metin değiştir (find and replace)",
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
            "description": "Bir dizindeki dosya ve klasörleri listele",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Dizin yolu", "default": "."},
                    "pattern": {"type": "string", "description": "Glob pattern (örn: *.py, **/*.js)", "default": "*"},
                    "recursive": {"type": "boolean", "description": "Alt dizinleri de tara", "default": False}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Dosyalarda metin veya regex pattern ara",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Aranacak metin veya regex"},
                    "path": {"type": "string", "description": "Arama yapılacak dizin", "default": "."},
                    "file_pattern": {"type": "string", "description": "Dosya filtresi (örn: *.py)", "default": "*"},
                    "case_sensitive": {"type": "boolean", "description": "Büyük/küçük harf duyarlı", "default": False}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Kabuk komutu çalıştır (bash/cmd)",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Çalıştırılacak komut"},
                    "timeout": {"type": "integer", "description": "Zaman aşımı (saniye)", "default": 120},
                    "cwd": {"type": "string", "description": "Çalışma dizini"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_directory",
            "description": "Yeni dizin oluştur",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Oluşturulacak dizin yolu"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Dosya veya boş dizin sil",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Silinecek dosya/dizin yolu"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_file",
            "description": "Dosya veya dizin taşı/yeniden adlandır",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Kaynak yol"},
                    "destination": {"type": "string", "description": "Hedef yol"}
                },
                "required": ["source", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_info",
            "description": "Dosya hakkında detaylı bilgi al (boyut, tarih, vb.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Dosya yolu"}
                },
                "required": ["path"]
            }
        }
    }
]


async def execute_tool(name: str, args: Dict[str, Any], workspace: str = ".") -> str:
    """Tool'u çalıştır ve sonucu döndür"""

    # Yolları workspace'e göre ayarla
    def resolve_path(p: str) -> Path:
        path = Path(p)
        if not path.is_absolute():
            path = Path(workspace) / path
        return path

    try:
        if name == "read_file":
            path = resolve_path(args["path"])
            if not path.exists():
                return f"[HATA] Dosya bulunamadı: {path}"
            if path.is_dir():
                return f"[HATA] Bu bir dizin: {path}"

            content = path.read_text(encoding="utf-8")
            lines = len(content.split("\n"))
            return f"[OK] {path} okundu ({len(content)} karakter, {lines} satır)\n\n{content}"

        elif name == "write_file":
            path = resolve_path(args["path"])
            content = args["content"]

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

            return f"[OK] {path} yazıldı ({len(content)} karakter)"

        elif name == "edit_file":
            path = resolve_path(args["path"])
            old_text = args["old_text"]
            new_text = args["new_text"]

            if not path.exists():
                return f"[HATA] Dosya bulunamadı: {path}"

            content = path.read_text(encoding="utf-8")

            if old_text not in content:
                # Benzer metinleri bul
                lines = content.split("\n")
                similar = [l.strip() for l in lines if old_text[:20] in l][:3]
                hint = f"\nBenzer satırlar: {similar}" if similar else ""
                return f"[HATA] Metin bulunamadı: '{old_text[:50]}...'{hint}"

            new_content = content.replace(old_text, new_text, 1)
            path.write_text(new_content, encoding="utf-8")

            return f"[OK] {path} düzenlendi"

        elif name == "list_files":
            path = resolve_path(args.get("path", "."))
            pattern = args.get("pattern", "*")
            recursive = args.get("recursive", False)

            if not path.exists():
                return f"[HATA] Dizin bulunamadı: {path}"

            glob_func = path.rglob if recursive else path.glob
            files = list(glob_func(pattern))[:100]

            if not files:
                return f"[INFO] '{pattern}' ile eşleşen dosya bulunamadı"

            result = []
            for f in sorted(files):
                try:
                    stat = f.stat()
                    ftype = "D" if f.is_dir() else "F"
                    size = f"{stat.st_size:,}" if not f.is_dir() else "-"
                    mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    rel_path = f.relative_to(path) if recursive else f.name
                    result.append(f"[{ftype}] {rel_path:<50} {size:>12} bytes  {mtime}")
                except:
                    pass

            return f"Toplam: {len(files)} dosya/dizin\n\n" + "\n".join(result)

        elif name == "search_files":
            search_pattern = args["pattern"]
            path = resolve_path(args.get("path", "."))
            file_pattern = args.get("file_pattern", "*")
            case_sensitive = args.get("case_sensitive", False)

            flags = 0 if case_sensitive else re.IGNORECASE

            results = []
            try:
                regex = re.compile(search_pattern, flags)
            except re.error as e:
                return f"[HATA] Geçersiz regex: {e}"

            for f in path.rglob(file_pattern):
                if f.is_file():
                    try:
                        content = f.read_text(encoding="utf-8", errors="ignore")
                        for i, line in enumerate(content.split("\n"), 1):
                            if regex.search(line):
                                rel_path = f.relative_to(path)
                                results.append(f"{rel_path}:{i}: {line.strip()[:100]}")
                                if len(results) >= 50:
                                    break
                    except:
                        pass

                if len(results) >= 50:
                    break

            if not results:
                return f"[INFO] '{search_pattern}' bulunamadı"

            return f"Bulunan: {len(results)} eşleşme\n\n" + "\n".join(results)

        elif name == "run_command":
            command = args["command"]
            timeout = args.get("timeout", 120)
            cwd = args.get("cwd", workspace)

            # Tehlikeli komutları engelle
            dangerous = ["rm -rf /", "del /f /s /q c:", "format", ":(){:|:&};:"]
            if any(d in command.lower() for d in dangerous):
                return "[HATA] Tehlikeli komut engellendi"

            try:
                result = await asyncio.wait_for(
                    asyncio.create_subprocess_shell(
                        command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=cwd
                    ),
                    timeout=timeout
                )

                stdout, stderr = await result.communicate()
                output = stdout.decode("utf-8", errors="ignore") + stderr.decode("utf-8", errors="ignore")

                status = "OK" if result.returncode == 0 else f"HATA (kod: {result.returncode})"
                return f"[{status}]\n{output[:10000]}"

            except asyncio.TimeoutError:
                return f"[HATA] Komut zaman aşımına uğradı ({timeout}s)"

        elif name == "create_directory":
            path = resolve_path(args["path"])
            path.mkdir(parents=True, exist_ok=True)
            return f"[OK] Dizin oluşturuldu: {path}"

        elif name == "delete_file":
            path = resolve_path(args["path"])
            if not path.exists():
                return f"[HATA] Dosya/dizin bulunamadı: {path}"

            if path.is_dir():
                if list(path.iterdir()):
                    return f"[HATA] Dizin boş değil: {path}"
                path.rmdir()
            else:
                path.unlink()

            return f"[OK] Silindi: {path}"

        elif name == "move_file":
            source = resolve_path(args["source"])
            destination = resolve_path(args["destination"])

            if not source.exists():
                return f"[HATA] Kaynak bulunamadı: {source}"

            destination.parent.mkdir(parents=True, exist_ok=True)
            source.rename(destination)

            return f"[OK] Taşındı: {source} -> {destination}"

        elif name == "get_file_info":
            path = resolve_path(args["path"])

            if not path.exists():
                return f"[HATA] Dosya bulunamadı: {path}"

            stat = path.stat()
            info = {
                "path": str(path.absolute()),
                "name": path.name,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "size": stat.st_size,
                "size_human": f"{stat.st_size:,} bytes",
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": path.suffix
            }

            if path.is_file():
                try:
                    lines = len(path.read_text(encoding="utf-8").split("\n"))
                    info["lines"] = lines
                except:
                    pass

            return "[OK] Dosya bilgisi:\n" + "\n".join(f"  {k}: {v}" for k, v in info.items())

        else:
            return f"[HATA] Bilinmeyen tool: {name}"

    except Exception as e:
        return f"[HATA] Tool hatası ({name}): {str(e)}"
