import { useEffect, useRef, useState } from 'react'
import type WaveSurfer from 'wavesurfer.js'
import { getStemUrl } from '../../lib/api'
import { ExportButton } from '../export/ExportButton'
import { TrackRow } from './TrackRow'

const STEMS = ['vocals', 'drums', 'bass', 'other'] as const
type StemName = typeof STEMS[number]

interface Props {
  jobId: string
  onReset: () => void
}

export function StemMixer({ jobId, onReset }: Props) {
  const audioCtxRef = useRef<AudioContext>(new AudioContext())
  const wsRefs = useRef<(WaveSurfer | null)[]>(STEMS.map(() => null))
  const readyCount = useRef(0)

  const [allReady, setAllReady] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [volumes, setVolumes] = useState<Record<StemName, number>>(
    { vocals: 1, drums: 1, bass: 1, other: 1 },
  )
  const [muted, setMuted] = useState<Record<StemName, boolean>>(
    { vocals: false, drums: false, bass: false, other: false },
  )
  const [soloedStem, setSoloedStem] = useState<StemName | null>(null)

  useEffect(() => {
    const ctx = audioCtxRef.current
    return () => { ctx.close() }
  }, [])

  // Apply effective volumes whenever mix state changes
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

    // Sync seek: when this waveform is clicked/dragged, update all others
    ws.on('interaction', () => {
      const time = ws.getCurrentTime()
      wsRefs.current.forEach((other, i) => {
        if (i !== index) other?.setTime(time)
      })
    })

    if (index === 0) {
      ws.on('finish', () => setPlaying(false))
    }

    readyCount.current++
    if (readyCount.current === STEMS.length) setAllReady(true)
  }

  async function togglePlay() {
    if (!allReady) return
    if (audioCtxRef.current.state === 'suspended') {
      await audioCtxRef.current.resume()
    }
    if (playing) {
      wsRefs.current.forEach(ws => ws?.pause())
      setPlaying(false)
    } else {
      wsRefs.current.forEach(ws => ws?.play())
      setPlaying(true)
    }
  }

  function setVolume(stem: StemName, v: number) {
    setVolumes(prev => ({ ...prev, [stem]: v }))
  }

  function toggleMute(stem: StemName) {
    setMuted(prev => ({ ...prev, [stem]: !prev[stem] }))
  }

  function toggleSolo(stem: StemName) {
    setSoloedStem(prev => prev === stem ? null : stem)
  }

  return (
    <div className="flex min-h-screen flex-col bg-gray-950 p-6">
      <div className="mx-auto w-full max-w-3xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-white">Stem Mixer</h1>
          <button
            onClick={onReset}
            className="rounded-lg bg-gray-800 px-3 py-1.5 text-sm text-gray-300 hover:bg-gray-700"
          >
            New upload
          </button>
        </div>

        {!allReady && (
          <p className="mb-4 text-sm text-gray-500 animate-pulse">Loading waveforms…</p>
        )}

        <div className="space-y-2">
          {STEMS.map((stem, i) => (
            <TrackRow
              key={stem}
              stemName={stem}
              audioUrl={getStemUrl(jobId, stem)}
              audioContext={audioCtxRef.current}
              volume={volumes[stem]}
              muted={muted[stem]}
              soloed={soloedStem === stem}
              onReady={(ws) => handleReady(ws, i)}
              onVolumeChange={(v) => setVolume(stem, v)}
              onMuteToggle={() => toggleMute(stem)}
              onSoloToggle={() => toggleSolo(stem)}
            />
          ))}
        </div>

        <div className="mt-8 flex justify-center gap-4">
          <button
            onClick={togglePlay}
            disabled={!allReady || exporting}
            className="w-32 rounded-full bg-purple-600 py-3 text-sm font-semibold text-white transition-colors hover:bg-purple-500 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {playing ? 'Pause' : 'Play'}
          </button>
          {allReady && (
            <>
              <ExportButton jobId={jobId} volumes={volumes} muted={muted} format="mp3" disabled={exporting} onLoadingChange={setExporting} />
              <ExportButton jobId={jobId} volumes={volumes} muted={muted} format="wav" disabled={exporting} onLoadingChange={setExporting} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
