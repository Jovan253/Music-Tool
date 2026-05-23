import { useEffect, useRef } from 'react'
import WaveSurfer from 'wavesurfer.js'

interface Props {
  url: string
  audioContext: AudioContext
  onReady: (ws: WaveSurfer) => void
}

export function Waveform({ url, audioContext, onReady }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return
    const ws = WaveSurfer.create({
      container: containerRef.current,
      url,
      audioContext,
      waveColor: '#374151',
      progressColor: '#7c3aed',
      height: 64,
      normalize: true,
    })
    ws.on('ready', () => onReady(ws))
    return () => { ws.destroy() }
  // audioContext is a stable ref — only re-run if url changes
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url])

  return <div ref={containerRef} className="w-full" />
}
