import { useEffect, useState } from 'react'
import { MailCheck } from 'lucide-react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth, useFetch } from '../hooks'
import { useT } from '../i18n'
import { EMAIL_RE, EmptyState, Field, Spinner } from '../components/ui'
import { TripHistory } from './Trips'

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
    <AuthShell title="Sign in" footer={<>{t('New here?')} <Link to="/register" state={{ from }} className="text-turquoise-deep">{t('Create an account')}</Link></>}>
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
  const { register, verifyEmail, resendCode, isAuthenticated } = useAuth()
  const nav = useNavigate()
  const from = useLocation().state?.from
  const [f, setF] = useState({ full_name: '', email: '', password: '' })
  const [step, setStep] = useState('form')   // form -> code
  const [code, setCode] = useState('')
  const [wait, setWait] = useState(0)        // seconds until a new code may be asked for
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')
  const [busy, setBusy] = useState(false)
  useEffect(() => {
    if (wait <= 0) return undefined
    const timer = setTimeout(() => setWait((w) => w - 1), 1000)
    return () => clearTimeout(timer)
  }, [wait])
  if (isAuthenticated) return <Navigate to={from || '/account'} replace />
  const email = f.email.trim().toLowerCase()

  async function submit(e) {
    e.preventDefault()
    if (!EMAIL_RE.test(email)) return setError('A valid email is required.')
    if (f.password.length < 8) return setError('This password is too short. It must contain at least 8 characters.')
    setBusy(true); setError(''); setInfo('')
    try {
      const res = await register({ ...f, email })
      if (res?.pending) { setStep('code'); setCode(''); setWait(res.resend_after || 60) } else nav(from || '/account', { replace: true })
    } catch (ex) { setError(ex.message) } finally { setBusy(false) }
  }
  async function confirm(e) {
    e.preventDefault()
    if (code.replace(/\D/g, '').length !== 6) return setError('Enter the 6-digit code from the e-mail.')
    setBusy(true); setError(''); setInfo('')
    try { await verifyEmail(email, code); nav(from || '/account', { replace: true }) } catch (ex) { setError(ex.message) } finally { setBusy(false) }
  }
  async function again() {
    setBusy(true); setError(''); setInfo('')
    try { await resendCode(email); setInfo('A new code was sent.'); setWait(60); setCode('') } catch (ex) { setError(ex.message) } finally { setBusy(false) }
  }

  const footer = <>{t('Already registered?')} <Link to="/login" state={{ from }} className="text-turquoise-deep">{t('Sign in')}</Link></>
  if (step === 'code') {
    return (
      <AuthShell title="Confirm your e-mail" footer={footer}>
        <p className="mt-4 flex gap-2.5 rounded-sm bg-sand-soft/70 p-3 text-[13.5px] leading-relaxed text-navy"><MailCheck className="mt-0.5 h-5 w-5 shrink-0 text-turquoise-deep" aria-hidden="true" />
          <span>{t('We sent a 6-digit code to {email}. Enter it below to confirm your e-mail address.', { email })}</span></p>
        <form onSubmit={confirm} className="mt-5 space-y-4">
          <Field label="Code from the e-mail"><input inputMode="numeric" autoComplete="one-time-code" maxLength={6} autoFocus className="input text-center font-mono text-[24px] tracking-[0.5em]"
            value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))} placeholder="••••••" /></Field>
          {error && <p role="alert" className="text-[12px] text-destructive">{t(error)}</p>}
          {info && <p role="status" className="text-[12px] text-turquoise-deep">{t(info)}</p>}
          <button className="btn-primary w-full" disabled={busy}>{busy && <Spinner />}{t('Confirm and create account')}</button>
        </form>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-[13px]">
          <button type="button" onClick={again} disabled={busy || wait > 0} className="font-medium text-turquoise-deep disabled:text-ink/60">{wait > 0 ? t('Send a new code in {n} s', { n: wait }) : t('Send a new code')}</button>
          <button type="button" onClick={() => { setStep('form'); setError(''); setInfo('') }} className="text-ink underline-offset-2 hover:underline">{t('Change e-mail')}</button>
        </div>
        <p className="mt-3 text-[12px] text-ink/80">{t('Check your spam folder if the e-mail does not arrive within a few minutes.')}</p>
      </AuthShell>
    )
  }
  return (
    <AuthShell title="Create account" footer={footer}>
      <p className="mt-3 text-[13px] leading-relaxed text-ink">{t('We send a code to your e-mail to confirm it. Bookings are made from a confirmed account.')}</p>
      <form onSubmit={submit} className="mt-5 space-y-4">
        <Field label="Full name"><input className="input" autoComplete="name" value={f.full_name} onChange={(e) => setF({ ...f, full_name: e.target.value })} /></Field>
        <Field label="Email"><input type="email" autoComplete="email" className="input" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></Field>
        <Field label="Password (min. 8 characters)"><input type="password" autoComplete="new-password" minLength={8} className="input" value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} /></Field>
        {error && <p role="alert" className="text-[12px] text-destructive">{t(error)}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy && <Spinner />}{t('Send the code')}</button>
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
  const saved = useFetch('/saved/', { list: true })
  const [name, setName] = useState(user?.full_name || '')
  async function unsave(s) { await api.del(`/saved/${s.id}/`); saved.reload() }
  return (
    <div className="shell py-16 lg:py-24">
      <div className="flex flex-wrap items-end justify-between gap-4"><h1 className="display-lg">{t('My account')}</h1><button className="btn-outline" onClick={logout}>{t('Sign out')}</button></div>
      <p className="mt-2 text-ink">{user.email}</p>
      <form className="mt-6 flex max-w-md gap-3" onSubmit={(e) => { e.preventDefault(); updateProfile({ full_name: name }) }}>
        <input className="input !mt-0" value={name} onChange={(e) => setName(e.target.value)} aria-label={t('Full name')} /><button className="btn-primary">{t('Save')}</button></form>

      <div className="mt-14"><TripHistory /></div>

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
