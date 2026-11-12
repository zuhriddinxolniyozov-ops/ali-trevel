import { useState } from 'react'
import { MailCheck } from 'lucide-react'
import { api } from '../api'
import { useT } from '../i18n'
import { Spinner } from './ui'
import { goToPayment } from './Deposit'

/**
 * After a booking request is sent (when the team switched it on in Settings), the request waits for the six-digit code e-mailed
 * to the account: only the right code passes it on to the deposit or to the team.
 */
export default function BookingCode({ reference, email, onVerified, className = '' }) {
  const t = useT()
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    if (code.length !== 6) return setError('Enter the 6-digit code from the e-mail.')
    setBusy(true); setError('')
    try {
      const res = await api.post('/bookings-verify/', { reference, code })
      if (goToPayment(res)) return
      onVerified(res)
    } catch (ex) { setError(ex.message) } finally { setBusy(false) }
  }

  return (
    <form onSubmit={submit} noValidate className={`scroll-mt-24 rounded-sm border border-navy/12 bg-sand-soft/40 p-5 ${className}`}>
      <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink">{t('Confirm your booking')}</p>
      <p className="mt-3 flex gap-2.5 rounded-sm bg-white/70 p-3 text-[13.5px] leading-relaxed text-navy"><MailCheck className="mt-0.5 h-5 w-5 shrink-0 text-turquoise-deep" aria-hidden="true" />
        <span>{t('We sent a 6-digit code to {email}. Enter it below to confirm your booking request.', { email })}</span></p>
      <label className="label mt-4">{t('Code from the e-mail')}
        <input inputMode="numeric" autoComplete="one-time-code" maxLength={6} autoFocus className="input text-center font-mono text-[24px] tracking-[0.5em]"
          value={code} onChange={(e) => { setCode(e.target.value.replace(/\D/g, '').slice(0, 6)); setError('') }} placeholder="••••••" /></label>
      {error && <p role="alert" className="mt-2 text-[12px] text-destructive">{t(error)}</p>}
      <button type="submit" className="btn-primary mt-4 w-full" disabled={busy}>{busy && <Spinner />}{t('Confirm the booking')}</button>
      <p className="mt-3 text-[12px] text-ink/80">{t('The code works for 15 minutes. Check your spam folder if the e-mail does not arrive within a few minutes.')}</p>
    </form>
  )
}
