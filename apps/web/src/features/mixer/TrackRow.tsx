import type WaveSurfer from 'wavesurfer.js'
import { Waveform } from '../waveform/Waveform'

interface Props {
  stemName: string
  audioUrl: string
  volume: number
  muted: boolean
  soloed: boolean
  onReady: (ws: WaveSurfer) => void
  onVolumeChange: (v: number) => void
  onMuteToggle: () => void
  onSoloToggle: () => void
}

const STEM_COLORS: Record<string, string> = {
  vocals: '#ec4899',
  drums: '#f97316',
  bass: '#3b82f6',
  other: '#22c55e',
}

export function TrackRow({
  stemName, audioUrl, volume, muted, soloed,
  onReady, onVolumeChange, onMuteToggle, onSoloToggle,
}: Props) {
  const color = STEM_COLORS[stemName] ?? '#a855f7'

  return (
    <div className="flex items-center gap-3 rounded-lg bg-gray-900 p-3">
      <div className="w-16 shrink-0">
        <p className="text-sm font-medium capitalize" style={{ color }}>{stemName}</p>
      </div>

      <div className="min-w-0 flex-1">
        <Waveform url={audioUrl} onReady={onReady} />
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <button
          onClick={onMuteToggle}
          title="Mute"
          className={`w-7 rounded px-1.5 py-1 text-xs font-bold transition-colors ${
            muted ? 'bg-yellow-500 text-gray-950' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          M
        </button>
        <button
          onClick={onSoloToggle}
          title="Solo"
          className={`w-7 rounded px-1.5 py-1 text-xs font-bold transition-colors ${
            soloed ? 'bg-purple-500 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          S
        </button>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={volume}
          onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
          disabled={muted}
          className="w-20 accent-purple-500 disabled:opacity-40"
        />
      </div>
    </div>
  )
}
