import { createClient } from '@supabase/supabase-js'

// The dashboard shows both a project URL and a REST URL. Pasting the REST one makes
// sign-in POST to /rest/v1/auth/v1/token, which 404s and looks like wrong credentials.
function normalizeUrl(url: string): string {
  let out = (url ?? '').trim().replace(/\/+$/, '')
  for (const suffix of ['/rest/v1', '/auth/v1', '/storage/v1']) {
    if (out.endsWith(suffix)) out = out.slice(0, -suffix.length)
  }
  return out
}

const supabaseUrl = normalizeUrl(import.meta.env.VITE_SUPABASE_URL as string)
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
