"use client"
import { useState } from "react"

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

export default function Home() {
  const [userId, setUserId] = useState("")
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState("")

  async function handleUpload() {
  if (!userId || !file) {
    setMessage("Please enter your name and upload a PDF")
    return
  }

  setLoading(true)
  setMessage("")

  const formData = new FormData()
  formData.append("file", file)
  formData.append("user_id", userId)

  try {
    const response = await fetch("http://localhost:8000/ingest", {
      method: "POST",
      body: formData
    })
    const data = await response.json()
    setMessage("✅ Meal plan uploaded successfully!")
  } catch (error) {
    setMessage("❌ Something went wrong. Is your backend running?")
  } finally {
    setLoading(false)
  }
}

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-green-600 mb-2">Platemate 🥗</h1>
      <p className="text-gray-500 mb-8 text-center max-w-md">
        Upload your personal meal plan and ask questions about your nutrition
      </p>

    <div className="bg-white rounded-2xl shadow p-8 w-full max-w-md flex flex-col gap-4">
  
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-gray-700">Your Name</label>
      <input
        type="text"
        placeholder="e.g. nivi"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        className="border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
      />
    </div>

    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-gray-700">Upload Meal Plan PDF</label>
      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files[0])}
        className="text-sm text-gray-500"
      />
    </div>

    <button 
  onClick={handleUpload}
  disabled={loading}
  className="bg-green-600 text-white rounded-lg py-2 font-medium hover:bg-green-700 transition disabled:opacity-50"
>
  {loading ? "Uploading..." : "Upload Meal Plan"}
</button>

    {message && <p className="text-sm text-center text-gray-600">{message}</p>}

    </div>
    </div>
  )
}