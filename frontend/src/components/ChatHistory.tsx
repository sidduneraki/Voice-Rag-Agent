export interface Message {
  role: "user" | "assistant"
  text: string
}

export default function ChatHistory({ messages }: { messages: Message[] }) {
  return (
    <div className="flex flex-col gap-3 overflow-y-auto flex-1 py-2">
      {messages.length === 0 && (
        <p className="text-center text-gray-400 text-sm mt-8">Upload a document and start speaking...</p>
      )}
      {messages.map((m, i) => (
        <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
          <div className={`max-w-[75%] px-4 py-2 rounded-2xl text-sm leading-relaxed ${
            m.role === "user"
              ? "bg-indigo-500 text-white rounded-br-sm"
              : "bg-white text-gray-800 border border-gray-100 rounded-bl-sm shadow-sm"
          }`}>
            {m.text}
          </div>
        </div>
      ))}
    </div>
  )
}