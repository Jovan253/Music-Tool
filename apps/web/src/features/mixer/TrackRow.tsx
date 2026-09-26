import type WaveSurfer from 'wavesurfer.js'
import { Waveform } from '../waveform/Waveform'
import { STEM_COLORS } from './stemColors'

interface Props {
  stemName: string
  audioUrl: string
  volume: number
  muted: boolean
  soloed: boolean
  dimmed: boolean
  onReady: (ws: WaveSurfer) => void
  onDestroy: () => void
  onVolumeChange: (v: number) => void
  onMuteToggle: () => void
  onSoloToggle: () => void
}

export function TrackRow({
  stemName, audioUrl, volume, muted, soloed, dimmed,
  onReady, onDestroy, onVolumeChange, onMuteToggle, onSoloToggle,
}: Props) {
  const color = STEM_COLORS[stemName] ?? '#a855f7'
  const silent = muted || dimmed

  return (
    <div
      className={[
        'panel rounded-md transition-opacity',
        'grid items-center gap-x-4 gap-y-3 px-3 py-3',
        // Mobile stacks label above waveform with controls beneath; desktop is one row.
        'grid-cols-[auto_1fr] sm:grid-cols-[7rem_1fr_auto]',
        silent ? 'opacity-55' : 'opacity-100',
      ].join(' ')}
    >
      <div className="col-span-2 flex items-center gap-2 sm:col-span-1">
        <span
          aria-hidden
          className="h-6 w-1 shrink-0 rounded-full"
          style={{
            backgroundColor: color,
            boxShadow: silent ? 'none' : `0 0 8px ${color}66`,
          }}
        />
        <span className="legend text-console-200">{stemName}</span>
      </div>

      <div className="col-span-2 min-w-0 sm:col-span-1">
        <Waveform
          url={audioUrl}
          color={color}
          dimmed={silent}
          onReady={onReady}
          onDestroy={onDestroy}
        />
      </div>

      <div className="col-span-2 flex items-center justify-between gap-3 sm:col-span-1 sm:justify-end">
        <div className="flex items-center gap-1.5">
          <ChannelButton
            label="S"
            title={`Solo ${stemName}`}
            active={soloed}
            activeClass="bg-solo text-console-1000 shadow-[0_0_10px_rgba(255,212,59,0.45)]"
            onClick={onSoloToggle}
          />
          <ChannelButton
            label="M"
            title={`Mute ${stemName}`}
            active={muted}
            activeClass="bg-mute text-console-1000 shadow-[0_0_10px_rgba(255,122,122,0.45)]"
            onClick={onMuteToggle}
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
            disabled={muted}
            aria-label={`${stemName} level`}
            className="fader w-28 sm:w-24"
          />
          {/* Fixed width and tabular digits so the number does not jitter while dragging. */}
          <span className="legend w-8 text-right tabular-nums text-console-400">
            {Math.round(volume * 100)}
          </span>
        </div>
      </div>
    </div>
  )
}

function ChannelButton({
  label, title, active, activeClass, onClick,
}: {
  label: string
  title: string
  active: boolean
  activeClass: string
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      title={title}
      aria-pressed={active}
      className={[
        'h-7 w-7 rounded border font-mono text-[11px] font-bold transition-all',
        'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-transport',
        active
          ? `border-transparent ${activeClass}`
          : 'border-console-600 bg-console-800 text-console-400 hover:border-console-500 hover:text-console-200',
      ].join(' ')}
    >
      {label}
    </button>
  )
}
