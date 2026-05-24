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
    <div className="flex flex-col items-center gap-1">
      <button
        onClick={handleExport}
        disabled={loading || disabled}
        className="w-32 rounded-full border border-purple-600 py-3 text-sm font-semibold text-purple-300 transition-colors hover:bg-purple-600 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
      >
        {loading ? 'Exporting…' : `Export ${format.toUpperCase()}`}
      </button>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  )
}
