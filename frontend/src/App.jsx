import React, { useState, useRef, useEffect } from 'react'
import {
  Plus, Globe, FileText, Presentation, Table2, Search, Code2, Bot,
  Clock, Smartphone, ChevronDown, Send, Sparkles, Users, Image,
  Settings, LogOut, User, Mail, Lock, Eye, EyeOff, X, Menu,
  MessageSquare, Zap, ArrowUp
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

const API_URL = 'http://localhost:8000'

// ==================== MAIN APP - KIMI CLONE ====================
function App() {
  const [user, setUser] = useState(null)
  const [currentPage, setCurrentPage] = useState('chat')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [chatHistory, setChatHistory] = useState([
    { id: 1, title: 'Flask API oluşturma', date: 'Bugün' },
    { id: 2, title: 'React component', date: 'Dün' },
    { id: 3, title: 'Python script', date: '2 gün önce' },
  ])
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState('login')
  const [selectedModel, setSelectedModel] = useState('K2.5 Instant')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setMessages([])
        inputRef.current?.focus()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

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

  const handleLogin = (userData) => {
    setUser(userData)
    setShowAuthModal(false)
  }

  // Sidebar menu items
  const menuItems = [
    { id: 'chat', icon: Plus, label: 'New Chat', shortcut: 'Ctrl K', action: () => { setMessages([]); setCurrentPage('chat') } },
    { id: 'divider1' },
    { id: 'websites', icon: Globe, label: 'Websites' },
    { id: 'docs', icon: FileText, label: 'Docs' },
    { id: 'slides', icon: Presentation, label: 'Slides' },
    { id: 'sheets', icon: Table2, label: 'Sheets' },
    { id: 'research', icon: Search, label: 'Deep Research' },
    { id: 'code', icon: Code2, label: 'Kimi Code' },
    { id: 'claw', icon: Bot, label: 'Kimi Claw', badge: 'Beta' },
    { id: 'divider2' },
    { id: 'history', icon: Clock, label: 'Chat History', expandable: true },
  ]

  // Quick actions
  const quickActions = [
    { icon: Globe, label: 'Websites' },
    { icon: FileText, label: 'Docs' },
    { icon: Presentation, label: 'Slides' },
    { icon: Table2, label: 'Sheets' },
    { icon: Search, label: 'Deep Research' },
    { icon: Users, label: 'Agent Swarm', badge: 'Beta' },
  ]

  // Featured cases
  const featuredCases = [
    { title: 'Kimi Agent', subtitle: 'Now with Office Pilot', color: 'from-blue-500 to-cyan-500', image: '🤖' },
    { title: 'Taylor Swift Spotify', subtitle: 'with all songs', color: 'from-green-500 to-emerald-500', image: '🎵' },
    { title: 'Checkerboard Lipstick', subtitle: 'Landing Page', color: 'from-pink-500 to-rose-500', image: '💄' },
  ]

  return (
    <div className="h-screen flex bg-[#1a1a1a] text-white overflow-hidden">
      {/* Sidebar */}
      <aside className={`${sidebarCollapsed ? 'w-0' : 'w-56'} bg-[#232323] flex flex-col transition-all duration-300 overflow-hidden`}>
        {/* Logo */}
        <div className="p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <span className="text-black font-bold text-lg">K</span>
            </div>
          </div>
          <button onClick={() => setSidebarCollapsed(true)} className="p-1 hover:bg-white/10 rounded">
            <Menu size={18} />
          </button>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 px-2 space-y-1 overflow-y-auto">
          {menuItems.map((item, i) => {
            if (item.id.startsWith('divider')) {
              return <div key={i} className="h-px bg-white/10 my-2" />
            }
            return (
              <button
                key={item.id}
                onClick={item.action || (() => setCurrentPage(item.id))}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  currentPage === item.id ? 'bg-white/10' : 'hover:bg-white/5'
                }`}
              >
                <item.icon size={18} className="text-gray-400" />
                <span className="flex-1 text-left">{item.label}</span>
                {item.shortcut && <span className="text-xs text-gray-500">{item.shortcut}</span>}
                {item.badge && <span className="text-xs text-cyan-400">{item.badge}</span>}
              </button>
            )
          })}

          {/* Chat History */}
          <div className="pl-9 space-y-1">
            <button className="w-full text-left text-sm text-gray-400 hover:text-white py-1 px-2 rounded hover:bg-white/5">
              All Chats
            </button>
            {chatHistory.map(chat => (
              <button
                key={chat.id}
                className="w-full text-left text-sm text-gray-500 hover:text-white py-1 px-2 rounded hover:bg-white/5 truncate"
              >
                {chat.title}
              </button>
            ))}
          </div>
        </nav>

        {/* Bottom */}
        <div className="p-2 border-t border-white/10">
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm hover:bg-white/5">
            <Smartphone size={18} className="text-gray-400" />
            <span>Mobile App</span>
          </button>

          {/* User */}
          {user ? (
            <button
              onClick={() => setShowAuthModal(true)}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm hover:bg-white/5 mt-1"
            >
              <div className="w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center text-xs font-bold">
                {user.name?.charAt(0).toUpperCase()}
              </div>
              <span className="flex-1 text-left truncate">{user.name}</span>
              <button className="px-2 py-0.5 bg-white/10 rounded text-xs hover:bg-white/20">
                Upgrade
              </button>
            </button>
          ) : (
            <button
              onClick={() => setShowAuthModal(true)}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm hover:bg-white/5 mt-1"
            >
              <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center">
                <User size={14} />
              </div>
              <span>Giriş Yap</span>
            </button>
          )}
        </div>
      </aside>

      {/* Collapsed sidebar toggle */}
      {sidebarCollapsed && (
        <button
          onClick={() => setSidebarCollapsed(false)}
          className="absolute left-2 top-4 z-10 p-2 bg-[#232323] rounded-lg hover:bg-white/10"
        >
          <Menu size={18} />
        </button>
      )}

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="flex items-center justify-end p-4">
          <button className="flex items-center gap-2 text-cyan-400 hover:text-cyan-300 text-sm">
            <Sparkles size={16} />
            Upgrade your plan
          </button>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto px-4">
          {messages.length === 0 ? (
            /* Empty State - Home */
            <div className="max-w-3xl mx-auto pt-20">
              {/* KIMI Logo */}
              <h1 className="text-6xl font-bold text-center mb-16 tracking-wider">KIMI</h1>

              {/* Input Box */}
              <div className="bg-[#2a2a2a] rounded-2xl p-4 mb-6">
                <input
                  ref={inputRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                  placeholder="Ask away. Pics work too."
                  className="w-full bg-transparent text-white placeholder-gray-500 outline-none text-lg"
                />
                <div className="flex items-center justify-between mt-4">
                  <div className="flex items-center gap-2">
                    <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                      <Plus size={20} className="text-gray-400" />
                    </button>
                    <button className="flex items-center gap-2 px-3 py-1.5 bg-white/10 hover:bg-white/15 rounded-lg transition-colors">
                      <Bot size={16} />
                      <span className="text-sm">Agent</span>
                    </button>
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="flex items-center gap-1 px-3 py-1.5 hover:bg-white/10 rounded-lg text-sm">
                      {selectedModel}
                      <ChevronDown size={14} />
                    </button>
                    <button
                      onClick={sendMessage}
                      disabled={!input.trim()}
                      className={`p-2 rounded-full transition-colors ${
                        input.trim() ? 'bg-white text-black hover:bg-gray-200' : 'bg-white/10 text-gray-500'
                      }`}
                    >
                      <ArrowUp size={18} />
                    </button>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex flex-wrap justify-center gap-2 mb-12">
                {quickActions.map((action, i) => (
                  <button
                    key={i}
                    className="flex items-center gap-2 px-4 py-2 bg-[#2a2a2a] hover:bg-[#333] rounded-full text-sm transition-colors"
                  >
                    <action.icon size={16} className="text-gray-400" />
                    <span>{action.label}</span>
                    {action.badge && <span className="text-cyan-400 text-xs">{action.badge}</span>}
                  </button>
                ))}
              </div>

              {/* Featured Agent Cases */}
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-gray-400 text-sm">Featured Agent cases</h2>
                  <button className="text-gray-400 hover:text-white text-sm flex items-center gap-1">
                    More cases
                    <ChevronDown size={14} className="rotate-[-90deg]" />
                  </button>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  {featuredCases.map((item, i) => (
                    <div
                      key={i}
                      className={`bg-gradient-to-br ${item.color} rounded-xl p-4 h-32 flex flex-col justify-between cursor-pointer hover:scale-105 transition-transform`}
                    >
                      <div className="text-3xl">{item.image}</div>
                      <div>
                        <p className="font-semibold">{item.title}</p>
                        <p className="text-sm opacity-80">{item.subtitle}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Chat Messages */
            <div className="max-w-3xl mx-auto py-4 space-y-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    msg.role === 'user' ? 'bg-[#2a2a2a]' : 'bg-transparent'
                  }`}>
                    {msg.role === 'assistant' ? (
                      <div className="flex gap-3">
                        <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center flex-shrink-0">
                          <span className="text-black font-bold">K</span>
                        </div>
                        <div className="flex-1">
                          <ReactMarkdown
                            components={{
                              code({ inline, className, children }) {
                                if (inline) return <code className="bg-white/10 px-1.5 py-0.5 rounded text-cyan-300">{children}</code>
                                const lang = className?.replace('language-', '') || 'text'
                                return (
                                  <SyntaxHighlighter style={oneDark} language={lang} customStyle={{ borderRadius: '8px', margin: '8px 0' }}>
                                    {String(children).replace(/\n$/, '')}
                                  </SyntaxHighlighter>
                                )
                              }
                            }}
                          >{msg.content}</ReactMarkdown>
                        </div>
                      </div>
                    ) : (
                      <span>{msg.content}</span>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-black font-bold">K</span>
                  </div>
                  <div className="flex gap-1 items-center">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input (when chatting) */}
        {messages.length > 0 && (
          <div className="p-4 border-t border-white/10">
            <div className="max-w-3xl mx-auto">
              <div className="bg-[#2a2a2a] rounded-2xl p-3 flex items-center gap-3">
                <button className="p-2 hover:bg-white/10 rounded-lg">
                  <Plus size={18} className="text-gray-400" />
                </button>
                <input
                  ref={inputRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                  placeholder="Ask away. Pics work too."
                  className="flex-1 bg-transparent outline-none"
                />
                <button className="flex items-center gap-1 px-2 py-1 hover:bg-white/10 rounded text-sm text-gray-400">
                  {selectedModel}
                  <ChevronDown size={14} />
                </button>
                <button
                  onClick={sendMessage}
                  disabled={!input.trim()}
                  className={`p-2 rounded-full transition-colors ${
                    input.trim() ? 'bg-white text-black' : 'bg-white/10 text-gray-500'
                  }`}
                >
                  <ArrowUp size={16} />
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#232323] rounded-2xl p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">
                {authMode === 'login' ? 'Giriş Yap' : 'Kayıt Ol'}
              </h2>
              <button onClick={() => setShowAuthModal(false)} className="p-1 hover:bg-white/10 rounded">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={(e) => { e.preventDefault(); handleLogin({ id: '1', name: 'Kullanıcı', email: 'user@example.com' }) }} className="space-y-4">
              {authMode === 'register' && (
                <div className="grid grid-cols-2 gap-3">
                  <input
                    placeholder="Ad"
                    className="bg-[#1a1a1a] rounded-lg px-4 py-3 outline-none focus:ring-2 ring-cyan-500"
                  />
                  <input
                    placeholder="Soyad"
                    className="bg-[#1a1a1a] rounded-lg px-4 py-3 outline-none focus:ring-2 ring-cyan-500"
                  />
                </div>
              )}

              {authMode === 'register' && (
                <input
                  placeholder="Kullanıcı Adı"
                  className="w-full bg-[#1a1a1a] rounded-lg px-4 py-3 outline-none focus:ring-2 ring-cyan-500"
                />
              )}

              <input
                type="email"
                placeholder="E-posta"
                className="w-full bg-[#1a1a1a] rounded-lg px-4 py-3 outline-none focus:ring-2 ring-cyan-500"
              />

              <input
                type="password"
                placeholder="Şifre"
                className="w-full bg-[#1a1a1a] rounded-lg px-4 py-3 outline-none focus:ring-2 ring-cyan-500"
              />

              {authMode === 'register' && (
                <input
                  type="password"
                  placeholder="Şifre Tekrar"
                  className="w-full bg-[#1a1a1a] rounded-lg px-4 py-3 outline-none focus:ring-2 ring-cyan-500"
                />
              )}

              <button
                type="submit"
                className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 rounded-lg font-semibold transition-colors"
              >
                {authMode === 'login' ? 'Giriş Yap' : 'Kayıt Ol'}
              </button>
            </form>

            <p className="text-center text-gray-400 mt-4">
              {authMode === 'login' ? (
                <>Hesabınız yok mu? <button onClick={() => setAuthMode('register')} className="text-cyan-400 hover:underline">Kayıt Ol</button></>
              ) : (
                <>Zaten hesabınız var mı? <button onClick={() => setAuthMode('login')} className="text-cyan-400 hover:underline">Giriş Yap</button></>
              )}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
