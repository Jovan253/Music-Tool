import { useEffect, useRef } from 'react'
import WaveSurfer from 'wavesurfer.js'

interface Props {
  url: string
  onReady: (ws: WaveSurfer) => void
  onDestroy: () => void
}

export function Waveform({ url, onReady, onDestroy }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return
    let active = true
    const ws = WaveSurfer.create({
      container: containerRef.current,
      url,
      waveColor: '#374151',
      progressColor: '#7c3aed',
      height: 64,
      normalize: true,
    })
    ws.on('ready', () => { if (active) onReady(ws) })
    return () => { active = false; onDestroy(); ws.destroy() }
  }, [url])

  return <div ref={containerRef} className="w-full" />
}
