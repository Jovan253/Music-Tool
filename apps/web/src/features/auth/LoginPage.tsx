import { useState } from 'react'
import { useAuth } from './auth-context'

export function LoginPage() {
  const { signIn, signUp } = useAuth()
  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [signupDone, setSignupDone] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      if (mode === 'login') {
        await signIn(email, password)
      } else {
        await signUp(email, password)
        setSignupDone(true)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  if (signupDone) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="panel w-full max-w-sm rounded-lg p-8 text-center">
          <p className="legend text-console-400">check your inbox</p>
          <p className="mt-3 text-console-200">
            Confirm your email address, then sign in.
          </p>
          <p className="mt-2 text-sm text-console-500">
            The message can take a minute and sometimes lands in spam.
          </p>
          <button
            className="legend mt-6 text-transport transition-opacity hover:opacity-80"
            onClick={() => { setMode('login'); setSignupDone(false) }}
          >
            back to sign in
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <header className="mb-6 text-center">
          <h1 className="font-mono text-2xl font-semibold tracking-tight text-console-100">
            TrackSplit
          </h1>
          <p className="legend mt-2 text-console-500">
            split a track into vocals · drums · bass · other
          </p>
        </header>

        <div className="panel rounded-lg p-6">
          <p className="legend mb-5 text-console-400">
            {mode === 'login' ? 'sign in' : 'create account'}
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <Field
              label="email"
              type="email"
              value={email}
              onChange={setEmail}
              autoComplete="email"
            />
            <Field
              label="password"
              type="password"
              value={password}
              onChange={setPassword}
              minLength={6}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            />

            {error && (
              <div className="rounded border border-danger/40 bg-danger/10 px-3 py-2">
                <p className="text-sm text-console-300">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded bg-transport py-2.5 text-sm font-medium text-white shadow-[0_0_16px_rgba(124,92,255,0.35)] transition-all hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-transport"
            >
              {loading ? 'working…' : mode === 'login' ? 'Sign in' : 'Create account'}
            </button>
          </form>
        </div>

        <p className="mt-5 text-center text-sm text-console-500">
          {mode === 'login' ? "No account yet?" : 'Already registered?'}{' '}
          <button
            className="text-transport transition-opacity hover:opacity-80"
            onClick={() => { setMode(mode === 'login' ? 'signup' : 'login'); setError(null) }}
          >
            {mode === 'login' ? 'Create one' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  )
}

function Field({
  label, type, value, onChange, minLength, autoComplete,
}: {
  label: string
  type: string
  value: string
  onChange: (v: string) => void
  minLength?: number
  autoComplete?: string
}) {
  return (
    <label className="block">
      <span className="legend mb-1.5 block text-console-500">{label}</span>
      <input
        type={type}
        required
        minLength={minLength}
        autoComplete={autoComplete}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded border border-console-600 bg-console-950 px-3 py-2 text-console-100 shadow-[inset_0_1px_2px_rgba(0,0,0,0.5)] transition-colors placeholder:text-console-600 focus:border-transport focus:outline-none"
      />
    </label>
  )
}
