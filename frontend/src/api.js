import { MARKET } from './market'
import { readLang } from './lang'

const TOKEN_KEY = 'ali_travel_token'

export const getToken = () => {
  try { return localStorage.getItem(TOKEN_KEY) } catch { return null }
}
export const setToken = (t) => {
  try { t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY) } catch { /* storage unavailable */ }
}

// Photos straight from a phone are often huge (8-12 MB) or in the iPhone's HEIC format, which the server does not take.
// Before uploading, the browser redraws such a photo as a JPG of at most 2560 px on its longest side (a few hundred KB).
const MAX_SIDE = 2560
async function decode(file) {
  if (typeof createImageBitmap === 'function') {
    try { return await createImageBitmap(file, { imageOrientation: 'from-image' }) } catch { /* try the <img> way */ }
  }
  const url = URL.createObjectURL(file)
  try {
    const img = new Image()
    img.src = url
    await img.decode()
    return img
  } finally { URL.revokeObjectURL(url) }
}
export async function preparePhoto(file) {
  const type = (file.type || '').toLowerCase()
  if (type === 'image/gif') return file   // keep animations as they are
  const small = file.size < 1.5 * 1024 * 1024 && ['image/jpeg', 'image/png', 'image/webp'].includes(type)
  if (small) return file
  let picture
  try { picture = await decode(file) } catch {
    throw new Error('This photo could not be read. Please choose a JPG or PNG photo.')
  }
  const w = picture.width, h = picture.height
  const scale = Math.min(1, MAX_SIDE / Math.max(w, h))
  const canvas = document.createElement('canvas')
  canvas.width = Math.round(w * scale); canvas.height = Math.round(h * scale)
  const ctx = canvas.getContext('2d')
  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, canvas.width, canvas.height)   // a transparent PNG gets a white background
  ctx.drawImage(picture, 0, 0, canvas.width, canvas.height)
  const blob = await new Promise((done) => canvas.toBlob(done, 'image/jpeg', 0.86))
  if (!blob) throw new Error('This photo could not be read. Please choose a JPG or PNG photo.')
  const name = (file.name || 'photo').replace(/\.[^.]+$/, '') + '.jpg'
  return new File([blob], name, { type: 'image/jpeg' })
}

// Photo uploads in progress (the link to the server can be slow): the editor shows the percentage, keeps "Save" off until they
// finish, and the browser asks before the page is reloaded or closed, which would cancel them.
const uploads = new Map()   // id -> { loaded, total }
const uploadListeners = new Set()
const tellUploads = () => uploadListeners.forEach((fn) => fn())
export function uploadState() {
  const all = [...uploads.values()]
  const total = all.reduce((s, x) => s + x.total, 0)
  return { count: all.length, percent: total ? Math.min(99, Math.round((all.reduce((s, x) => s + x.loaded, 0) / total) * 100)) : 0 }
}
export function onUploads(fn) { uploadListeners.add(fn); return () => uploadListeners.delete(fn) }
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', (e) => { if (uploads.size) { e.preventDefault(); e.returnValue = '' } })
}
function sendWithProgress(form) {
  const id = Symbol('upload')
  uploads.set(id, { loaded: 0, total: 1 }); tellUploads()
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/upload/')
    Object.entries(authHeaders()).forEach(([k, v]) => xhr.setRequestHeader(k, v))
    xhr.upload.onprogress = (e) => { if (e.lengthComputable) { uploads.set(id, { loaded: e.loaded, total: e.total }); tellUploads() } }
    const done = () => { uploads.delete(id); tellUploads() }
    xhr.onload = () => {
      done()
      let data = null
      try { data = JSON.parse(xhr.responseText) } catch { /* not JSON */ }
      if (xhr.status >= 200 && xhr.status < 300) resolve(data)
      else reject(new Error(data?.error || data?.detail || (xhr.status === 413 ? 'The photo is too large.' : 'The photo could not be uploaded. Please try again.')))
    }
    xhr.onerror = () => { done(); reject(new Error('The connection was lost while uploading. Please try again.')) }
    xhr.onabort = () => { done(); reject(new Error('The upload was cancelled.')) }
    xhr.send(form)
  })
}

// The site editor indexes every GET response so it can tell which record a clicked piece of text belongs to.
let responseHook = null
export const setResponseHook = (fn) => { responseHook = fn }

function authHeaders() {
  const headers = {}
  headers['X-Lang'] = readLang()
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
    form.append('file', await preparePhoto(file))
    return sendWithProgress(form)
  },
}
