import { useState } from 'react'
import { StemMixer } from './features/mixer/StemMixer'
import { UploadZone } from './features/upload/UploadZone'

function App() {
  const [jobId, setJobId] = useState<string | null>(null)

  if (jobId) {
    return <StemMixer jobId={jobId} onReset={() => setJobId(null)} />
  }

  return <UploadZone onReady={setJobId} />
}

export default App
