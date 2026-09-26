import { useEffect, useMemo, useState } from 'react'
import { fetchDemoJob, fetchDemoStemUrl, type DemoJob } from '../../lib/api'
import { StemMixer, type MixerSource } from '../mixer/StemMixer'

export function DemoPage() {
  const [job, setJob] = useState<DemoJob | null>(null)
  const [error, setError] = useState<string | null>(null)

  const source = useMemo<MixerSource>(() => ({
    fetchStemUrl: fetchDemoStemUrl,
    fetchMeta: async () => ({ processing_ms: null }),
    // Export posts to an authenticated route; offering it here would 401.
    canExport: false,
  }), [])

  useEffect(() => {
    let cancelled = false
    fetchDemoJob()
      .then(d => { if (!cancelled) setJob(d) })
      .catch(() => { if (!cancelled) setError('The demo track is not available right now.') })
    return () => { cancelled = true }
  }, [])

  return (
    <div className="min-h-screen px-4 py-10 sm:px-6">
      <div className="mx-auto w-full max-w-4xl">
        <header className="mb-8 text-center">
          <h1 className="font-mono text-2xl font-semibold tracking-tight text-console-100 sm:text-3xl">
            TrackSplit
          </h1>
          <p className="mt-3 text-console-300">
            Upload a song and get its vocals, drums, bass and everything else as four
            separate tracks you can mix, mute and play along to.
          </p>
          <p className="legend mt-2 text-console-500">
            demo · no sign-in needed
          </p>
        </header>

        <section aria-labelledby="try-it">
          <h2 id="try-it" className="legend mb-3 text-console-400">
            try it — this is a real separation
          </h2>

          {error && (
            <div className="panel rounded-lg px-4 py-8 text-center">
              <p className="text-console-300">{error}</p>
            </div>
          )}

          {!job && !error && (
            <div className="space-y-2" aria-busy>
              {[0, 1, 2, 3].map(i => (
                <div key={i} className="panel h-[86px] animate-pulse rounded-md" />
              ))}
            </div>
          )}

          {job && (
            <StemMixer
              jobId="demo"
              source={source}
              title={job.title}
              embedded
            />
          )}
        </section>

        <div className="mt-10 text-center">
          <a
            href="/"
            className="inline-block rounded bg-transport px-5 py-2.5 text-sm font-medium text-white shadow-[0_0_16px_rgba(124,92,255,0.35)] transition-all hover:brightness-110"
          >
            Separate your own track
          </a>
          <p className="legend mt-3 text-console-600">
            free · takes about 30 seconds
          </p>
        </div>
      </div>
    </div>
  )
}
