"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [query, setQuery] = useState("")
  const [userId, setUserId] = useState("")
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  async function handleSend() {
    if (!query || !userId) return

    const userMessage = { role: "user", content: query }
    setMessages(prev => [...prev, userMessage])
    setQuery("")
    setLoading(true)

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, user_id: userId, history: messages })
      })
      const data = await response.json()
      const assistantMessage = { role: "assistant", content: data.answer }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      setMessages(prev => [...prev, { role: "assistant", content: "Something went wrong. Try again." }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-8">
      <h1 className="text-4xl font-bold text-green-600 mb-2">Platemate 🥗</h1>
      <p className="text-gray-500 mb-6">Ask anything about your meal plan</p>

      <div className="w-full max-w-2xl flex flex-col gap-4">
        
        <input
          type="text"
          placeholder="Your name (e.g. nivi)"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
        />

        <div className="bg-white rounded-2xl shadow p-4 flex flex-col gap-3 min-h-96">
          {messages.length === 0 && (
            <p className="text-gray-400 text-sm text-center mt-8">
              Ask a question about your meal plan...
            </p>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={`rounded-2xl px-4 py-2 max-w-sm text-sm ${
                msg.role === "user"
                  ? "bg-green-600 text-white"
                  : "bg-gray-100 text-gray-800"
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-2xl px-4 py-2 text-sm text-gray-500">
                Thinking...
              </div>
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Ask about your meal plan..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            className="flex-1 border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="bg-green-600 text-white rounded-lg px-6 py-2 text-sm font-medium hover:bg-green-700 transition disabled:opacity-50"
          >
            Send
          </button>
        </div>

        <button
          onClick={() => router.push("/")}
          className="text-sm text-gray-400 hover:text-gray-600 text-center"
        >
          ← Upload a new meal plan
        </button>

      </div>
    </div>
  )
}