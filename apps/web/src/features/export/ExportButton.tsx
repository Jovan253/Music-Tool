import { useState } from 'react'
import { exportMix } from '../../lib/api'

interface Props {
  jobId: string
  volumes: Record<string, number>
  muted: Record<string, boolean>
  format?: 'mp3' | 'wav'
  disabled?: boolean
  onLoadingChange?: (loading: boolean) => void
}

export function ExportButton({ jobId, volumes, muted, format = 'mp3', disabled = false, onLoadingChange }: Props) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleExport() {
    setLoading(true)
    onLoadingChange?.(true)
    setError(null)
    try {
      // Muted stems get volume 0
      const effectiveVolumes = Object.fromEntries(
        Object.entries(volumes).map(([stem, vol]) => [stem, muted[stem] ? 0 : vol]),
      )
      const blob = await exportMix(jobId, effectiveVolumes, format)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `mix.${format}`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Export failed')
    } finally {
      setLoading(false)
      onLoadingChange?.(false)
    }
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <button
        onClick={handleExport}
        disabled={loading || disabled}
        className="legend rounded border border-console-600 bg-console-800 px-3 py-2 text-console-300 transition-colors hover:border-transport hover:text-console-100 disabled:cursor-not-allowed disabled:opacity-35 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-transport"
      >
        {loading ? 'rendering…' : `↓ ${format}`}
      </button>
      {error && <p className="max-w-40 text-right text-[11px] text-danger">{error}</p>}
    </div>
  )
}
