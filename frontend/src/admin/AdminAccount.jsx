import { useState } from 'react'
import { Eye, EyeOff, KeyRound } from 'lucide-react'
import { api, setToken } from '../api'
import { useAuth } from '../hooks'
import { useT } from '../i18n'
import { Spinner } from '../components/ui'

const FIELD_NAMES = { 'new email': 'New login (e-mail)', 'new password': 'New password', 'current password': 'Current password' }

/**
 * The signed-in admin changes the login (the e-mail used to sign in) and/or the password. The current password is always
 * asked for. After a new password every other device is signed out; this one gets a fresh token and stays signed in.
 */
export default function AdminAccount() {
  const t = useT()
  const { user, updateProfile } = useAuth()
  const [form, setForm] = useState({ current_password: '', new_email: '', new_password: '', repeat: '' })
  const [show, setShow] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState(null)   // { ok, text }
  const set = (key) => (e) => { setMessage(null); setForm({ ...form, [key]: e.target.value }) }

  // Server messages are in English: "field: text" becomes "<translated field>: <translated text>".
  const explain = (text) => {
    const [, field, rest] = /^([a-z ]+): (.+)$/.exec(text) || []
    return field && FIELD_NAMES[field] ? `${t(FIELD_NAMES[field])}: ${t(rest)}` : t(text)
  }

  async function save(e) {
    e.preventDefault()
    const email = form.new_email.trim().toLowerCase()
    if (!form.current_password) return setMessage({ ok: false, text: t('Write your current password.') })
    if (!email && !form.new_password) return setMessage({ ok: false, text: t('Write a new login or a new password.') })
    if (form.new_password && form.new_password !== form.repeat) return setMessage({ ok: false, text: t('The two new passwords are not the same.') })
    setSaving(true)
    try {
      const res = await api.post('/auth/credentials/', { current_password: form.current_password, new_email: email, new_password: form.new_password })
      setToken(res.token)
      await updateProfile({})   // reload the signed-in user (new login) with the new token
      setForm({ current_password: '', new_email: '', new_password: '', repeat: '' })
      setMessage({ ok: true, text: form.new_password ? t('Saved. Other devices were signed out: sign in there with the new password.') : t('Saved. Sign in with the new login from now on.') })
    } catch (ex) {
      setMessage({ ok: false, text: explain(ex.message) })
    }
    setSaving(false)
  }

  const input = 'input'
  const pass = show ? 'text' : 'password'
  return (
    <form onSubmit={save} className="max-w-xl space-y-6 rounded-sm border border-navy/10 bg-white p-5 sm:p-7">
      <div className="flex items-start gap-3">
        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-navy text-ivory"><KeyRound className="h-5 w-5" /></span>
        <div>
          <h2 className="font-heading text-[26px] leading-tight">{t('Login and password')}</h2>
          <p className="mt-1 text-[14px] text-ink">{t('You sign in to the admin panel with this e-mail and password.')}</p>
          <p className="mt-2 text-[14px] text-navy">{t('Current login')}: <span className="font-mono">{user?.email}</span></p>
        </div>
      </div>

      <label className="label">{t('New login (e-mail)')} <span className="font-normal text-ink">({t('leave empty to keep it')})</span>
        <input type="email" autoComplete="username" className={input} value={form.new_email} onChange={set('new_email')} placeholder={user?.email} /></label>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="label">{t('New password')} <span className="font-normal text-ink">({t('at least 8 characters')})</span>
          <input type={pass} autoComplete="new-password" className={input} value={form.new_password} onChange={set('new_password')} /></label>
        <label className="label">{t('Repeat the new password')}
          <input type={pass} autoComplete="new-password" className={input} value={form.repeat} onChange={set('repeat')} /></label>
      </div>

      <div className="border-t border-navy/10 pt-5">
        <label className="label">{t('Current password')} <span className="font-normal text-ink">({t('needed to save any change')})</span>
          <input type={pass} autoComplete="current-password" className={input} value={form.current_password} onChange={set('current_password')} /></label>
        <button type="button" onClick={() => setShow((v) => !v)} className="mt-2 inline-flex items-center gap-1.5 text-[13px] text-turquoise-deep hover:text-navy">
          {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}{t(show ? 'Hide passwords' : 'Show passwords')}</button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <button type="submit" className="btn-primary" disabled={saving}>{saving && <Spinner />}{t('Save')}</button>
        {message && <p role="status" className={`text-[14px] ${message.ok ? 'text-turquoise-deep' : 'text-destructive'}`}>{message.text}</p>}
      </div>
    </form>
  )
}
