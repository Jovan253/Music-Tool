const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

let _authToken: string | null = null

export function setAuthToken(token: string | null): void {
  _authToken = token
}

export interface UploadResponse {
  job_id: string
  status: string
  filename: string
}

export interface JobResponse {
  job_id: string
  status: 'pending' | 'processing' | 'done' | 'failed'
  filename: string
  created_at: string
  stems: Record<string, string> | null
  error: string | null
}

export function uploadFile(
  file: File,
  onProgress: (pct: number) => void,
): Promise<UploadResponse> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    const form = new FormData()
    form.append('file', file)

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 100))
    }

    xhr.onload = () => {
      if (xhr.status === 201) {
        resolve(JSON.parse(xhr.responseText) as UploadResponse)
      } else {
        const detail = (() => {
          try { return (JSON.parse(xhr.responseText) as { detail: string }).detail } catch { return xhr.statusText }
        })()
        reject(new Error(detail))
      }
    }

    xhr.onerror = () => reject(new Error('Network error — please try again'))
    xhr.open('POST', `${BASE_URL}/upload`)
    if (_authToken) xhr.setRequestHeader('Authorization', `Bearer ${_authToken}`)
    xhr.send(form)
  })
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    ...(init?.headers as Record<string, string>),
  }
  if (_authToken) headers['Authorization'] = `Bearer ${_authToken}`

  const res = await fetch(`${BASE_URL}${path}`, { ...init, headers })
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
}

export function getJobStatus(jobId: string): Promise<JobResponse> {
  return request<JobResponse>(`/jobs/${jobId}`)
}

export function getStemUrl(jobId: string, stemName: string): string {
  return `${BASE_URL}/jobs/${jobId}/stems/${stemName}`
}

export async function exportMix(
  jobId: string,
  stems: Record<string, number>,
  format: 'mp3' | 'wav',
): Promise<Blob> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (_authToken) headers['Authorization'] = `Bearer ${_authToken}`

  const res = await fetch(`${BASE_URL}/jobs/${jobId}/export`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ stems, format }),
  })
  if (!res.ok) throw new Error(`Export failed: ${res.status}`)
  return res.blob()
}
