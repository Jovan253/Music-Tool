import { useEffect, useRef, useState } from 'react'
import { getJobStatus, uploadFile, type UploadResponse } from '../../lib/api'

const ALLOWED_TYPES = ['audio/mpeg', 'audio/wav', 'audio/x-wav', 'audio/mp4', 'audio/x-m4a']
const ALLOWED_EXTENSIONS = ['.mp3', '.wav', '.m4a']
const MAX_SIZE_MB = 50
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

type State =
  | { kind: 'idle' }
  | { kind: 'uploading'; progress: number }
  | { kind: 'processing'; jobId: string }
  | { kind: 'error'; message: string }

interface Props {
  onReady: (jobId: string) => void
}

function validateFile(file: File): string | null {
  const ext = '.' + (file.name.split('.').pop() ?? '').toLowerCase()
  const typeOk = ALLOWED_TYPES.includes(file.type) || ALLOWED_EXTENSIONS.includes(ext)
  if (!typeOk) return `Unsupported file type. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`
  if (file.size > MAX_SIZE_BYTES) return `File too large. Maximum size is ${MAX_SIZE_MB} MB`
  return null
}

export function UploadZone({ onReady }: Props) {
  const [state, setState] = useState<State>({ kind: 'idle' })
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const pollingJobId = state.kind === 'processing' ? state.jobId : null

  useEffect(() => {
    if (!pollingJobId) return
    const id = setInterval(async () => {
      try {
        const job = await getJobStatus(pollingJobId)
        if (job.status === 'done') {
          onReady(pollingJobId)
        } else if (job.status === 'failed') {
          setState({ kind: 'error', message: job.error ?? 'Separation failed' })
        }
      } catch {
        // network error — keep polling
      }
    }, 3000)
    return () => clearInterval(id)
  }, [pollingJobId, onReady])

  function handleFile(file: File) {
    const err = validateFile(file)
    if (err) { setState({ kind: 'error', message: err }); return }

    setState({ kind: 'uploading', progress: 0 })
    uploadFile(file, (pct) => setState({ kind: 'uploading', progress: pct }))
      .then((result: UploadResponse) => setState({ kind: 'processing', jobId: result.job_id }))
      .catch((e: unknown) =>
        setState({ kind: 'error', message: e instanceof Error ? e.message : 'Upload failed' }),
      )
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  function onInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
    e.target.value = ''
  }

  function reset() { setState({ kind: 'idle' }) }

  const isInteractive = state.kind === 'idle' || state.kind === 'error'

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-950 p-6">
      <div className="w-full max-w-lg">
        <h1 className="mb-8 text-center text-3xl font-semibold text-white">Music Tool</h1>

        {state.kind === 'processing' ? (
          <div className="rounded-xl border border-purple-800 bg-purple-950 p-8 text-center">
            <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-purple-400 border-t-transparent" />
            <p className="text-lg font-medium text-purple-200">Separating stems…</p>
            <p className="mt-2 text-sm text-purple-400">This takes 1–3 minutes. Hang tight.</p>
          </div>
        ) : (
          <div
            role="button"
            tabIndex={0}
            onClick={() => isInteractive && inputRef.current?.click()}
            onKeyDown={(e) => e.key === 'Enter' && isInteractive && inputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); if (isInteractive) setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            className={[
              'cursor-pointer rounded-xl border-2 border-dashed p-12 text-center transition-colors',
              dragging
                ? 'border-purple-400 bg-purple-950'
                : state.kind === 'uploading'
                  ? 'cursor-default border-gray-700 bg-gray-900'
                  : 'border-gray-700 bg-gray-900 hover:border-purple-600',
            ].join(' ')}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".mp3,.wav,.m4a,audio/*"
              className="hidden"
              onChange={onInputChange}
            />

            {state.kind === 'uploading' ? (
              <div className="space-y-4">
                <p className="text-gray-400">Uploading… {state.progress}%</p>
                <div className="h-2 overflow-hidden rounded-full bg-gray-800">
                  <div
                    className="h-full rounded-full bg-purple-500 transition-all duration-150"
                    style={{ width: `${state.progress}%` }}
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-lg text-gray-300">
                  {dragging ? 'Drop to upload' : 'Drag & drop an audio file'}
                </p>
                <p className="text-sm text-gray-500">or click to browse</p>
                <p className="text-xs text-gray-600">mp3 · wav · m4a · max {MAX_SIZE_MB} MB</p>
              </div>
            )}
          </div>
        )}

        {state.kind === 'error' && (
          <div className="mt-4 flex items-center justify-between rounded-lg border border-red-800 bg-red-950 px-4 py-3">
            <p className="text-sm text-red-300">{state.message}</p>
            <button onClick={reset} className="ml-4 text-xs text-red-400 hover:text-red-200">
              Dismiss
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
