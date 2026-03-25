import React, { useState, useRef, useEffect } from 'react'
import {
  Terminal, MessageSquare, FileText, Table2, Presentation, Code2,
  Search, Users, Settings, LogOut, Menu, X, Send, Plus, Trash2,
  Moon, Sun, Globe, ChevronDown, Sparkles, Zap, Bot, Cpu,
  User, Mail, Lock, Eye, EyeOff, Check, ArrowRight, Github,
  Twitter, Instagram, MessageCircle
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

const API_URL = 'http://localhost:8000'

// ==================== AUTH CONTEXT ====================
const AuthContext = React.createContext(null)

function useAuth() {
  return React.useContext(AuthContext)
}

// ==================== PAGES ====================

// Landing Page
function LandingPage({ onNavigate }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Hero */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 text-purple-300 px-4 py-2 rounded-full text-sm mb-8">
            <Sparkles size={16} /> Kimi K2.5 - 256K Context AI
          </div>
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-white via-purple-200 to-cyan-200 bg-clip-text text-transparent">
            Your AI Assistant for Everything
          </h1>
          <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
            Chat, code, create documents, analyze data - all powered by Kimi K2.5 with 256K context window
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => onNavigate('chat')}
              className="px-8 py-4 bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 rounded-xl font-semibold text-lg transition-all shadow-lg shadow-purple-500/25"
            >
              Start Chatting Free
            </button>
            <button
              onClick={() => onNavigate('features')}
              className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl font-semibold text-lg transition-all"
            >
              Explore Features
            </button>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Powerful AI Tools</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: MessageSquare, title: 'Chat', desc: 'Natural conversations with AI', color: 'purple', page: 'chat' },
              { icon: Code2, title: 'Kimi Code', desc: 'AI coding assistant in terminal', color: 'cyan', page: 'code' },
              { icon: FileText, title: 'Docs', desc: 'Create & edit documents', color: 'blue', page: 'docs' },
              { icon: Table2, title: 'Sheets', desc: 'AI-powered spreadsheets', color: 'green', page: 'sheets' },
              { icon: Presentation, title: 'Slides', desc: 'Generate presentations', color: 'orange', page: 'slides' },
              { icon: Users, title: 'Agent Swarm', desc: 'Multi-agent collaboration', color: 'pink', page: 'swarm' },
            ].map((f, i) => (
              <div
                key={i}
                onClick={() => onNavigate(f.page)}
                className={`p-6 rounded-2xl bg-gradient-to-br from-${f.color}-500/10 to-transparent border border-${f.color}-500/20 hover:border-${f.color}-500/40 cursor-pointer transition-all group`}
              >
                <f.icon className={`text-${f.color}-400 mb-4`} size={32} />
                <h3 className="text-xl font-semibold mb-2">{f.title}</h3>
                <p className="text-slate-400">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Install Section */}
      <section className="py-20 px-4 bg-black/20">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">Install Kimi CLI</h2>
          <p className="text-slate-400 mb-8">One command to get started</p>
          <div className="bg-slate-900 rounded-xl p-4 font-mono text-left max-w-2xl mx-auto">
            <div className="flex items-center justify-between">
              <code className="text-cyan-400">curl -fsSL https://flashomer.github.io/kimi/install.sh | bash</code>
              <button className="text-slate-500 hover:text-white transition-colors">
                <Check size={18} />
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

// Chat Page
function ChatPage({ user }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [chatHistory, setChatHistory] = useState([
    { id: 1, title: 'Python Flask API', date: 'Bugün' },
    { id: 2, title: 'React Component', date: 'Dün' },
  ])
  const [activeChatId, setActiveChatId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return
    const msg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: msg }])
    setIsLoading(true)

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, session_id: user?.id || 'anonymous' })
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Bağlantı hatası. Backend çalışıyor mu?' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-slate-900 border-r border-slate-800 transition-all overflow-hidden`}>
        <div className="p-4">
          <button
            onClick={() => { setMessages([]); setActiveChatId(null) }}
            className="w-full flex items-center gap-2 px-4 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg transition-colors"
          >
            <Plus size={18} /> Yeni Sohbet
          </button>
        </div>
        <div className="px-2">
          <p className="text-xs text-slate-500 px-2 py-2">Geçmiş</p>
          {chatHistory.map(chat => (
            <button
              key={chat.id}
              onClick={() => setActiveChatId(chat.id)}
              className={`w-full text-left px-3 py-2 rounded-lg mb-1 transition-colors ${
                activeChatId === chat.id ? 'bg-slate-800' : 'hover:bg-slate-800/50'
              }`}
            >
              <p className="text-sm truncate">{chat.title}</p>
              <p className="text-xs text-slate-500">{chat.date}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <Bot size={64} className="mx-auto mb-4 text-slate-700" />
                <h2 className="text-2xl font-bold mb-2">Kimi'ye Hoşgeldin!</h2>
                <p className="text-slate-500 mb-6">Sormak istediğin her şeyi yazabilirsin</p>
                <div className="flex flex-wrap gap-2 justify-center max-w-md">
                  {['Python kodu yaz', 'Web sitesi oluştur', 'Veri analizi yap'].map((s, i) => (
                    <button
                      key={i}
                      onClick={() => setInput(s)}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition-colors"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-purple-600'
                    : 'bg-slate-800'
                }`}>
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown
                      components={{
                        code({ inline, className, children }) {
                          if (inline) return <code className="bg-slate-700 px-1.5 py-0.5 rounded text-cyan-300">{children}</code>
                          const lang = className?.replace('language-', '') || 'text'
                          return (
                            <SyntaxHighlighter style={oneDark} language={lang} customStyle={{ borderRadius: '8px', margin: '8px 0' }}>
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          )
                        }
                      }}
                    >{msg.content}</ReactMarkdown>
                  ) : msg.content}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-800 rounded-2xl px-4 py-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce delay-200" />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-slate-800">
          <div className="max-w-4xl mx-auto flex gap-2">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Mesajınızı yazın..."
              className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 focus:border-purple-500 focus:outline-none transition-colors"
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="px-4 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-xl transition-colors"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Code Page
function CodePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-cyan-950 to-slate-950">
      <section className="pt-20 pb-16 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 px-4 py-2 rounded-full text-sm mb-8">
            <Terminal size={16} /> Kimi Code CLI
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            AI Coding Assistant in Your Terminal
          </h1>
          <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
            Write, debug, and understand code faster with Kimi K2.5
          </p>

          {/* Install Commands */}
          <div className="max-w-2xl mx-auto space-y-4 text-left">
            <div className="bg-slate-900/80 backdrop-blur rounded-xl border border-slate-800 overflow-hidden">
              <div className="px-4 py-2 bg-slate-800/50 text-sm text-slate-400">Linux / macOS</div>
              <div className="p-4">
                <code className="text-cyan-400">curl -fsSL https://flashomer.github.io/kimi/install.sh | bash</code>
              </div>
            </div>
            <div className="bg-slate-900/80 backdrop-blur rounded-xl border border-slate-800 overflow-hidden">
              <div className="px-4 py-2 bg-slate-800/50 text-sm text-slate-400">Windows PowerShell</div>
              <div className="p-4">
                <code className="text-cyan-400">irm https://flashomer.github.io/kimi/install.ps1 | iex</code>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Zap, title: 'Hızlı', desc: 'Streaming yanıtlar, gerçek zamanlı kod' },
              { icon: Code2, title: 'Tool Calling', desc: 'Dosya okuma, yazma, shell komutları' },
              { icon: Users, title: 'Agent Modları', desc: 'Autopilot, Team, Ralph, Ultra' },
            ].map((f, i) => (
              <div key={i} className="p-6 bg-slate-900/50 rounded-xl border border-slate-800">
                <f.icon className="text-cyan-400 mb-4" size={28} />
                <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
                <p className="text-slate-400 text-sm">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CLI Demo */}
      <section className="py-16 px-4">
        <div className="max-w-3xl mx-auto">
          <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 bg-slate-800/50 border-b border-slate-800">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="ml-2 text-sm text-slate-400">kimi</span>
            </div>
            <div className="p-4 font-mono text-sm space-y-2">
              <div className="text-slate-500">$ kimi</div>
              <div className="text-purple-400">◆ Kimi (kimi-k2.5)</div>
              <div className="text-cyan-400">&gt; Flask API oluştur</div>
              <div className="text-slate-400">⏳ Düşünüyor...</div>
              <div className="text-green-400">▶ write_file app.py</div>
              <div className="text-green-400">+ app.py (45 satır, 1.2KB)</div>
              <div className="text-white">Flask API oluşturuldu! Çalıştırmak için: python app.py</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

// Features Page
function FeaturesPage({ onNavigate }) {
  const features = [
    { icon: MessageSquare, title: 'Chat', desc: '256K context ile uzun konuşmalar', color: 'purple', page: 'chat' },
    { icon: Code2, title: 'Kimi Code', desc: 'Terminal tabanlı AI kodlama', color: 'cyan', page: 'code' },
    { icon: FileText, title: 'Docs', desc: 'Doküman oluşturma ve düzenleme', color: 'blue', page: 'docs' },
    { icon: Table2, title: 'Sheets', desc: 'Excel formülleri ve analiz', color: 'green', page: 'sheets' },
    { icon: Presentation, title: 'Slides', desc: 'Sunum oluşturma', color: 'orange', page: 'slides' },
    { icon: Search, title: 'Deep Research', desc: 'Derinlemesine araştırma', color: 'pink', page: 'chat' },
    { icon: Users, title: 'Agent Swarm', desc: 'Çoklu agent işbirliği', color: 'indigo', page: 'swarm' },
    { icon: Bot, title: 'Kimi Claw', desc: '7/24 çalışan AI agentlar', color: 'red', page: 'chat' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 to-purple-950 py-20 px-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-4">Features</h1>
        <p className="text-slate-400 text-center mb-12">Kimi ile yapabilecekleriniz</p>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((f, i) => (
            <div
              key={i}
              onClick={() => onNavigate(f.page)}
              className="p-6 bg-slate-900/50 hover:bg-slate-900 rounded-xl border border-slate-800 hover:border-purple-500/50 cursor-pointer transition-all group"
            >
              <f.icon className={`text-${f.color}-400 mb-4 group-hover:scale-110 transition-transform`} size={28} />
              <h3 className="font-semibold mb-2">{f.title}</h3>
              <p className="text-sm text-slate-400">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Auth Pages
function LoginPage({ onLogin, onNavigate }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!email || !password) {
      setError('Tüm alanları doldurun')
      return
    }
    // Demo login
    onLogin({ id: '1', email, name: email.split('@')[0] })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 text-2xl font-bold mb-2">
            <Terminal className="text-purple-400" /> Kimi
          </div>
          <p className="text-slate-400">Hesabınıza giriş yapın</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-slate-900/50 backdrop-blur rounded-2xl border border-slate-800 p-8 space-y-4">
          {error && <div className="text-red-400 text-sm bg-red-400/10 px-4 py-2 rounded-lg">{error}</div>}

          <div>
            <label className="block text-sm text-slate-400 mb-2">E-posta</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-3 focus:border-purple-500 focus:outline-none"
                placeholder="ornek@email.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-2">Şifre</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input
                type={showPass ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-12 py-3 focus:border-purple-500 focus:outline-none"
                placeholder="••••••••"
              />
              <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white">
                {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button type="submit" className="w-full py-3 bg-purple-600 hover:bg-purple-500 rounded-lg font-semibold transition-colors">
            Giriş Yap
          </button>

          <p className="text-center text-slate-400">
            Hesabınız yok mu?{' '}
            <button type="button" onClick={() => onNavigate('register')} className="text-purple-400 hover:text-purple-300">
              Kayıt Ol
            </button>
          </p>
        </form>
      </div>
    </div>
  )
}

function RegisterPage({ onLogin, onNavigate }) {
  const [form, setForm] = useState({ name: '', surname: '', username: '', email: '', password: '', password2: '' })
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!form.name || !form.email || !form.password) {
      setError('Tüm alanları doldurun')
      return
    }
    if (form.password !== form.password2) {
      setError('Şifreler eşleşmiyor')
      return
    }
    onLogin({ id: '1', email: form.email, name: form.name })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 px-4 py-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 text-2xl font-bold mb-2">
            <Terminal className="text-purple-400" /> Kimi
          </div>
          <p className="text-slate-400">Yeni hesap oluşturun</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-slate-900/50 backdrop-blur rounded-2xl border border-slate-800 p-8 space-y-4">
          {error && <div className="text-red-400 text-sm bg-red-400/10 px-4 py-2 rounded-lg">{error}</div>}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-slate-400 mb-2">Ad</label>
              <input
                value={form.name}
                onChange={e => setForm({...form, name: e.target.value})}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 focus:border-purple-500 focus:outline-none"
                placeholder="Ad"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-2">Soyad</label>
              <input
                value={form.surname}
                onChange={e => setForm({...form, surname: e.target.value})}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 focus:border-purple-500 focus:outline-none"
                placeholder="Soyad"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-2">Kullanıcı Adı</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input
                value={form.username}
                onChange={e => setForm({...form, username: e.target.value})}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-3 focus:border-purple-500 focus:outline-none"
                placeholder="kullanici_adi"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-2">E-posta</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input
                type="email"
                value={form.email}
                onChange={e => setForm({...form, email: e.target.value})}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-3 focus:border-purple-500 focus:outline-none"
                placeholder="ornek@email.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-2">Şifre</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input
                type={showPass ? 'text' : 'password'}
                value={form.password}
                onChange={e => setForm({...form, password: e.target.value})}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-3 focus:border-purple-500 focus:outline-none"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-2">Şifre Tekrar</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input
                type={showPass ? 'text' : 'password'}
                value={form.password2}
                onChange={e => setForm({...form, password2: e.target.value})}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-3 focus:border-purple-500 focus:outline-none"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button type="submit" className="w-full py-3 bg-purple-600 hover:bg-purple-500 rounded-lg font-semibold transition-colors">
            Kayıt Ol
          </button>

          <p className="text-center text-slate-400">
            Zaten hesabınız var mı?{' '}
            <button type="button" onClick={() => onNavigate('login')} className="text-purple-400 hover:text-purple-300">
              Giriş Yap
            </button>
          </p>
        </form>
      </div>
    </div>
  )
}

// User Panel
function UserPanel({ user, onLogout, onNavigate }) {
  const [activeTab, setActiveTab] = useState('profile')

  return (
    <div className="min-h-screen bg-slate-950 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-8">Hesabım</h1>

        <div className="flex gap-8">
          {/* Sidebar */}
          <div className="w-48 space-y-1">
            {[
              { id: 'profile', label: 'Profil', icon: User },
              { id: 'settings', label: 'Ayarlar', icon: Settings },
              { id: 'history', label: 'Geçmiş', icon: MessageSquare },
            ].map(item => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                  activeTab === item.id ? 'bg-purple-600' : 'hover:bg-slate-800'
                }`}
              >
                <item.icon size={18} />
                {item.label}
              </button>
            ))}
            <button
              onClick={onLogout}
              className="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-red-400 hover:bg-red-400/10 transition-colors"
            >
              <LogOut size={18} />
              Çıkış
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 bg-slate-900/50 rounded-xl border border-slate-800 p-6">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold">Profil Bilgileri</h2>
                <div className="flex items-center gap-4">
                  <div className="w-20 h-20 bg-purple-600 rounded-full flex items-center justify-center text-3xl font-bold">
                    {user?.name?.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-semibold">{user?.name}</p>
                    <p className="text-slate-400">{user?.email}</p>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'settings' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold">Ayarlar</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                    <span>Tema</span>
                    <button className="px-4 py-2 bg-slate-700 rounded-lg">Koyu</button>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                    <span>Dil</span>
                    <button className="px-4 py-2 bg-slate-700 rounded-lg">Türkçe</button>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'history' && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold">Sohbet Geçmişi</h2>
                <div className="space-y-2">
                  {[1,2,3].map(i => (
                    <div key={i} className="p-4 bg-slate-800/50 rounded-lg flex items-center justify-between">
                      <div>
                        <p className="font-medium">Sohbet #{i}</p>
                        <p className="text-sm text-slate-400">2 saat önce</p>
                      </div>
                      <button className="text-red-400 hover:text-red-300">
                        <Trash2 size={18} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Simple placeholder pages
function DocsPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <FileText size={64} className="mx-auto mb-4 text-blue-400" />
        <h1 className="text-3xl font-bold mb-2">Docs</h1>
        <p className="text-slate-400">AI Document Agent - Yakında</p>
      </div>
    </div>
  )
}

function SheetsPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <Table2 size={64} className="mx-auto mb-4 text-green-400" />
        <h1 className="text-3xl font-bold mb-2">Sheets</h1>
        <p className="text-slate-400">AI Excel Agent - Yakında</p>
      </div>
    </div>
  )
}

function SlidesPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <Presentation size={64} className="mx-auto mb-4 text-orange-400" />
        <h1 className="text-3xl font-bold mb-2">Slides</h1>
        <p className="text-slate-400">AI Presentation Agent - Yakında</p>
      </div>
    </div>
  )
}

function SwarmPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <Users size={64} className="mx-auto mb-4 text-pink-400" />
        <h1 className="text-3xl font-bold mb-2">Agent Swarm</h1>
        <p className="text-slate-400">Multi-Agent Collaboration - Beta</p>
      </div>
    </div>
  )
}

// ==================== MAIN APP ====================
function App() {
  const [page, setPage] = useState('home')
  const [user, setUser] = useState(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const navigate = (p) => {
    setPage(p)
    setMobileMenuOpen(false)
  }

  const handleLogin = (userData) => {
    setUser(userData)
    setPage('chat')
  }

  const handleLogout = () => {
    setUser(null)
    setPage('home')
  }

  // Navigation items
  const navItems = [
    { id: 'chat', label: 'Chat', icon: MessageSquare },
    { id: 'code', label: 'Code', icon: Code2 },
    { id: 'docs', label: 'Docs', icon: FileText },
    { id: 'sheets', label: 'Sheets', icon: Table2 },
    { id: 'slides', label: 'Slides', icon: Presentation },
    { id: 'features', label: 'Features', icon: Sparkles },
  ]

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      {!['login', 'register'].includes(page) && (
        <header className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur-lg border-b border-slate-800">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex items-center justify-between h-16">
              {/* Logo */}
              <button onClick={() => navigate('home')} className="flex items-center gap-2 font-bold text-xl">
                <Terminal className="text-purple-400" size={28} />
                <span>Kimi</span>
              </button>

              {/* Desktop Nav */}
              <nav className="hidden md:flex items-center gap-1">
                {navItems.map(item => (
                  <button
                    key={item.id}
                    onClick={() => navigate(item.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                      page === item.id ? 'bg-purple-600' : 'hover:bg-slate-800'
                    }`}
                  >
                    <item.icon size={16} />
                    {item.label}
                  </button>
                ))}
              </nav>

              {/* User / Auth */}
              <div className="flex items-center gap-4">
                {user ? (
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => navigate('panel')}
                      className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
                    >
                      <div className="w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center text-xs font-bold">
                        {user.name?.charAt(0).toUpperCase()}
                      </div>
                      <span className="hidden sm:inline">{user.name}</span>
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <button onClick={() => navigate('login')} className="px-4 py-2 hover:bg-slate-800 rounded-lg transition-colors">
                      Giriş
                    </button>
                    <button onClick={() => navigate('register')} className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition-colors">
                      Kayıt Ol
                    </button>
                  </div>
                )}

                {/* Mobile menu button */}
                <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="md:hidden p-2 hover:bg-slate-800 rounded-lg">
                  {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
              </div>
            </div>
          </div>

          {/* Mobile Nav */}
          {mobileMenuOpen && (
            <div className="md:hidden border-t border-slate-800 bg-slate-950/95 backdrop-blur-lg">
              <nav className="p-4 space-y-1">
                {navItems.map(item => (
                  <button
                    key={item.id}
                    onClick={() => navigate(item.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      page === item.id ? 'bg-purple-600' : 'hover:bg-slate-800'
                    }`}
                  >
                    <item.icon size={20} />
                    {item.label}
                  </button>
                ))}
              </nav>
            </div>
          )}
        </header>
      )}

      {/* Main Content */}
      <main className={!['login', 'register'].includes(page) ? 'pt-16' : ''}>
        {page === 'home' && <LandingPage onNavigate={navigate} />}
        {page === 'chat' && <ChatPage user={user} />}
        {page === 'code' && <CodePage />}
        {page === 'docs' && <DocsPage />}
        {page === 'sheets' && <SheetsPage />}
        {page === 'slides' && <SlidesPage />}
        {page === 'swarm' && <SwarmPage />}
        {page === 'features' && <FeaturesPage onNavigate={navigate} />}
        {page === 'login' && <LoginPage onLogin={handleLogin} onNavigate={navigate} />}
        {page === 'register' && <RegisterPage onLogin={handleLogin} onNavigate={navigate} />}
        {page === 'panel' && <UserPanel user={user} onLogout={handleLogout} onNavigate={navigate} />}
      </main>

      {/* Footer */}
      {!['login', 'register', 'chat'].includes(page) && (
        <footer className="border-t border-slate-800 py-12 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-4 gap-8 mb-8">
              <div>
                <div className="flex items-center gap-2 font-bold text-xl mb-4">
                  <Terminal className="text-purple-400" size={24} />
                  Kimi
                </div>
                <p className="text-slate-400 text-sm">AI-powered productivity tools</p>
              </div>
              <div>
                <h4 className="font-semibold mb-4">Products</h4>
                <ul className="space-y-2 text-slate-400 text-sm">
                  <li><button onClick={() => navigate('chat')} className="hover:text-white">Chat</button></li>
                  <li><button onClick={() => navigate('code')} className="hover:text-white">Kimi Code</button></li>
                  <li><button onClick={() => navigate('docs')} className="hover:text-white">Docs</button></li>
                  <li><button onClick={() => navigate('sheets')} className="hover:text-white">Sheets</button></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-4">Resources</h4>
                <ul className="space-y-2 text-slate-400 text-sm">
                  <li><button onClick={() => navigate('features')} className="hover:text-white">Features</button></li>
                  <li><a href="https://github.com/flashomer/kimi" className="hover:text-white">GitHub</a></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-4">Connect</h4>
                <div className="flex gap-4">
                  <a href="#" className="text-slate-400 hover:text-white"><Twitter size={20} /></a>
                  <a href="#" className="text-slate-400 hover:text-white"><Instagram size={20} /></a>
                  <a href="#" className="text-slate-400 hover:text-white"><Github size={20} /></a>
                  <a href="#" className="text-slate-400 hover:text-white"><MessageCircle size={20} /></a>
                </div>
              </div>
            </div>
            <div className="border-t border-slate-800 pt-8 text-center text-slate-500 text-sm">
              © 2024 Kimi · Powered by Moonshot AI · K2.5 256K Context
            </div>
          </div>
        </footer>
      )}
    </div>
  )
}

export default App
