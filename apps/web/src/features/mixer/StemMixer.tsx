import { useEffect, useRef, useState } from 'react'
import type WaveSurfer from 'wavesurfer.js'
import { fetchStemUrl, getJobStatus } from '../../lib/api'
import { ExportButton } from '../export/ExportButton'
import { TrackRow } from './TrackRow'

const STEMS = ['vocals', 'drums', 'bass', 'other'] as const
type StemName = typeof STEMS[number]

const SKIP_SECONDS = 5

// The mixer is used by both the signed-in app and the public demo page, which
// read from different endpoints. Injecting the source keeps one console rather
// than a second, drifting copy.
export interface MixerSource {
  fetchStemUrl: (stem: string) => Promise<string>
  fetchMeta: () => Promise<{ processing_ms: number | null }>
  canExport: boolean
}

interface Props {
  jobId: string
  source?: MixerSource
  onReset?: () => void
  title?: string
  // Embedded drops the full-page wrapper so the console can sit inside another
  // page (the demo) without doubling its padding and min-height.
  embedded?: boolean
}

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export function StemMixer({ jobId, source, onReset, title = 'Stem mixer', embedded = false }: Props) {
  const wsRefs = useRef<(WaveSurfer | null)[]>(STEMS.map(() => null))
  const sourceRef = useRef<MixerSource>(
    source ?? {
      fetchStemUrl: (stem) => fetchStemUrl(jobId, stem),
      fetchMeta: () => getJobStatus(jobId),
      canExport: true,
    },
  )

  const [stemUrls, setStemUrls] = useState<Record<StemName, string> | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [allReady, setAllReady] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [processingMs, setProcessingMs] = useState<number | null>(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volumes, setVolumes] = useState<Record<StemName, number>>(
    { vocals: 1, drums: 1, bass: 1, other: 1 },
  )
  const [muted, setMuted] = useState<Record<StemName, boolean>>(
    { vocals: false, drums: false, bass: false, other: false },
  )
  const [soloedStem, setSoloedStem] = useState<StemName | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoadError(null)
    const src = sourceRef.current
    Promise.all([
      Promise.all(STEMS.map(stem => src.fetchStemUrl(stem).then(url => [stem, url] as const))),
      src.fetchMeta(),
    ]).then(([entries, job]) => {
      if (cancelled) return
      setStemUrls(Object.fromEntries(entries) as Record<StemName, string>)
      setProcessingMs(job.processing_ms)
    }).catch((e: unknown) => {
      if (cancelled) return
      setLoadError(e instanceof Error ? e.message : 'Could not load the stems for this track')
    })
    return () => { cancelled = true }
  }, [jobId])

  useEffect(() => {
    // Read duration once every channel is loaded rather than inside the ready
    // handler: getDuration() can still report 0 at the moment `ready` fires, which
    // left the transport showing 0:00 / 0:00 for the whole session.
    if (!allReady) return
    const total = wsRefs.current[0]?.getDuration() ?? 0
    if (total > 0) setDuration(total)
  }, [allReady])

  useEffect(() => {
    if (!allReady) return
    STEMS.forEach((stem, i) => {
      let vol = volumes[stem]
      if (soloedStem !== null && soloedStem !== stem) vol = 0
      if (muted[stem]) vol = 0
      wsRefs.current[i]?.setVolume(vol)
    })
  }, [volumes, muted, soloedStem, allReady])

  function handleReady(ws: WaveSurfer, index: number) {
    wsRefs.current[index] = ws

    ws.on('interaction', (newTime: number) => {
      wsRefs.current.forEach((other, i) => {
        if (i !== index) other?.setTime(newTime)
      })
    })

    // Track 0 is the clock for the whole transport: four subscriptions would fight
    // over the same state and the displayed time would flicker between them.
    if (index === 0) {
      ws.on('finish', () => setPlaying(false))
      ws.on('timeupdate', (t: number) => setCurrentTime(t))
      setDuration(ws.getDuration())
    }

    if (wsRefs.current.every(ref => ref !== null)) setAllReady(true)
  }

  function togglePlay() {
    if (!allReady) return
    if (playing) {
      wsRefs.current.forEach(ws => ws?.pause())
      setPlaying(false)
    } else {
      wsRefs.current.forEach(ws => ws?.play())
      setPlaying(true)
    }
  }

  function seekBy(delta: number) {
    if (!allReady) return
    const lead = wsRefs.current[0]
    if (!lead) return
    const target = Math.min(Math.max(lead.getCurrentTime() + delta, 0), lead.getDuration())
    wsRefs.current.forEach(ws => ws?.setTime(target))
    setCurrentTime(target)
  }

  const anySoloed = soloedStem !== null

  return (
    <div className={embedded ? '' : 'min-h-screen px-4 py-6 sm:px-6 sm:py-10'}>
      <div className={embedded ? 'w-full' : 'mx-auto w-full max-w-4xl'}>
        <header className="mb-5 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="font-mono text-lg font-semibold tracking-tight text-console-100 sm:text-xl">
              {title}
            </h1>
            <p className="legend mt-1 text-console-500">
              {processingMs !== null
                ? `separated in ${(processingMs / 1000).toFixed(1)}s · 4 channels`
                : '4 channels'}
            </p>
          </div>
          {onReset && (
            <button
              onClick={onReset}
              className="legend rounded border border-console-600 bg-console-800 px-3 py-2 text-console-300 transition-colors hover:border-console-500 hover:text-console-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-transport"
            >
              New upload
            </button>
          )}
        </header>

        {loadError && (
          <div className="mb-4 rounded-md border border-danger/40 bg-danger/10 px-4 py-3">
            <p className="legend text-danger">could not load</p>
            <p className="mt-1 text-sm text-console-300">{loadError}</p>
          </div>
        )}

        <div className="space-y-2">
          {stemUrls
            ? STEMS.map((stem, i) => (
              <TrackRow
                key={stem}
                stemName={stem}
                audioUrl={stemUrls[stem]}
                volume={volumes[stem]}
                muted={muted[stem]}
                soloed={soloedStem === stem}
                dimmed={anySoloed && soloedStem !== stem}
                onReady={(ws) => handleReady(ws, i)}
                onDestroy={() => { wsRefs.current[i] = null }}
                onVolumeChange={(v) => setVolumes(prev => ({ ...prev, [stem]: v }))}
                onMuteToggle={() => setMuted(prev => ({ ...prev, [stem]: !prev[stem] }))}
                onSoloToggle={() => setSoloedStem(prev => prev === stem ? null : stem)}
              />
            ))
            : !loadError && STEMS.map(stem => (
              <div key={stem} className="panel h-[86px] animate-pulse rounded-md" />
            ))}
        </div>

        <div className="panel mt-4 flex flex-wrap items-center justify-between gap-4 rounded-md px-4 py-3">
          <div className="flex items-center gap-2">
            <TransportButton label="Back 5 seconds" onClick={() => seekBy(-SKIP_SECONDS)} disabled={!allReady}>
              ⏪
            </TransportButton>
            <button
              onClick={togglePlay}
              disabled={!allReady || exporting}
              aria-label={playing ? 'Pause' : 'Play'}
              className="flex h-11 w-11 items-center justify-center rounded-full bg-transport text-base text-white shadow-[0_0_16px_rgba(124,92,255,0.4)] transition-all hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-35 disabled:shadow-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-transport"
            >
              {playing ? '❙❙' : '▶'}
            </button>
            <TransportButton label="Forward 5 seconds" onClick={() => seekBy(SKIP_SECONDS)} disabled={!allReady}>
              ⏩
            </TransportButton>

            <span className="legend ml-2 tabular-nums text-console-300">
              {formatTime(currentTime)} <span className="text-console-600">/</span> {formatTime(duration)}
            </span>
          </div>

          {sourceRef.current.canExport && (
            <div className="flex items-center gap-2">
              <ExportButton jobId={jobId} volumes={volumes} muted={muted} format="mp3" disabled={!allReady || exporting} onLoadingChange={setExporting} />
              <ExportButton jobId={jobId} volumes={volumes} muted={muted} format="wav" disabled={!allReady || exporting} onLoadingChange={setExporting} />
            </div>
          )}
        </div>

        <p className="legend mt-4 text-center text-console-600">
          S solos a channel · M mutes it · click a waveform to seek
        </p>
      </div>
    </div>
  )
}

function TransportButton({
  label, onClick, disabled, children,
}: {
  label: string
  onClick: () => void
  disabled: boolean
  children: React.ReactNode
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
      title={label}
      className="flex h-9 w-9 items-center justify-center rounded border border-console-600 bg-console-800 text-xs text-console-300 transition-colors hover:border-console-500 hover:text-console-100 disabled:cursor-not-allowed disabled:opacity-35 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-transport"
    >
      {children}
    </button>
  )
}
