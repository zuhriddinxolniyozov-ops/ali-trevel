import { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react'
import { api, getToken, setToken } from './api'
import { useI18n } from './i18n'
import { useEdit } from './edit/context'

/* ---------- data loading ---------- */
export function useFetch(path, { list = false } = {}) {
  const { lang } = useI18n()
  const { version } = useEdit() // bumps after the site editor saves, so pages refetch
  const [state, setState] = useState({ data: list ? [] : null, loading: true, error: null })
  const load = useCallback(() => {
    if (!path) return
    setState((s) => ({ ...s, loading: true }))
    api[list ? 'list' : 'get'](path)
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((e) => setState({ data: list ? [] : null, loading: false, error: e }))
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
export const discounted = (amount, percent) => Math.round(Number(amount || 0) * (100 - (Number(percent) || 0))) / 100
/** $289 or $231.20: cents only when there are some. */
export const exactMoney = (value) => {
  const n = Number(value || 0)
  return `$${n.toLocaleString('en-US', Number.isInteger(n) ? {} : { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export const CURRENCIES = { USD: { symbol: '$', rate: 1 }, EUR: { symbol: '€', rate: 0.93 }, GBP: { symbol: '£', rate: 0.79 } }
export const money = (usd, code = 'USD') => {
  const c = CURRENCIES[code] || CURRENCIES.USD
  return `${c.symbol}${Math.round(Number(usd || 0) * c.rate).toLocaleString('en-US')}`
}
