import { useState, useRef, useEffect } from "react"

interface Message {
  role: "user" | "assistant"
  text: string
}

function DocumentUpload({ onStatus }: { onStatus: (s: string) => void }) {
  const [loading, setLoading] = useState(false)

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)

    const form = new FormData()
    form.append("file", file)

    try {
      const res = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: form
      })
      const data = await res.json()
      onStatus(`✅ ${data.filename} — ${data.chunks_ingested} chunks`)
    } catch {
      onStatus("❌ Upload failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
      <h2 className="text-sm font-semibold text-gray-500 mb-3 uppercase tracking-wide">
        Knowledge Base
      </h2>

      <label className="cursor-pointer">
        <div className="bg-indigo-50 hover:bg-indigo-100 text-indigo-600 text-sm font-medium px-4 py-2 rounded-lg inline-block transition">
          {loading ? "Uploading..." : "Upload PDF"}
        </div>
        <input type="file" accept=".pdf,.txt" className="hidden" onChange={handleUpload} disabled={loading} />
      </label>
    </div>
  )
}

function ChatHistory({ messages }: { messages: Message[] }) {
  return (
    <div className="flex flex-col gap-3 overflow-y-auto flex-1 py-2 px-1 h-full">
      {messages.length === 0 && (
        <p className="text-center text-gray-400 text-sm mt-8">
          Upload a document and start speaking...
        </p>
      )}

      {messages.map((m, i) => (
        <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
          <div
            className={`max-w-[75%] px-4 py-2 rounded-2xl text-sm ${
              m.role === "user"
                ? "bg-indigo-500 text-white"
                : "bg-white text-gray-800 border border-gray-100 shadow-sm"
            }`}
          >
            {m.text}
          </div>
        </div>
      ))}
    </div>
  )
}

function VoiceButton({ onMessage }: { onMessage: (m: Message) => void }) {
  const [active, setActive] = useState(false)
  const [bars, setBars] = useState<number[]>(Array(20).fill(2))
  const [ttsActive, setTtsActive] = useState(false)

  const processorRef = useRef<ScriptProcessorNode | null>(null)
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const ctxRef = useRef<AudioContext | null>(null)

  const audioQueueRef = useRef<string[]>([])
  const playingRef = useRef(false)
  const mutedRef = useRef(false)
  const currentAudioRef = useRef<HTMLAudioElement | null>(null)

  const playNext = () => {
    if (audioQueueRef.current.length === 0) {
      playingRef.current = false
      return
    }

    playingRef.current = true
    const url = audioQueueRef.current.shift()!
    const audio = new Audio(url)
    currentAudioRef.current = audio

    audio.onended = () => {
      URL.revokeObjectURL(url)
      playNext()
    }

    audio.play()
  }

  const start = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true }
    })

    const ctx = new AudioContext({ sampleRate: 16000 })
    ctxRef.current = ctx
    await ctx.resume() // ✅ important fix

    const source = ctx.createMediaStreamSource(stream)
    sourceRef.current = source

    const analyser = ctx.createAnalyser()
    analyser.fftSize = 64
    source.connect(analyser)

    const data = new Uint8Array(analyser.frequencyBinCount)
    const tick = () => {
      analyser.getByteFrequencyData(data)
      setBars(Array.from(data.slice(0, 20)).map(v => Math.max(2, (v / 255) * 48)))
      requestAnimationFrame(tick)
    }
    tick()

    const ws = new WebSocket("ws://localhost:8000/ws/voice")
    ws.binaryType = "arraybuffer"
    wsRef.current = ws

    ws.onopen = () => {
    const processor = ctx.createScriptProcessor(2048, 1, 1)
    processorRef.current = processor

    source.connect(processor)

    // Must connect to destination for onaudioprocess to fire
    // Use a gain node at 0 volume to prevent echo
    const silentGain = ctx.createGain()
    silentGain.gain.value = 0
    processor.connect(silentGain)
    silentGain.connect(ctx.destination)

    processor.onaudioprocess = (e) => {
    if (ws.readyState !== WebSocket.OPEN) return
    if (mutedRef.current) return
    const float32 = e.inputBuffer.getChannelData(0)
    const int16 = new Int16Array(float32.length)
    for (let i = 0; i < float32.length; i++) {
      int16[i] = Math.max(-32768, Math.min(32767, float32[i] * 32768))
    }
    console.log("Sending audio chunk", int16.buffer.byteLength, "bytes")
    ws.send(int16.buffer)
  }
}

    ws.onmessage = (e) => {
      if (!(e.data instanceof ArrayBuffer)) return

      const bytes = new Uint8Array(e.data)
      const text = new TextDecoder().decode(bytes)

      // ✅ robust signal detection
      if (text === "__TTS_START__") {
        mutedRef.current = true
        setTtsActive(true)
        return
      }

      if (text === "__TTS_END__") {
        mutedRef.current = false
        setTtsActive(false)
        return
      }

      // real audio
      const blob = new Blob([e.data], { type: "audio/mp3" })
      const url = URL.createObjectURL(blob)

      audioQueueRef.current.push(url)
      if (!playingRef.current) playNext()
    }

    ws.onerror = (e) => console.error("WS error", e)

    setActive(true)
  }

  const stop = () => {
    currentAudioRef.current?.pause()
    currentAudioRef.current = null

    audioQueueRef.current = []
    playingRef.current = false
    mutedRef.current = false

    wsRef.current?.send("STOP")
    wsRef.current?.close()

    processorRef.current?.disconnect()
    sourceRef.current?.disconnect()
    ctxRef.current?.close()

    setActive(false)
    setTtsActive(false)
    setBars(Array(20).fill(2))
  }

  // ✅ cleanup on unmount
  useEffect(() => {
    return () => {
      wsRef.current?.close()
      ctxRef.current?.close()
    }
  }, [])

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="flex items-end gap-[3px] h-14">
        {bars.map((h, i) => (
          <div
            key={i}
            className={`w-1 rounded-full transition-all duration-75 ${
              ttsActive ? "bg-green-400" : active ? "bg-indigo-400" : "bg-gray-200"
            }`}
            style={{ height: `${h}px` }}
          />
        ))}
      </div>

      <button
        onClick={active ? stop : start}
        className={`w-16 h-16 rounded-full text-white text-2xl shadow-lg transition-all ${
          active
            ? "bg-red-500 hover:bg-red-600 scale-110"
            : "bg-indigo-500 hover:bg-indigo-600"
        }`}
      >
        {active ? "⏹" : "🎙"}
      </button>

      <p className="text-xs text-gray-400">
        {ttsActive
          ? "Agent speaking..."
          : active
          ? "Listening... tap to stop"
          : "Tap to speak"}
      </p>
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [status, setStatus] = useState("")

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-8 px-4">
      <div className="w-full max-w-lg flex flex-col gap-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800">Voice RAG Agent</h1>
          <p className="text-sm text-gray-400">Speak to your documents</p>
        </div>

        <DocumentUpload onStatus={setStatus} />
        {status && <p className="text-sm text-center text-gray-600">{status}</p>}

        <div className="bg-gray-50 rounded-xl overflow-hidden" style={{ height: "400px" }}>
          <ChatHistory messages={messages} />
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <VoiceButton onMessage={(m) => setMessages(prev => [...prev, m])} />
        </div>
      </div>
    </div>
  )
}