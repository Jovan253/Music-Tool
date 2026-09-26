import { useState } from 'react'
import { AuthProvider } from './features/auth/AuthContext'
import { useAuth } from './features/auth/auth-context'
import { DemoPage } from './features/demo/DemoPage'
import { LoginPage } from './features/auth/LoginPage'
import { StemMixer } from './features/mixer/StemMixer'
import { UploadZone } from './features/upload/UploadZone'

function AppContent() {
  const { session, loading, signOut } = useAuth()
  const [jobId, setJobId] = useState<string | null>(null)

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="legend text-console-500">loading</p>
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
        className="legend absolute right-4 top-4 z-10 text-console-600 transition-colors hover:text-console-300"
      >
        sign out
      </button>
      {jobId
        ? <StemMixer jobId={jobId} onReset={() => setJobId(null)} />
        : <UploadZone onReady={setJobId} />
      }
    </div>
  )
}

function App() {
  // Two routes do not justify a router dependency. `vercel.json` rewrites every
  // path to index.html, so /demo is served by the SPA and read here.
  if (window.location.pathname.replace(/\/+$/, '') === '/demo') {
    return <DemoPage />
  }

  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
