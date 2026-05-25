import { useState } from 'react'
import { AuthProvider, useAuth } from './features/auth/AuthContext'
import { LoginPage } from './features/auth/LoginPage'
import { StemMixer } from './features/mixer/StemMixer'
import { UploadZone } from './features/upload/UploadZone'

function AppContent() {
  const { session, loading, signOut } = useAuth()
  const [jobId, setJobId] = useState<string | null>(null)

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="text-gray-400">Loading…</div>
      </div>
    )
  }

  if (!session) {
    return <LoginPage />
  }

  return (
    <div className="relative">
      <button
        onClick={signOut}
        className="absolute top-4 right-4 z-10 text-xs text-gray-500 hover:text-gray-300 transition-colors"
      >
        Sign out
      </button>
      {jobId
        ? <StemMixer jobId={jobId} onReset={() => setJobId(null)} />
        : <UploadZone onReady={setJobId} />
      }
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
