import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth, useFetch } from '../hooks'
import { useT } from '../i18n'
import { EMAIL_RE, EmptyState, Field, Spinner } from '../components/ui'

function AuthShell({ title, children, footer }) {
  const t = useT()
  return (
    <div className="shell flex justify-center py-16 lg:py-24">
      <div className="w-full max-w-md rounded-sm border border-navy/12 bg-card p-8">
        <h1 className="font-heading text-[34px]">{t(title)}</h1>{children}<div className="mt-6 text-[13px] text-ink">{footer}</div>
      </div>
    </div>
  )
}

export function Login() {
  const t = useT()
  const { login, isAuthenticated, user } = useAuth()
  const nav = useNavigate()
  const from = useLocation().state?.from
  const [f, setF] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const home = (u) => from || (u?.role === 'admin' ? '/admin' : '/account')
  if (isAuthenticated) return <Navigate to={home(user)} replace />
  async function submit(e) {
    e.preventDefault(); setBusy(true); setError('')
    try { const u = await login(f.email, f.password); nav(home(u), { replace: true }) } catch (ex) { setError(ex.message) } finally { setBusy(false) }
  }
  return (
    <AuthShell title="Sign in" footer={<>{t('New here?')} <Link to="/register" className="text-turquoise-deep">{t('Create an account')}</Link></>}>
      <form onSubmit={submit} className="mt-6 space-y-4">
        <Field label="Email"><input type="email" required className="input" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></Field>
        <Field label="Password"><input type="password" required className="input" value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} /></Field>
        {error && <p role="alert" className="text-[12px] text-destructive">{t(error)}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy && <Spinner />}{t('Sign in')}</button>
      </form>
    </AuthShell>
  )
}

export function Register() {
  const t = useT()
  const { register, isAuthenticated } = useAuth()
  const nav = useNavigate()
  const [f, setF] = useState({ full_name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  if (isAuthenticated) return <Navigate to="/account" replace />
  async function submit(e) {
    e.preventDefault()
    if (!EMAIL_RE.test(f.email)) return setError('A valid email is required.')
    setBusy(true); setError('')
    try { await register(f); nav('/account', { replace: true }) } catch (ex) { setError(ex.message) } finally { setBusy(false) }
  }
  return (
    <AuthShell title="Create account" footer={<>{t('Already registered?')} <Link to="/login" className="text-turquoise-deep">{t('Sign in')}</Link></>}>
      <form onSubmit={submit} className="mt-6 space-y-4">
        <Field label="Full name"><input className="input" value={f.full_name} onChange={(e) => setF({ ...f, full_name: e.target.value })} /></Field>
        <Field label="Email"><input type="email" className="input" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></Field>
        <Field label="Password (min. 8 characters)"><input type="password" minLength={8} className="input" value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} /></Field>
        {error && <p role="alert" className="text-[12px] text-destructive">{t(error)}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy && <Spinner />}{t('Create account')}</button>
      </form>
    </AuthShell>
  )
}

export function RequireAuth({ children, admin = false }) {
  const { isAuthenticated, ready, user } = useAuth()
  const loc = useLocation()
  if (!ready) return <div className="shell py-24"><Spinner /></div>
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: loc.pathname }} replace />
  if (admin && user.role !== 'admin') return <div className="shell py-24"><EmptyState title="Admins only" body="Your account does not have access to this area." /></div>
  return children
}

const STATUS_STYLE = {
  pending: 'bg-amber-100 text-amber-900', confirmed: 'bg-emerald-100 text-emerald-900', cancelled: 'bg-red-100 text-red-900',
  completed: 'bg-sand text-navy', published: 'bg-emerald-100 text-emerald-900', draft: 'bg-sand text-navy',
  review: 'bg-amber-100 text-amber-900', archived: 'bg-slate-200 text-slate-700', new: 'bg-amber-100 text-amber-900',
  read: 'bg-sand text-navy', replied: 'bg-emerald-100 text-emerald-900', approved: 'bg-emerald-100 text-emerald-900', rejected: 'bg-red-100 text-red-900',
}
export const cap = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s)
export function StatusPill({ status }) {
  const t = useT()
  return <span className={`rounded-full px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-[0.1em] ${STATUS_STYLE[status] || 'bg-sand text-navy'}`}>{t(status === 'review' ? 'Awaiting review' : cap(status))}</span>
}

export function Account() {
  const t = useT()
  const { user, logout, updateProfile } = useAuth()
  const bookings = useFetch('/bookings/', { list: true })
  const saved = useFetch('/saved/', { list: true })
  const [name, setName] = useState(user?.full_name || '')
  async function cancel(b) {
    if (!window.confirm(t('Cancel this request?'))) return
    await api.post(`/bookings/${b.id}/cancel/`); bookings.reload()
  }
  async function unsave(s) { await api.del(`/saved/${s.id}/`); saved.reload() }
  return (
    <div className="shell py-16 lg:py-24">
      <div className="flex flex-wrap items-end justify-between gap-4"><h1 className="display-lg">{t('My account')}</h1><button className="btn-outline" onClick={logout}>{t('Sign out')}</button></div>
      <p className="mt-2 text-ink">{user.email}</p>
      <form className="mt-6 flex max-w-md gap-3" onSubmit={(e) => { e.preventDefault(); updateProfile({ full_name: name }) }}>
        <input className="input !mt-0" value={name} onChange={(e) => setName(e.target.value)} aria-label={t('Full name')} /><button className="btn-primary">{t('Save')}</button></form>

      <h2 className="mt-14 font-heading text-[30px]">{t('Booking requests')}</h2>
      <div className="mt-4 divide-y divide-navy/10 rounded-sm border border-navy/10 bg-card">
        {bookings.data.map((b) => (
          <div key={b.id} className="flex flex-wrap items-center justify-between gap-3 p-4">
            <div><p className="font-medium">{b.service_title}</p><p className="text-[12.5px] text-ink"><span className="font-mono">{b.reference}</span> · {b.travel_date || t('date TBC')} · {b.guests} {t('Guests')}</p></div>
            <div className="flex items-center gap-3"><StatusPill status={b.status} />{['pending', 'confirmed'].includes(b.status) && <button className="text-[12px] text-destructive" onClick={() => cancel(b)}>{t('Cancel')}</button>}</div>
          </div>))}
        {!bookings.loading && !bookings.data.length && <p className="p-6 text-ink">{t('No requests yet.')} <Link to="/tours" className="text-turquoise-deep">{t('Browse tours')}</Link></p>}
      </div>

      <h2 className="mt-14 font-heading text-[30px]">{t('Saved')}</h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {saved.data.map((s) => (
          <div key={s.id} className="flex gap-3 rounded-sm border border-navy/10 bg-card p-3">
            {s.item_image && <img src={s.item_image} alt="" className="h-16 w-20 rounded object-cover" />}
            <div className="min-w-0 flex-1"><Link to={`/${s.item_type}s/${s.item_slug}`} className="block truncate font-medium hover:text-turquoise-deep">{s.item_title}</Link><p className="text-[12px] text-ink">{s.item_meta}</p>
              <button className="text-[12px] text-destructive" onClick={() => unsave(s)}>{t('Remove')}</button></div></div>))}
        {!saved.loading && !saved.data.length && <p className="text-ink">{t('Nothing saved yet.')}</p>}
      </div>
    </div>
  )
}
