import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { CalendarDays, CircleCheck, CreditCard, Hash, MapPin, Plane, RotateCcw, Star, Users } from 'lucide-react'
import { api } from '../api'
import { useFetch } from '../hooks'
import { useI18n, useT } from '../i18n'
import { formatMoney } from '../market'
import { Spinner } from '../components/ui'
import { StatusPill } from './Auth'

const LOCALES = { en: 'en-GB', uz: 'uz-UZ', ru: 'ru-RU', fr: 'fr-FR', de: 'de-DE', es: 'es-ES' }
const today = () => new Date().toISOString().slice(0, 10)
// browsers write Uzbek dates as "2026 M12 20", so Uzbek month names are spelled here
const UZ_MONTHS = ['yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun', 'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr']
export function formatDay(d, lang) {
  if (!d) return ''
  const [y, m, day] = d.slice(0, 10).split('-').map(Number)
  if (lang === 'uz') return `${day}-${UZ_MONTHS[m - 1]}, ${y}`
  return new Date(y, m - 1, day, 12).toLocaleDateString(LOCALES[lang] || 'en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
}

/** Which list a trip belongs to: cancelled, past (finished or its last day is over) or upcoming. */
export function tripGroup(b) {
  if (b.status === 'cancelled') return 'cancelled'
  const last = b.end_date || b.travel_date
  if (b.status === 'completed' || (last && last < today())) return 'past'
  return 'upcoming'
}

const DEPOSIT_TONE = { paid: 'bg-[#f0fdf4] text-[#15803d]', pending: 'bg-amber-100 text-amber-900', failed: 'bg-red-100 text-red-900', refunded: 'bg-sky-100 text-sky-900', kept: 'bg-sand text-navy' }
const DEPOSIT_LABEL = { paid: 'Deposit paid', pending: 'Waiting for the deposit', failed: 'Deposit not paid', refunded: 'Deposit refunded', kept: 'Deposit not refunded' }

export function DepositBadge({ b }) {
  const t = useT()
  if (!b.deposit_status) return null
  return <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11.5px] font-medium ${DEPOSIT_TONE[b.deposit_status] || 'bg-sand text-navy'}`}>
    <CreditCard className="h-3.5 w-3.5" />{t(DEPOSIT_LABEL[b.deposit_status] || b.deposit_status)}{b.deposit_amount ? ` · ${formatMoney(b.deposit_amount, b.market)}` : ''}</span>
}

async function payAgain(b) {
  const res = await api.post(`/bookings/${b.id}/pay/`)
  if (res?.payment_url) window.location.assign(res.payment_url)
}

function TripCard({ b, onCancel }) {
  const t = useT()
  const { lang } = useI18n()
  const day = (d) => formatDay(d, lang)
  const group = tripGroup(b)
  const total = b.final_price_usd != null && b.final_price_usd !== '' ? Number(b.final_price_usd) - Number(b.discount_usd || 0) : Number(b.estimated_total_usd || 0)
  const tourLink = b.service_slug && ['tour', 'selection'].includes(b.service_type) ? `/tours/${b.service_slug}` : b.service_slug && b.service_type === 'hotel' ? `/hotels/${b.service_slug}` : null
  const meeting = b.meeting_place
    ? [day(b.arrival_date), b.arrival_time?.slice(0, 5), b.meeting_place].filter(Boolean).join(' · ')
    : (b.arrival_date || b.arrival_note) ? [day(b.arrival_date), b.arrival_time?.slice(0, 5), b.arrival_flight, b.arrival_note].filter(Boolean).join(' · ') : ''
  return (
    <article className="rounded-[12px] border border-navy/10 bg-card p-4 sm:p-5">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0">
          <h3 className="font-body text-[17px] font-bold leading-snug tracking-normal text-navy">{b.service_title_local || b.service_title}</h3>
          <p className="mt-1 inline-flex items-center gap-1 font-mono text-[12px] text-ink"><Hash className="h-3.5 w-3.5" />{b.reference}{b.market === 'local' && <span className="ml-2 rounded-full bg-[#f0fdf4] px-2 py-0.5 font-body text-[11px] text-[#15803d]">🇺🇿 {t('Local')}</span>}</p>
        </div>
        <div className="flex flex-wrap items-center gap-1.5"><StatusPill status={b.status} /><DepositBadge b={b} /></div>
      </div>
      <dl className="mt-4 grid gap-2.5 text-[13.5px] text-navy sm:grid-cols-2">
        <div className="flex items-start gap-2"><CalendarDays className="mt-0.5 h-4 w-4 shrink-0 text-turquoise-deep" /><span><span className="sr-only">{t('Date')}: </span>{b.travel_date ? `${day(b.travel_date)}${b.end_date && b.end_date !== b.travel_date ? ` → ${day(b.end_date)}` : ''}` : t('date TBC')}</span></div>
        <div className="flex items-start gap-2"><Users className="mt-0.5 h-4 w-4 shrink-0 text-turquoise-deep" /><span>{b.guests} {t('Guests')}</span></div>
        {meeting && <div className="flex items-start gap-2 sm:col-span-2">{b.meeting_place ? <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-turquoise-deep" /> : <Plane className="mt-0.5 h-4 w-4 shrink-0 text-turquoise-deep" />}<span><span className="text-ink">{t(b.meeting_place ? 'Meeting' : 'Arrival')}:</span> {meeting}</span></div>}
      </dl>
      <div className="mt-4 flex flex-wrap items-end justify-between gap-3 border-t border-navy/10 pt-3">
        <div>
          {total > 0 && <p className="text-[18px] font-bold text-navy">{formatMoney(total, b.market)}</p>}
          <p className="text-[11.5px] text-ink">{t(b.final_price_usd != null && b.final_price_usd !== '' ? 'Agreed price' : 'Estimated total')} · {t('Sent')} {day(b.created?.slice(0, 10))}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {tourLink && <Link to={tourLink} className="inline-flex h-9 items-center rounded-full border border-navy/20 px-4 text-[13px] font-medium text-navy hover:border-navy">{t(group === 'upcoming' ? 'View tour' : 'Book again')}{group !== 'upcoming' && <RotateCcw className="ml-1.5 h-3.5 w-3.5" />}</Link>}
          {group === 'past' && b.status === 'completed' && b.service_type === 'tour' && tourLink && <Link to={`${tourLink}#reviews`} className="inline-flex h-9 items-center gap-1.5 rounded-full bg-navy px-4 text-[13px] font-medium text-ivory hover:bg-navy-deep"><Star className="h-3.5 w-3.5" />{t('Write a review')}</Link>}
          {b.status === 'pending' && ['pending', 'failed'].includes(b.deposit_status) && <button type="button" onClick={() => payAgain(b)} className="inline-flex h-9 items-center gap-1.5 rounded-full bg-navy px-4 text-[13px] font-medium text-ivory hover:bg-navy-deep"><CreditCard className="h-3.5 w-3.5" />{t('Pay the deposit')}</button>}
          {group === 'upcoming' && ['pending', 'confirmed'].includes(b.status) && <button type="button" onClick={() => onCancel(b)} className="h-9 rounded-full px-3 text-[13px] text-destructive hover:bg-red-50">{t('Cancel')}</button>}
        </div>
      </div>
    </article>
  )
}

