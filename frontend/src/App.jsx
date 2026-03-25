import React, { useState, useRef, useEffect } from 'react'
import { Terminal, Copy, Check, Send, Loader2, ExternalLink, Command, Zap } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

const API_URL = 'http://localhost:8000'

function App() {
  const [activeTab, setActiveTab] = useState('install') // install | chat
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(() => crypto.randomUUID())
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

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
        body: JSON.stringify({ message: msg, session_id: sessionId })
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Hata: Backend çalışmıyor. \`docker-compose up -d\` ile başlatın.` }])
    } finally {
      setIsLoading(false)
    }
  }

  // Copy button component
  const CopyButton = ({ text }) => {
    const [copied, setCopied] = useState(false)
    return (
      <button
        onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }}
        className="absolute right-2 top-2 p-2 bg-slate-700 hover:bg-slate-600 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
      >
        {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
      </button>
    )
  }

  // Code block for install commands
  const CodeBlock = ({ children, lang = 'bash' }) => (
    <div className="relative group my-3">
      <CopyButton text={children} />
      <SyntaxHighlighter style={oneDark} language={lang} customStyle={{ borderRadius: '8px', padding: '1rem', paddingRight: '3rem' }}>
        {children}
      </SyntaxHighlighter>
    </div>
  )

  return (
    <div className="min-h-screen bg-[#0a0f1a] text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-[#0d1321]">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Terminal size={22} />
            </div>
            <div>
              <h1 className="text-xl font-bold">Kimi Code</h1>
              <p className="text-xs text-slate-500">Powered by Kimi K2.5</p>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex bg-slate-800 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('install')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'install' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              <Command size={14} className="inline mr-1" /> Kurulum
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'chat' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              <Zap size={14} className="inline mr-1" /> Chat
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        {activeTab === 'install' ? (
          /* INSTALL TAB */
          <div className="space-y-8">
            {/* Hero */}
            <div className="text-center py-8">
              <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                Terminal'de AI ile Kod Yaz
              </h2>
              <p className="text-slate-400 text-lg max-w-2xl mx-auto">
                Kimi K2.5 modeli ile 256K context, dosya okuma/yazma, shell komutları ve Agent Swarm desteği.
              </p>
            </div>

            {/* Quick Install */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Zap className="text-yellow-400" /> Hızlı Kurulum
              </h3>

              <div className="space-y-4">
                <div>
                  <p className="text-sm text-slate-400 mb-2">Linux / macOS:</p>
                  <CodeBlock>curl -fsSL https://flashomer.github.io/kimi/install.sh | bash</CodeBlock>
                </div>

                <div>
                  <p className="text-sm text-slate-400 mb-2">Windows (PowerShell):</p>
                  <CodeBlock>irm https://flashomer.github.io/kimi/install.ps1 | iex</CodeBlock>
                </div>

                <div>
                  <p className="text-sm text-slate-400 mb-2">Manuel:</p>
                  <CodeBlock>{`pip install openai rich && curl -fsSL https://flashomer.github.io/kimi/kimi_cli.py -o kimi.py && python kimi.py`}</CodeBlock>
                </div>
              </div>
            </div>

            {/* Features */}
            <div className="grid md:grid-cols-3 gap-4">
              {[
                { title: 'Kimi K2.5', desc: '256K context window ile büyük kod tabanlarını analiz et', icon: '🧠' },
                { title: 'Tool Calling', desc: 'Dosya oku/yaz, shell komutları çalıştır', icon: '🛠️' },
                { title: 'Agent Swarm', desc: 'Paralel ajanlarla karmaşık görevleri böl', icon: '🐝' },
              ].map((f, i) => (
                <div key={i} className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-5">
                  <div className="text-3xl mb-3">{f.icon}</div>
                  <h4 className="font-semibold mb-1">{f.title}</h4>
                  <p className="text-sm text-slate-400">{f.desc}</p>
                </div>
              ))}
            </div>

            {/* CLI Commands */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
              <h3 className="text-xl font-semibold mb-4">CLI Komutları</h3>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-400 mb-2">Terminal Komutları:</p>
                  <CodeBlock>{`kimi              # CLI başlat
kimi web          # Web UI aç
kimi login        # API key ayarla
kimi swarm "..."  # Agent Swarm`}</CodeBlock>
                </div>

                <div>
                  <p className="text-sm text-slate-400 mb-2">CLI İçi Komutlar:</p>
                  <CodeBlock>{`/help     # Yardım
/model    # Model değiştir
/swarm    # Agent Swarm
/shell    # Shell modu
/clear    # Temizle`}</CodeBlock>
                </div>
              </div>
            </div>

            {/* Example Usage */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
              <h3 className="text-xl font-semibold mb-4">Örnek Kullanım</h3>
              <div className="bg-[#0a0f1a] rounded-xl p-4 font-mono text-sm">
                <div className="text-slate-500">$ kimi</div>
                <div className="text-cyan-400 mt-2">{'>'} Bu dizindeki Python dosyalarını listele</div>
                <div className="text-slate-300 mt-1 ml-2">list_files(pattern="*.py")</div>
                <div className="text-green-400 mt-1 ml-2">[OK] 5 dosya bulundu...</div>
                <div className="text-cyan-400 mt-3">{'>'} main.py dosyasına Flask API ekle</div>
                <div className="text-slate-300 mt-1 ml-2">read_file("main.py")</div>
                <div className="text-slate-300 mt-1 ml-2">edit_file("main.py", ...)</div>
                <div className="text-green-400 mt-1 ml-2">[OK] Flask API eklendi</div>
              </div>
            </div>

            {/* API Key */}
            <div className="bg-gradient-to-r from-cyan-900/30 to-blue-900/30 border border-cyan-700/30 rounded-2xl p-6">
              <h3 className="text-xl font-semibold mb-2">API Key Nasıl Alınır?</h3>
              <ol className="list-decimal list-inside text-slate-300 space-y-2">
                <li>
                  <a href="https://platform.moonshot.ai" target="_blank" className="text-cyan-400 hover:underline inline-flex items-center gap-1">
                    platform.moonshot.ai <ExternalLink size={12} />
                  </a> adresine gidin
                </li>
                <li>Hesap oluşturun veya giriş yapın</li>
                <li>API Keys bölümünden yeni key oluşturun</li>
                <li><code className="bg-slate-800 px-2 py-0.5 rounded">kimi login</code> ile CLI'ya ekleyin</li>
              </ol>
            </div>
          </div>
        ) : (
          /* CHAT TAB */
          <div className="h-[calc(100vh-200px)] flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {messages.length === 0 ? (
                <div className="text-center py-16 text-slate-500">
                  <Terminal size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Mesaj yazarak başlayın</p>
                  <p className="text-sm mt-2">Asıl güç terminalde! <code className="bg-slate-800 px-2 py-0.5 rounded">kimi</code> komutu ile CLI kullanın.</p>
                </div>
              ) : (
                messages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-3xl rounded-2xl px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-cyan-600'
                        : 'bg-slate-800 border border-slate-700'
                    }`}>
                      {msg.role === 'assistant' ? (
                        <ReactMarkdown
                          components={{
                            code({ inline, className, children }) {
                              if (inline) return <code className="bg-slate-700 px-1 rounded">{children}</code>
                              const lang = /language-(\w+)/.exec(className || '')?.[1] || 'text'
                              return (
                                <SyntaxHighlighter style={oneDark} language={lang} customStyle={{ borderRadius: '8px' }}>
                                  {String(children).replace(/\n$/, '')}
                                </SyntaxHighlighter>
                              )
                            }
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      ) : (
                        <p>{msg.content}</p>
                      )}
                    </div>
                  </div>
                ))
              )}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-800 border border-slate-700 rounded-2xl px-4 py-3 flex items-center gap-2">
                    <Loader2 className="animate-spin text-cyan-400" size={18} />
                    <span className="text-slate-400">Düşünüyor...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="flex gap-3">
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Mesaj yazın..."
                className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 focus:border-cyan-500 focus:outline-none"
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="px-4 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-700 rounded-xl transition-colors"
              >
                <Send size={20} />
              </button>
            </div>
            <p className="text-center text-xs text-slate-600 mt-2">
              Tam özellikler için terminalde <code className="bg-slate-800 px-1 rounded">kimi</code> kullanın
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-4 text-center text-sm text-slate-500">
        Kimi K2.5 · Moonshot AI · 256K Context
      </footer>
    </div>
  )
}

export default App
