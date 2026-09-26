import { useEffect, useRef, useState } from 'react'
import WaveSurfer from 'wavesurfer.js'

interface Props {
  url: string
  color: string
  dimmed?: boolean
  onReady: (ws: WaveSurfer) => void
  onDestroy: () => void
}

export function Waveform({ url, color, dimmed = false, onReady, onDestroy }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    if (!containerRef.current) return
    // `active` guards the ready handler so a StrictMode double-mount cannot report
    // a destroyed instance as ready. Deps stay narrow deliberately: including the
    // callbacks would recreate WaveSurfer on every parent render and reintroduce
    // the races fixed in 9084c15, 939c676 and 9d7898c.
    let active = true
    setReady(false)
    const ws = WaveSurfer.create({
      container: containerRef.current,
      url,
      waveColor: `${color}4d`,
      progressColor: color,
      cursorColor: '#e9e9ef',
      cursorWidth: 1,
      height: 56,
      barWidth: 2,
      barGap: 1,
      barRadius: 1,
      normalize: true,
    })
    ws.on('ready', () => {
      if (!active) return
      setReady(true)
      onReady(ws)
    })
    return () => {
      active = false
      onDestroy()
      ws.destroy()
    }
  }, [url, color])

  return (
    <div className="relative">
      <div ref={containerRef} className={dimmed ? 'opacity-45 transition-opacity' : 'transition-opacity'} />
      {!ready && (
        <div
          aria-hidden
          className="absolute inset-0 flex items-center gap-[3px] overflow-hidden rounded"
        >
          {Array.from({ length: 64 }).map((_, i) => (
            <span
              key={i}
              className="flex-1 animate-pulse rounded-sm bg-console-700"
              style={{
                // A static pseudo-waveform silhouette so the skeleton reads as audio
                // rather than a generic loading bar.
                height: `${18 + Math.abs(Math.sin(i * 0.7)) * 30}px`,
                animationDelay: `${(i % 8) * 90}ms`,
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
