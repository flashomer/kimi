"""
Kimi 2.5 CLI Backend - FastAPI
Real-time AI agent API with WebSocket support
"""

import os
import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import redis.asyncio as redis
from openai import AsyncOpenAI

from .tools import TOOLS, execute_tool
from .config import settings

app = FastAPI(
    title="Kimi 2.5 CLI API",
    description="Moonshot AI K2.5 powered terminal agent API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client: Optional[redis.Redis] = None

# OpenAI client for Kimi API
kimi_client: Optional[AsyncOpenAI] = None

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    workspace: Optional[str] = "."


class ChatResponse(BaseModel):
    response: str
    session_id: str
    tool_calls: List[Dict[str, Any]] = []


class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    message_count: int
    workspace: str


@app.on_event("startup")
async def startup():
    global redis_client, kimi_client

    # Redis bağlantısı
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        print(f"Redis bağlantısı başarılı: {redis_url}")
    except Exception as e:
        print(f"Redis bağlantı hatası: {e}")
        redis_client = None

    # Kimi API client
    api_key = os.getenv("MOONSHOT_API_KEY", "")
    if api_key:
        kimi_client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.ai/v1"
        )
        print("Kimi API client hazır")
    else:
        print("UYARI: MOONSHOT_API_KEY ayarlanmamış!")


@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()


def get_system_prompt(workspace: str) -> str:
    """Sistem promptu oluştur"""
    return f"""Sen Kimi, güçlü bir AI kodlama asistanısın.

## Yeteneklerin
- Dosya okuma, yazma ve düzenleme
- Kabuk komutları çalıştırma
- Kod analizi ve debugging
- Proje yapısı anlama ve oluşturma

## Çalışma Dizini
{workspace}

## Kurallar
1. Değişiklik yapmadan önce dosyaları oku
2. Güvenli olmayan komutları çalıştırma
3. Kısa ve öz yanıtlar ver
4. Türkçe yanıt ver"""


async def get_session(session_id: str) -> Dict[str, Any]:
    """Session bilgisini al"""
    if redis_client:
        data = await redis_client.get(f"session:{session_id}")
        if data:
            return json.loads(data)

    # Dosyadan oku
    session_file = Path(f"sessions/{session_id}.json")
    if session_file.exists():
        return json.loads(session_file.read_text())

    return {
        "session_id": session_id,
        "messages": [],
        "workspace": ".",
        "created_at": datetime.now().isoformat()
    }


async def save_session(session_id: str, data: Dict[str, Any]):
    """Session'ı kaydet"""
    json_data = json.dumps(data, ensure_ascii=False)

    if redis_client:
        await redis_client.set(f"session:{session_id}", json_data, ex=86400)  # 24 saat

    # Dosyaya da yaz
    session_file = Path(f"sessions/{session_id}.json")
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(json_data)


async def process_chat(message: str, session_id: str, workspace: str) -> Dict[str, Any]:
    """Chat mesajını işle"""
    if not kimi_client:
        raise HTTPException(status_code=500, detail="Kimi API yapılandırılmamış")

    # Session'ı al
    session = await get_session(session_id)
    session["workspace"] = workspace

    # Kullanıcı mesajını ekle
    session["messages"].append({"role": "user", "content": message})

    # API'ye gönder
    messages_to_send = [
        {"role": "system", "content": get_system_prompt(workspace)}
    ] + session["messages"][-20:]  # Son 20 mesaj

    tool_calls_log = []

    try:
        response = await kimi_client.chat.completions.create(
            model=settings.default_model,
            messages=messages_to_send,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=32000
        )

        assistant_message = response.choices[0].message

        # Tool çağrıları varsa işle
        while assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                # Tool'u çalıştır
                result = await execute_tool(func_name, func_args, workspace)

                tool_calls_log.append({
                    "name": func_name,
                    "args": func_args,
                    "result": result[:500]  # Kısa özet
                })

                # Mesajlara ekle
                session["messages"].append({
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
                session["messages"].append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # Devam et
            messages_to_send = [
                {"role": "system", "content": get_system_prompt(workspace)}
            ] + session["messages"][-20:]

            response = await kimi_client.chat.completions.create(
                model=settings.default_model,
                messages=messages_to_send,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=32000
            )
            assistant_message = response.choices[0].message

        # Son yanıtı kaydet
        final_content = assistant_message.content or ""
        session["messages"].append({"role": "assistant", "content": final_content})

        # Session'ı kaydet
        await save_session(session_id, session)

        return {
            "response": final_content,
            "session_id": session_id,
            "tool_calls": tool_calls_log
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# REST Endpoints

@app.get("/")
async def root():
    return {"message": "Kimi 2.5 CLI API", "version": "1.0.0"}


@app.get("/health")
async def health():
    redis_ok = False
    if redis_client:
        try:
            await redis_client.ping()
            redis_ok = True
        except:
            pass

    return {
        "status": "healthy",
        "redis": redis_ok,
        "kimi_api": kimi_client is not None
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint"""
    session_id = request.session_id or str(uuid.uuid4())
    result = await process_chat(request.message, session_id, request.workspace or ".")
    return result


@app.get("/sessions")
async def list_sessions():
    """Tüm session'ları listele"""
    sessions = []
    session_dir = Path("sessions")

    if session_dir.exists():
        for f in session_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                sessions.append({
                    "session_id": data.get("session_id", f.stem),
                    "created_at": data.get("created_at", ""),
                    "message_count": len(data.get("messages", [])),
                    "workspace": data.get("workspace", ".")
                })
            except:
                pass

    return sessions


@app.get("/sessions/{session_id}")
async def get_session_details(session_id: str):
    """Session detaylarını al"""
    session = await get_session(session_id)
    if not session["messages"]:
        raise HTTPException(status_code=404, detail="Session bulunamadı")
    return session


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Session'ı sil"""
    if redis_client:
        await redis_client.delete(f"session:{session_id}")

    session_file = Path(f"sessions/{session_id}.json")
    if session_file.exists():
        session_file.unlink()

    return {"message": "Session silindi"}


@app.get("/files")
async def list_files(path: str = ".", pattern: str = "*"):
    """Dosyaları listele"""
    try:
        p = Path(path)
        files = []
        for f in sorted(p.glob(pattern))[:100]:
            stat = f.stat()
            files.append({
                "name": f.name,
                "path": str(f),
                "is_dir": f.is_dir(),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        return files
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/files/read")
async def read_file(path: str):
    """Dosya içeriğini oku"""
    try:
        content = Path(path).read_text(encoding="utf-8")
        return {"path": path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/files/write")
async def write_file(path: str, content: str):
    """Dosyaya yaz"""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"message": f"{path} yazıldı", "size": len(content)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), path: str = "."):
    """Dosya yükle"""
    try:
        dest = Path(path) / file.filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        content = await file.read()
        dest.write_bytes(content)
        return {"message": f"{file.filename} yüklendi", "path": str(dest)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# WebSocket for real-time chat

@app.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket ile real-time chat"""
    await websocket.accept()
    active_connections[session_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            workspace = data.get("workspace", ".")

            # Typing indicator
            await websocket.send_json({"type": "typing", "status": True})

            try:
                result = await process_chat(message, session_id, workspace)
                await websocket.send_json({
                    "type": "response",
                    "data": result
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })

            await websocket.send_json({"type": "typing", "status": False})

    except WebSocketDisconnect:
        del active_connections[session_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
