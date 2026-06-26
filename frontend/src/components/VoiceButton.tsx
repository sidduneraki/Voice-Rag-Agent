import { useEffect, useRef, useState } from "react"
import type { Message } from "./ChatHistory"

const WS_URL = "ws://localhost:8000/ws/voice"

export default function VoiceButton({ onMessage }: { onMessage: (m: Message) => void }) {
  const [active, setActive] = useState(false)
  const [bars, setBars] = useState<number[]>(Array(20).fill(2))
  const wsRef = useRef<WebSocket | null>(null)
  const mediaRef = useRef<MediaRecorder | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animRef = useRef<number>(0)

  const startVisualizer = (stream: MediaStream) => {
    const ctx = new AudioContext()
    const source = ctx.createMediaStreamSource(stream)
    const analyser = ctx.createAnalyser()
    analyser.fftSize = 64
    source.connect(analyser)
    analyserRef.current = analyser

    const data = new Uint8Array(analyser.frequencyBinCount)
    const tick = () => {
      analyser.getByteFrequencyData(data)
      setBars(Array.from(data.slice(0, 20)).map(v => Math.max(2, (v / 255) * 48)))
      animRef.current = requestAnimationFrame(tick)
    }
    tick()
  }

  const start = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    startVisualizer(stream)

    const ws = new WebSocket(WS_URL)
    ws.binaryType = "arraybuffer"
    wsRef.current = ws

    ws.onopen = () => {
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" })
      recorder.ondataavailable = async (e) => {
        if (ws.readyState === WebSocket.OPEN && e.data.size > 0) {
          const buf = await e.data.arrayBuffer()
          ws.send(buf)
        }
      }
      recorder.start(250)
      mediaRef.current = recorder
    }

    ws.onmessage = (e) => {
      if (e.data instanceof ArrayBuffer) {
        const blob = new Blob([e.data], { type: "audio/mp3" })
        const url = URL.createObjectURL(blob)
        const audio = new Audio(url)
        audio.play()
      } else {
        try {
          const msg = JSON.parse(e.data)
          if (msg.transcript) onMessage({ role: "user", text: msg.transcript })
          if (msg.response) onMessage({ role: "assistant", text: msg.response })
        } catch {}
      }
    }

    setActive(true)
  }

  const stop = () => {
    mediaRef.current?.stop()
    wsRef.current?.close()
    cancelAnimationFrame(animRef.current)
    setBars(Array(20).fill(2))
    setActive(false)
  }

  useEffect(() => () => stop(), [])

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="flex items-end gap-[3px] h-14">
        {bars.map((h, i) => (
          <div key={i} className={`w-1 rounded-full transition-all duration-75 ${active ? "bg-indigo-400" : "bg-gray-200"}`}
            style={{ height: `${h}px` }} />
        ))}
      </div>
      <button
        onClick={active ? stop : start}
        className={`w-16 h-16 rounded-full flex items-center justify-center text-white text-2xl shadow-lg transition-all ${
          active ? "bg-red-500 hover:bg-red-600 scale-110" : "bg-indigo-500 hover:bg-indigo-600"
        }`}>
        {active ? "⏹" : "🎙"}
      </button>
      <p className="text-xs text-gray-400">{active ? "Listening... tap to stop" : "Tap to speak"}</p>
    </div>
  )
}