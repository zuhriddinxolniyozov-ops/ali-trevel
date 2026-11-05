import { MARKET } from './market'

const TOKEN_KEY = 'ali_travel_token'

export const getToken = () => {
  try { return localStorage.getItem(TOKEN_KEY) } catch { return null }
}
export const setToken = (t) => {
  try { t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY) } catch { /* storage unavailable */ }
}

// The site editor indexes every GET response so it can tell which record a clicked piece of text belongs to.
let responseHook = null
export const setResponseHook = (fn) => { responseHook = fn }

function authHeaders() {
  const headers = {}
  try { headers['X-Lang'] = localStorage.getItem('ali-travel-locale') || 'en' } catch { /* storage unavailable */ }
  headers['X-Market'] = MARKET
  const token = getToken()
  if (token) headers.Authorization = `Token ${token}`
  return headers
}

async function parse(res) {
  const data = res.status === 204 ? null : await res.json().catch(() => null)
  if (!res.ok) {
    // DRF field errors look like { field: ["message"] }; say which field the message is about.
    const entry = data && typeof data === 'object' && !data.error && !data.detail ? Object.entries(data)[0] : null
    const first = entry ? `${entry[0].replace(/_/g, ' ')}: ${[entry[1]].flat()[0]}` : null
    const err = new Error(data?.error || data?.detail || first || 'Request failed')
    err.status = res.status
    throw err
  }
  return data
}

async function request(path, { method = 'GET', body } = {}, retry = true) {
  const headers = { 'Content-Type': 'application/json', ...authHeaders() }
  const res = await fetch(`/api${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined })
  // A stale token makes even public endpoints answer 401: drop it and retry anonymously.
  if (res.status === 401 && headers.Authorization && retry && !path.startsWith('/auth/')) {
    setToken(null)
    return request(path, { method, body }, false)
  }
  const data = await parse(res)
  if (method === 'GET' && responseHook) { try { responseHook(path, data) } catch { /* indexing is best effort */ } }
  return data
}

const list = (data) => (Array.isArray(data) ? data : data?.results ?? [])

export const api = {
  get: (p) => request(p),
  post: (p, body) => request(p, { method: 'POST', body }),
  patch: (p, body) => request(p, { method: 'PATCH', body }),
  put: (p, body) => request(p, { method: 'PUT', body }),
  del: (p) => request(p, { method: 'DELETE' }),
  list: (p) => request(p).then(list),
  /** Download a file (e.g. a CSV export) with the signed-in admin's token. */
  download: async (path, filename) => {
    const res = await fetch(`/api${path}`, { headers: authHeaders() })
    if (!res.ok) throw new Error('Download failed')
    const link = document.createElement('a')
    link.href = URL.createObjectURL(await res.blob())
    link.download = filename
    link.click()
    URL.revokeObjectURL(link.href)
  },
  /** Upload a photo (admin only). Resolves to { url }. */
  upload: async (file) => {
    const form = new FormData()
    form.append('file', file)
    return parse(await fetch('/api/upload/', { method: 'POST', headers: authHeaders(), body: form }))
  },
}
