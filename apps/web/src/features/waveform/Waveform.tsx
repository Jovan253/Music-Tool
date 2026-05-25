import { useEffect, useRef } from 'react'
import WaveSurfer from 'wavesurfer.js'

interface Props {
  url: string
  onReady: (ws: WaveSurfer) => void
}

export function Waveform({ url, onReady }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return
    const ws = WaveSurfer.create({
      container: containerRef.current,
      url,
      waveColor: '#374151',
      progressColor: '#7c3aed',
      height: 64,
      normalize: true,
    })
    ws.on('ready', () => onReady(ws))
    return () => { ws.destroy() }
  }, [url])

  return <div ref={containerRef} className="w-full" />
}