/** The traveller's trips from both versions of the site: upcoming, past and cancelled, newest first. */
export function TripHistory() {
  const t = useT()
  const bookings = useFetch('/bookings/', { list: true })
  const [params] = useSearchParams()
  const returned = params.get('payment')   // back from the payment page
  const paid = returned && bookings.data.find((b) => b.reference === returned)
  const [checks, setChecks] = useState(0)
  useEffect(() => {   // Octo confirms the payment to the server a moment later: look again a few times
    if (!paid || paid.deposit_status !== 'pending' || checks >= 10) return undefined
    const timer = setTimeout(() => { setChecks((n) => n + 1); bookings.reload() }, 3000)
    return () => clearTimeout(timer)
  }, [paid, checks])   // eslint-disable-line react-hooks/exhaustive-deps
  const groups = useMemo(() => {
    const out = { upcoming: [], past: [], cancelled: [] }
    bookings.data.forEach((b) => out[tripGroup(b)].push(b))
    out.upcoming.sort((a, b) => (a.travel_date || '9999').localeCompare(b.travel_date || '9999'))   // the next trip first
    return out
  }, [bookings.data])
  const [tab, setTab] = useState(null)
  const current = tab || (groups.upcoming.length || !bookings.data.length ? 'upcoming' : 'past')
  async function cancel(b) {
    if (!window.confirm(t('Cancel this request?'))) return
    await api.post(`/bookings/${b.id}/cancel/`); bookings.reload()
  }
  const tabs = [['upcoming', 'Upcoming'], ['past', 'Past trips'], ['cancelled', 'Cancelled']]
  const list = groups[current]
  return (
    <section aria-labelledby="trips-title">
      <h2 id="trips-title" className="font-heading text-[30px]">{t('Travel history')}</h2>
      {paid && (
        <p role="status" className={`mt-4 flex gap-2 rounded-sm border px-4 py-3 text-[14px] ${paid.deposit_status === 'paid' ? 'border-[#16a34a]/30 bg-[#f0fdf4] text-[#15803d]' : paid.deposit_status === 'failed' ? 'border-red-200 bg-red-50 text-red-800' : 'border-amber-200 bg-amber-50 text-amber-900'}`}>
          {paid.deposit_status === 'paid' ? <CircleCheck className="mt-0.5 h-4 w-4 shrink-0" /> : <CreditCard className="mt-0.5 h-4 w-4 shrink-0" />}
          {t(paid.deposit_status === 'paid' ? 'Thank you! The deposit is paid and your request {ref} has reached our team.' : paid.deposit_status === 'failed' ? 'The payment did not go through. You can pay the deposit again from the request {ref} below.' : 'We are checking your payment for the request {ref}…', { ref: paid.reference })}
        </p>
      )}
      <div role="tablist" className="mt-4 flex gap-2 overflow-x-auto pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {tabs.map(([key, label]) => (
          <button key={key} role="tab" aria-selected={current === key} type="button" onClick={() => setTab(key)}
            className={`h-10 shrink-0 whitespace-nowrap rounded-full border px-4 text-[14px] font-medium ${current === key ? 'border-navy bg-navy text-ivory' : 'border-navy/15 bg-white text-navy hover:border-navy'}`}>
            {t(label)} <span className={current === key ? 'text-ivory/70' : 'text-ink'}>({groups[key].length})</span>
          </button>
        ))}
      </div>
      {bookings.loading ? <div className="py-10"><Spinner /></div> : (
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          {list.map((b) => <TripCard key={b.id} b={b} onCancel={cancel} />)}
          {!list.length && (
            <p className="rounded-[12px] border border-dashed border-navy/20 p-6 text-ink lg:col-span-2">
              {t(current === 'upcoming' ? 'No upcoming trips yet.' : current === 'past' ? 'No past trips yet.' : 'No cancelled requests.')}{' '}
              <Link to="/tours" className="text-turquoise-deep">{t('Browse tours')}</Link>
            </p>
          )}
        </div>
      )}
    </section>
  )
}

export default function Trips() {
  const t = useT()
  return (
    <div className="shell py-12 lg:py-20">
      <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-turquoise-deep">{t('My account')}</p>
      <div className="mt-3"><TripHistory /></div>
    </div>
  )
}
