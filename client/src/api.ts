import type { Marker, MarkerIn } from './types'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const EXPORT_URL = BASE_URL + '/markers/export'

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(BASE_URL + path, {
      ...init,
      headers: init.body ? { 'Content-Type': 'application/json' } : undefined,
    })
  } catch {
    throw new Error('Network error: server is unreachable')
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    if (typeof body?.detail === 'string') throw new Error(body.detail)
    if (response.status === 422) throw new Error('Invalid marker data')
    throw new Error(`HTTP ${response.status}`)
  }

  return response.status === 204 ? (undefined as T) : response.json()
}

export const api = {
  list: () => request<{ markers: Marker[] }>('/markers').then((r) => r.markers),

  create: (data: MarkerIn) =>
    request<Marker>('/markers', { method: 'POST', body: JSON.stringify(data) }),

  replace: (id: string, data: MarkerIn) =>
    request<Marker>(`/markers/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  remove: (id: string) => request<void>(`/markers/${id}`, { method: 'DELETE' }),

  importMany: (markers: MarkerIn[]) =>
    request<{ markers: Marker[] }>('/markers/import', {
      method: 'POST',
      body: JSON.stringify({ markers }),
    }).then((r) => r.markers),

  clear: () => request<void>('/markers', { method: 'DELETE' }),
}
