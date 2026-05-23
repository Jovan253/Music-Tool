const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export interface UploadResponse {
  job_id: string
  status: string
  filename: string
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
    xhr.send(form)
  })
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, init)
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
