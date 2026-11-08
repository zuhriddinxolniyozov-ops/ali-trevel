import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { CreditCard, ShieldCheck, TriangleAlert } from 'lucide-react'
import { api } from '../api'
import { exactMoney, useSettings } from '../hooks'
import { useT } from '../i18n'
import { Spinner } from './ui'

/** The booking deposit as the site settings describe it (null when it is switched off). */
export function useDeposit() {
  const { content } = useSettings()
  if (!content?.deposit_enabled || !(Number(content.deposit_amount) > 0)) return null
  return { amount: exactMoney(Number(content.deposit_amount)), refunds: content.deposit_refund_on_cancel !== false, provider: content.deposit_provider }
}

/** A short note above the send button: a small deposit follows the request and comes back if the trip is cancelled. */
export function DepositNote({ deposit }) {
  const t = useT()
  if (!deposit) return null
  return (
    <p className="mt-4 flex gap-2 rounded-sm border border-navy/12 bg-white px-3 py-2.5 text-[12.5px] leading-snug text-navy">
      <ShieldCheck className="mt-px h-4 w-4 shrink-0 text-turquoise-deep" aria-hidden="true" />
      <span>{t(deposit.refunds
        ? 'To keep fake requests away, you pay a {amount} deposit after sending the request. If you cancel the trip, it is refunded.'
        : 'To keep fake requests away, you pay a {amount} deposit after sending the request. If you cancel the trip, our team decides about the refund.', { amount: deposit.amount })}</span>
    </p>
  )
}

/** After the request is saved: open the payment page the server gave (Octo, or the site's own page in test mode). */
export function goToPayment(res) {
  if (!res?.payment_url) return false
  window.location.assign(res.payment_url)
  return true
}

/** Test mode only (no payment keys yet): pretend to pay the deposit. No money moves. */
export function TestPayment() {
  const t = useT()
  const { reference } = useParams()
  const nav = useNavigate()
  const deposit = useDeposit()
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  async function finish(result) {
    setBusy(result); setError('')
    try { await api.post('/deposits/test/', { reference, result }); nav(`/trips?payment=${reference}`, { replace: true }) } catch (ex) { setError(ex.message); setBusy('') }
  }
  return (
    <div className="shell flex justify-center py-16 lg:py-24">
      <div className="w-full max-w-md rounded-sm border border-navy/12 bg-card p-8">
        <p className="flex items-center gap-2 rounded-sm bg-amber-100 px-3 py-2 text-[13px] font-medium text-amber-900"><TriangleAlert className="h-4 w-4 shrink-0" />{t('Test mode: no money is taken. The real payment page opens once the payment service is connected.')}</p>
        <h1 className="mt-6 flex items-center gap-2 font-heading text-[32px]"><CreditCard className="h-7 w-7 text-turquoise-deep" />{t('Booking deposit')}</h1>
        <p className="mt-2 text-[14px] text-ink">{t('Request')} <span className="font-mono">{reference}</span></p>
        {deposit && <p className="mt-4 text-[28px] font-bold text-navy">{deposit.amount}</p>}
        {error && <p role="alert" className="mt-3 text-[12.5px] text-destructive">{t(error)}</p>}
        <button type="button" className="btn-primary mt-6 w-full" disabled={!!busy} onClick={() => finish('paid')}>{busy === 'paid' && <Spinner />}{t('Pay (test)')}</button>
        <button type="button" className="btn-outline mt-2 w-full" disabled={!!busy} onClick={() => finish('cancel')}>{t('Cancel the payment')}</button>
        <Link to="/trips" className="mt-4 block text-center text-[13px] text-ink underline-offset-2 hover:underline">{t('My trips')}</Link>
      </div>
    </div>
  )
}
