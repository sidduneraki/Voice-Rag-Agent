import { useState } from "react"

export default function DocumentUpload() {
  const [status, setStatus] = useState("")
  const [loading, setLoading] = useState(false)

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setStatus("")
    const form = new FormData()
    form.append("file", file)
    try {
      const res = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: form,
      })
      const data = await res.json()
      setStatus(`✅ ${data.filename} — ${data.chunks_ingested} chunks ingested`)
    } catch {
      setStatus("❌ Upload failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
      <h2 className="text-sm font-semibold text-gray-500 mb-3 uppercase tracking-wide">Knowledge Base</h2>
      <label className="flex items-center gap-3 cursor-pointer">
        <div className="bg-indigo-50 hover:bg-indigo-100 text-indigo-600 text-sm font-medium px-4 py-2 rounded-lg transition">
          {loading ? "Uploading..." : "Upload PDF"}
        </div>
        <input type="file" accept=".pdf,.txt" className="hidden" onChange={handleUpload} disabled={loading}/>
      </label>
      {status && <p className="mt-2 text-sm text-gray-600">{status}</p>}
    </div>
  )
}