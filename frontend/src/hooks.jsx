import { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react'
import { api, getToken, onUploads, setToken, uploadState } from './api'
import { useI18n } from './i18n'
import { useEdit } from './edit/context'
import { MARKET, isLocal, roundPrice, som } from './market'

/* ---------- data loading ---------- */
// What a page loaded is kept, so coming back to it (Back, or a reload) shows it at once while a fresh copy is fetched behind it.
// Public answers are also kept in sessionStorage (this tab only, so a reload is instant); signed-in answers stay in memory.
const memory = new Map()
const STORE = 'ali-api:'
const cacheKey = (path, list, lang) => `${MARKET}|${lang}|${list ? 'l' : 'g'}|${getToken() ? `u${getToken().slice(-6)}` : 'anon'}|${path}`

function readCache(key) {
  if (memory.has(key)) return memory.get(key)
  if (!key.includes('|anon|')) return undefined
  try {
    const raw = sessionStorage.getItem(STORE + key)
    if (raw) { const data = JSON.parse(raw); memory.set(key, data); return data }
  } catch { /* storage unavailable */ }
  return undefined
}

function writeCache(key, data) {
  memory.set(key, data)
  if (!key.includes('|anon|')) return
  try { sessionStorage.setItem(STORE + key, JSON.stringify(data)) } catch {
    try { Object.keys(sessionStorage).filter((k) => k.startsWith(STORE)).forEach((k) => sessionStorage.removeItem(k)) } catch { /* full or blocked: memory is enough */ }
  }
}

export function useFetch(path, { list = false } = {}) {
  const { lang } = useI18n()
  const { version } = useEdit() // bumps after the site editor saves, so pages refetch
  const [state, setState] = useState(() => {
    const hit = path ? readCache(cacheKey(path, list, lang)) : undefined
    return hit !== undefined ? { data: hit, loading: false, error: null } : { data: list ? [] : null, loading: true, error: null }
  })
  const latest = useRef(null)
  const load = useCallback(() => {
    if (!path) return
    const key = cacheKey(path, list, lang)
    latest.current = key
    const hit = readCache(key)
    if (hit !== undefined) setState((s) => (s.data === hit && !s.loading ? s : { data: hit, loading: false, error: null }))
    else setState((s) => ({ ...s, loading: true }))
    api[list ? 'list' : 'get'](path)
      .then((data) => {
        if (latest.current !== key) return   // the page moved on to another address meanwhile
        const same = hit !== undefined && JSON.stringify(hit) === JSON.stringify(data)
        writeCache(key, data)
        if (!same) setState({ data, loading: false, error: null })
      })
      .catch((e) => { if (latest.current === key && hit === undefined) setState({ data: list ? [] : null, loading: false, error: e }) })
  }, [path, list, lang, version])
  useEffect(() => { load() }, [load])
  return { ...state, reload: load }
}

const DEFAULT_SETTINGS = {
  email: 'alitravel004@gmail.com',
  phone_primary: '+998942222498',
  phone_secondary: '+998938653300',
  instagram_url: 'https://www.instagram.com/al1_travel1',
  telegram_url: 'https://t.me/al1_travel1',
  facebook_url: 'https://www.facebook.com/share/1CQmva9Sds/',
  youtube_url: 'https://www.youtube.com/@Alitravel_uz',
  x_url: 'https://x.com/alitraveluz',
}

export function useSettings() {
  const { data } = useFetch('/site-content/')
  const merged = { ...DEFAULT_SETTINGS }
  if (data) Object.keys(data).forEach((k) => data[k] && (merged[k] = data[k]))
  return { settings: merged, content: data }
}

/* ---------- auth ---------- */
const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    if (!getToken()) { setReady(true); return }
    api.get('/auth/me/')
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setReady(true))
  }, [])

  const finish = ({ token, user: u }) => { setToken(token); setUser(u); return u }
  const value = {
    user, ready, isAuthenticated: !!user,
    login: (email, password) => api.post('/auth/login/', { email, password }).then(finish),
    register: (payload) => api.post('/auth/register/', payload).then(finish),
    logout: async () => { try { await api.post('/auth/logout/') } catch { /* already signed out */ } setToken(null); setUser(null) },
    updateProfile: (payload) => api.patch('/auth/me/', payload).then(setUser),
  }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/* ---------- photo uploads in progress ---------- */
/** { count, percent } of the photos being uploaded right now (re-renders as they progress). */
export function useUploads() {
  const [state, setState] = useState(uploadState)
  useEffect(() => onUploads(() => setState(uploadState())), [])
  return state
}

/* ---------- the Back button closes a window first ---------- */
/**
 * While `open` is true (an editing form, the phone menu, a dialog), the browser's Back button closes it instead of leaving
 * the page: opening adds a history entry, Back removes it and calls onClose. Closing it with its own buttons removes the entry.
 */
export function useBackClose(open, onClose) {
  const closeRef = useRef(onClose)
  closeRef.current = onClose
  const alive = useRef(false)
  useEffect(() => {
    if (!open) return undefined
    alive.current = true
    let backed = false
    if (!window.history.state?.aliOverlay) window.history.pushState({ ...(window.history.state || {}), aliOverlay: true }, '')
    const onPop = () => { backed = true; closeRef.current() }
    window.addEventListener('popstate', onPop)
    return () => {
      alive.current = false
      window.removeEventListener('popstate', onPop)
      // closed by its own button: take our entry away again (unless the window simply re-opened, or the page changed)
      if (!backed) setTimeout(() => { if (!alive.current && window.history.state?.aliOverlay) window.history.back() }, 0)
    }
  }, [open])
}

/* ---------- scroll reveal ---------- */
export function Reveal({ children, delay = 0, className = '', as: Tag = 'div' }) {
  const ref = useRef(null)
  const [shown, setShown] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el || typeof IntersectionObserver === 'undefined') { setShown(true); return }
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setShown(true); io.disconnect() } }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' })
    io.observe(el)
    return () => io.disconnect()
  }, [])
  return (
    <Tag ref={ref} className={className} style={{
      opacity: shown ? 1 : 0,
      transform: shown ? 'translateY(0)' : 'translateY(20px)',
      transition: 'opacity .8s cubic-bezier(.16,1,.3,1), transform .8s cubic-bezier(.16,1,.3,1)',
      transitionDelay: `${delay}ms`,
    }}>{children}</Tag>
  )
}

/* ---------- currency ---------- */
/** A price with `percent` taken off, rounded to cents. */
export const discounted = (amount, percent) => roundPrice(Number(amount || 0) * (100 - (Number(percent) || 0)) / 100)
/** $289 or $231.20 (cents only when there are some); 1 746 000 so'm on the local site. */
export const exactMoney = (value) => {
  const n = Number(value || 0)
  if (isLocal) return som(n)
  return `$${n.toLocaleString('en-US', Number.isInteger(n) ? {} : { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export const CURRENCIES = { USD: { symbol: '$', rate: 1 }, EUR: { symbol: '€', rate: 0.93 }, GBP: { symbol: '£', rate: 0.79 } }
export const money = (usd, code = 'USD') => {
  if (isLocal) return som(usd)
  const c = CURRENCIES[code] || CURRENCIES.USD
  return `${c.symbol}${Math.round(Number(usd || 0) * c.rate).toLocaleString('en-US')}`
}
