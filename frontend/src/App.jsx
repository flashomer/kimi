import React, { useState, useRef, useEffect } from 'react'
import { Terminal, Copy, Check, Send, Loader2, ChevronRight } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

const API_URL = 'http://localhost:8000'

function App() {
  const [activeTab, setActiveTab] = useState('install')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(() => crypto.randomUUID())
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
        body: JSON.stringify({ message: msg, session_id: sessionId })
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Backend baglantisi yok. `docker-compose up -d` ile baslatin.' }])
    } finally {
      setIsLoading(false)
    }
  }

  const CopyBtn = ({ text }) => {
    const [copied, setCopied] = useState(false)
    return (
      <button
        onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }}
        className="p-2 bg-slate-700 hover:bg-slate-600 rounded transition-all"
      >
        {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
      </button>
    )
  }

  const CodeBox = ({ children, label }) => (
    <div className="bg-[#0d1117] rounded-lg overflow-hidden border border-slate-700">
      {label && <div className="px-3 py-1.5 bg-slate-800 text-xs text-slate-400 border-b border-slate-700">{label}</div>}
      <div className="flex items-center justify-between p-3 gap-3">
        <code className="text-sm text-green-400 flex-1 overflow-x-auto">{children}</code>
        <CopyBtn text={children} />
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-[#0a0e17] text-white font-mono">
      {/* Header */}
      <header className="border-b border-slate-800">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="text-cyan-400" size={24} />
            <span className="font-bold text-lg">Kimi Code</span>
            <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded">K2.5</span>
          </div>
          <div className="flex gap-1 bg-slate-800 p-1 rounded-lg">
            {['install', 'chat'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-1.5 rounded text-sm transition-all ${activeTab === tab ? 'bg-cyan-600' : 'hover:bg-slate-700'}`}
              >
                {tab === 'install' ? 'Kurulum' : 'Chat'}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {activeTab === 'install' ? (
          <div className="space-y-8">
            {/* Hero */}
            <div className="text-center py-6">
              <div className="inline-flex items-center gap-2 bg-cyan-500/10 text-cyan-400 px-3 py-1 rounded-full text-sm mb-4">
                <Terminal size={14} /> Terminal AI Agent
              </div>
              <h1 className="text-3xl font-bold mb-2">Kimi Code CLI</h1>
              <p className="text-slate-400">Tek komutla kur, terminalden kod yaz</p>
            </div>

            {/* Install Commands */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <ChevronRight className="text-cyan-400" size={18} /> Kurulum
              </h2>

              <div className="space-y-3">
                <div>
                  <p className="text-xs text-slate-500 mb-1.5">Linux / macOS</p>
                  <CodeBox>curl -fsSL https://flashomer.github.io/kimi/install.sh | bash</CodeBox>
                </div>

                <div>
                  <p className="text-xs text-slate-500 mb-1.5">Windows PowerShell</p>
                  <CodeBox>irm https://flashomer.github.io/kimi/install.ps1 | iex</CodeBox>
                </div>
              </div>
            </div>

            {/* Usage */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <ChevronRight className="text-cyan-400" size={18} /> Kullanım
              </h2>

              <div className="grid md:grid-cols-2 gap-3">
                <CodeBox label="CLI Başlat">kimi</CodeBox>
                <CodeBox label="Web UI">kimi web</CodeBox>
                <CodeBox label="Agent Swarm">kimi swarm "görev"</CodeBox>
                <CodeBox label="Yardım">kimi --help</CodeBox>
              </div>
            </div>

            {/* CLI Commands */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <ChevronRight className="text-cyan-400" size={18} /> CLI Komutları
              </h2>

              <div className="bg-[#0d1117] rounded-lg border border-slate-700 p-4 text-sm">
                <div className="grid grid-cols-2 gap-2">
                  {[
                    ['/help', 'Yardım göster'],
                    ['/model', 'Model değiştir'],
                    ['/swarm', 'Paralel ajanlar'],
                    ['/shell', 'Shell modu'],
                    ['/clear', 'Sohbeti temizle'],
                    ['/exit', 'Çıkış'],
                  ].map(([cmd, desc]) => (
                    <div key={cmd} className="flex items-center gap-2">
                      <code className="text-cyan-400">{cmd}</code>
                      <span className="text-slate-500">- {desc}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Example */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <ChevronRight className="text-cyan-400" size={18} /> Örnek
              </h2>

              <div className="bg-[#0d1117] rounded-lg border border-slate-700 p-4 text-sm space-y-2">
                <div><span className="text-slate-500">$</span> kimi</div>
                <div><span className="text-cyan-400">{'>'}</span> Flask API oluştur ve app.py'ye kaydet</div>
                <div className="text-slate-500 pl-2">→ read_file, write_file tools çalışıyor...</div>
                <div className="text-green-400 pl-2">✓ app.py oluşturuldu (Flask API)</div>
                <div><span className="text-cyan-400">{'>'}</span> Çalıştır</div>
                <div className="text-slate-500 pl-2">→ run_command("python app.py")</div>
                <div className="text-green-400 pl-2">✓ Server running on http://localhost:5000</div>
              </div>
            </div>

            {/* Features */}
            <div className="grid md:grid-cols-3 gap-3 pt-4">
              {[
                { icon: '🧠', title: 'Kimi K2.5', desc: '256K context' },
                { icon: '🛠️', title: 'Tool Calling', desc: 'Dosya & Shell' },
                { icon: '🐝', title: 'Agent Swarm', desc: 'Paralel ajanlar' },
              ].map((f, i) => (
                <div key={i} className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-4 text-center">
                  <div className="text-2xl mb-2">{f.icon}</div>
                  <div className="font-medium">{f.title}</div>
                  <div className="text-xs text-slate-500">{f.desc}</div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* Chat Tab */
          <div className="h-[calc(100vh-180px)] flex flex-col">
            <div className="flex-1 overflow-y-auto space-y-3 mb-4">
              {messages.length === 0 ? (
                <div className="text-center py-16 text-slate-500">
                  <Terminal size={40} className="mx-auto mb-3 opacity-30" />
                  <p>Mesaj yazın veya terminalde <code className="bg-slate-800 px-1 rounded">kimi</code> kullanın</p>
                </div>
              ) : messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-lg px-4 py-2 ${msg.role === 'user' ? 'bg-cyan-600' : 'bg-slate-800'}`}>
                    {msg.role === 'assistant' ? (
                      <ReactMarkdown
                        components={{
                          code({ inline, className, children }) {
                            if (inline) return <code className="bg-slate-700 px-1 rounded text-cyan-300">{children}</code>
                            return <SyntaxHighlighter style={oneDark} language="python" customStyle={{ borderRadius: '6px', fontSize: '12px' }}>{String(children)}</SyntaxHighlighter>
                          }
                        }}
                      >{msg.content}</ReactMarkdown>
                    ) : msg.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-800 rounded-lg px-4 py-2 flex items-center gap-2">
                    <Loader2 className="animate-spin" size={16} />
                    <span className="text-slate-400">...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="flex gap-2">
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendMessage()}
                placeholder="Mesaj..."
                className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:border-cyan-500 focus:outline-none"
              />
              <button onClick={sendMessage} disabled={isLoading} className="px-4 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-700 rounded-lg">
                <Send size={18} />
              </button>
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-slate-800 py-3 text-center text-xs text-slate-600">
        Kimi K2.5 · 256K Context · Moonshot AI
      </footer>
    </div>
  )
}

export default App
