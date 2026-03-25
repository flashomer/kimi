# Kimi 2.5 CLI Agent

Moonshot AI Kimi K2.5 API kullanan, Claude Code benzeri terminal ajanı.

## Özellikler

- **Dosya İşlemleri**: Okuma, yazma, düzenleme, arama
- **Shell Komutları**: Terminal komutlarını çalıştırma
- **Real-time Chat**: WebSocket ile anlık iletişim
- **Session Yönetimi**: Sohbet geçmişi kaydetme
- **Modern UI**: React + TailwindCSS arayüz
- **Docker Ready**: Tek komutla kurulum

## Hızlı Başlangıç

### 1. API Key Alın

[Moonshot AI Platform](https://platform.moonshot.ai) adresinden API key alın.

### 2. Kurulum

```bash
# Repo'yu klonlayın
git clone https://github.com/yourusername/kimi-cli.git
cd kimi-cli

# .env dosyasını oluşturun
cp .env.example .env

# API key'inizi .env dosyasına ekleyin
# MOONSHOT_API_KEY=your_api_key_here

# Docker ile başlatın
docker-compose up --build
```

### 3. Kullanım

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## CLI Kullanımı (Docker Olmadan)

```bash
# Bağımlılıkları yükleyin
pip install -r requirements.txt

# CLI'yi çalıştırın
python kimi_cli.py
```

### CLI Komutları

| Komut | Açıklama |
|-------|----------|
| `/help` | Yardım mesajı |
| `/clear` | Konuşma geçmişini temizle |
| `/config` | Ayarları göster |
| `/shell` | Shell moduna geç |
| `/exit` | Çıkış |

## API Endpoints

| Endpoint | Metod | Açıklama |
|----------|-------|----------|
| `/chat` | POST | Mesaj gönder |
| `/sessions` | GET | Tüm session'ları listele |
| `/sessions/{id}` | GET | Session detayları |
| `/sessions/{id}` | DELETE | Session sil |
| `/files` | GET | Dosyaları listele |
| `/files/read` | GET | Dosya oku |
| `/files/write` | POST | Dosya yaz |
| `/ws/{session_id}` | WS | WebSocket chat |

## Kimi K2.5 Özellikleri

- **1 Trilyon Parametre** (MoE mimarisi, 32B aktif)
- **256K Context Window**
- **Native Multimodal** (görsel + metin)
- **Agent Swarm** (paralel görev yönetimi)
- **OpenAI API Uyumlu**

## Proje Yapısı

```
kimi/
├── backend/
│   ├── main.py          # FastAPI uygulaması
│   ├── tools.py         # Tool fonksiyonları
│   └── config.py        # Konfigürasyon
├── frontend/
│   └── src/
│       ├── App.jsx      # Ana React component
│       └── index.css    # Stiller
├── kimi_cli.py          # Standalone CLI
├── docker-compose.yml   # Docker yapılandırması
└── requirements.txt     # Python bağımlılıkları
```

## Geliştirme

```bash
# Backend (development)
cd backend
uvicorn main:app --reload --port 8000

# Frontend (development)
cd frontend
npm install
npm run dev
```

## Lisans

MIT License

## Kaynaklar

- [Moonshot AI Platform](https://platform.moonshot.ai)
- [Kimi K2.5 GitHub](https://github.com/MoonshotAI/Kimi-K2.5)
- [Kimi Code CLI](https://github.com/MoonshotAI/kimi-cli)
