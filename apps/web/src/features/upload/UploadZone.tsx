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

function terminalMessage(status: string): string {
  if (status === 'expired') {
    return 'The audio for this track was removed to stay within storage limits. Upload it again to separate it.'
  }
  if (status === 'failed') return 'Separation failed'
  return `Separation stopped with an unexpected status: ${status}`
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
        } else if (job.status !== 'pending' && job.status !== 'processing') {
          // Anything not still in progress is terminal. Listing the terminal
          // statuses instead would poll forever on any status not in the list.
          setState({ kind: 'error', message: job.error ?? terminalMessage(job.status) })
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
    <div className="flex min-h-screen items-center justify-center p-4 sm:p-6">
      <div className="w-full max-w-xl">
        <header className="mb-8 text-center">
          <h1 className="font-mono text-2xl font-semibold tracking-tight text-console-100 sm:text-3xl">
            TrackSplit
          </h1>
          <p className="legend mt-2 text-console-500">
            split a track into vocals · drums · bass · other
          </p>
        </header>

        {state.kind === 'processing' ? (
          <div className="panel rounded-lg p-8 text-center">
            <div className="mx-auto mb-5 flex items-end justify-center gap-1" aria-hidden>
              {/* Four bars, one per channel, bouncing while the GPU works. */}
              {['#ff6f91', '#ffa94d', '#57a5ff', '#3ddc97'].map((c, i) => (
                <span
                  key={c}
                  className="w-1.5 animate-pulse rounded-full"
                  style={{
                    backgroundColor: c,
                    height: `${14 + i * 6}px`,
                    animationDelay: `${i * 140}ms`,
                    animationDuration: '900ms',
                  }}
                />
              ))}
            </div>
            <p className="legend text-console-200">separating</p>
            <p className="mt-2 text-sm text-console-400">
              Usually about 30 seconds on the GPU. The first run of the day takes
              a little longer while the container warms up.
            </p>
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
              'rounded-lg border border-dashed p-10 text-center transition-colors sm:p-14',
              'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-transport',
              dragging
                ? 'cursor-copy border-transport bg-transport/10'
                : state.kind === 'uploading'
                  ? 'cursor-default border-console-700 bg-console-900'
                  : 'cursor-pointer border-console-600 bg-console-900 hover:border-transport/70 hover:bg-console-850',
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
              <div className="space-y-3">
                <div className="flex items-baseline justify-between">
                  <span className="legend text-console-300">uploading</span>
                  <span className="legend tabular-nums text-console-300">{state.progress}%</span>
                </div>
                <div
                  role="progressbar"
                  aria-valuenow={state.progress}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  className="h-1.5 overflow-hidden rounded-full bg-console-800 shadow-[inset_0_1px_1px_rgba(0,0,0,0.6)]"
                >
                  <div
                    className="h-full rounded-full bg-transport transition-all duration-150"
                    style={{ width: `${state.progress}%` }}
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-base text-console-200">
                  {dragging ? 'Drop it' : 'Drop an audio file, or click to browse'}
                </p>
                <p className="legend text-console-500">
                  mp3 · wav · m4a · up to {MAX_SIZE_MB} mb
                </p>
              </div>
            )}
          </div>
        )}

        {state.kind === 'error' && (
          <div className="mt-4 flex items-start justify-between gap-4 rounded-md border border-danger/40 bg-danger/10 px-4 py-3">
            <div>
              <p className="legend text-danger">error</p>
              <p className="mt-1 text-sm text-console-300">{state.message}</p>
            </div>
            <button
              onClick={reset}
              className="legend shrink-0 text-console-500 transition-colors hover:text-console-200"
            >
              dismiss
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
