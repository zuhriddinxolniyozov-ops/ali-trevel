import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { discounted, exactMoney, useAuth, useSettings } from '../hooks'
import { groupPercent } from '../groupPricing'
import { useT } from '../i18n'
import ArrivalForm from './ArrivalForm'
import GroupPrice from './GroupPrice'
import { EMAIL_RE, Field, Honeypot, PHONE_RE, Photo, Spinner, Success } from './ui'

const nightsBetween = (from, to) => (from && to ? Math.round((new Date(to) - new Date(from)) / 864e5) : 0)

/**
 * Booking request form shared by tours, hotels, transfers and the trip planner.
 *  - tours can offer an optional hotel (`hotels`): the traveller picks one, the nights and the rooms;
 *  - `mode="hotel"` turns it into a stay request (check-in, check-out, rooms) priced per night.
 * `estimatedTotal` is the (already discounted) price per guest, per night for hotels, or per booking when `perGuest` is false.
 * With `groupPriced` that price is for a group of 20 or more and smaller groups pay more per person (tiers from the admin panel);
 * `priceFor(guests, tiers)` replaces the per-person calculation, used when several tours are booked together.
 */
export default function BookingForm({ serviceType, serviceSlug = '', serviceTitle, estimatedTotal = 0, perGuest = true, extra = {}, intro, onSubmitted, hotels = [], defaultNights = 1, mode = 'standard', groupPriced = false, priceFor = null, unit = 'room', stayIncluded = false }) {
  const t = useT()
  const { user } = useAuth()
  const { settings } = useSettings()
  const isStay = mode === 'hotel'
  const tiers = settings.group_pricing_tiers
  const grouped = (groupPriced || !!priceFor) && !isStay
  const perPersonAt = (g) => (priceFor ? priceFor(g, tiers) : estimatedTotal * (groupPriced ? groupPercent(tiers, g) / 100 : 1))
  const [f, setF] = useState({ full_name: user?.full_name || '', email: user?.email || '', phone: '', travel_date: '', end_date: '', guests: 2, rooms: 1, special_requests: '', hotel: '', nights: defaultNights, website: '', hotel_class: '', car_class: '' })
  const [errors, setErrors] = useState({})
  const [state, setState] = useState('idle')
  const [message, setMessage] = useState('')
  const [reference, setReference] = useState('')
  const [sent, setSent] = useState(null)
  const set = (k) => (e) => setF((p) => ({ ...p, [k]: e.target.value }))
  const hotel = hotels.find((h) => h.slug === f.hotel)
  const upgrade = stayIncluded && (f.hotel_class || f.car_class)  // a higher class than the one in the price: costs extra
  const beds = isStay ? unit === 'bed' : hotel?.price_basis === 'bed'  // hostels are priced per dorm bed, not per room

  const money = useMemo(() => {
    const guests = Number(f.guests) || 1
    if (isStay) {
      const nights = Math.max(nightsBetween(f.travel_date, f.end_date), 0)
      return { base: estimatedTotal * nights * (Number(f.rooms) || 1), hotel: 0, nights }
    }
    const base = perGuest ? perPersonAt(guests) * guests : estimatedTotal
    const stay = hotel ? discounted(hotel.price_from_usd, hotel.effective_discount) * (Number(f.nights) || 1) * (Number(f.rooms) || 1) : 0
    return { base, hotel: stay, nights: Number(f.nights) || 1 }
  }, [f, estimatedTotal, perGuest, hotel, isStay, tiers, groupPriced, priceFor])
  const total = money.base + money.hotel

  async function submit(e) {
    e.preventDefault()
    const err = {}
    if (f.full_name.trim().length < 2) err.full_name = 'Please tell us your name.'
    if (!EMAIL_RE.test(f.email.trim())) err.email = 'A valid email is required.'
    if (!PHONE_RE.test(f.phone.trim())) err.phone = 'Include your country code, e.g. +998 90 123 45 67.'
    if (!f.travel_date) err.travel_date = isStay ? 'Choose your check-in date.' : 'Choose a date.'
    if (isStay && f.travel_date && money.nights < 1) err.end_date = 'Check-out must be after check-in.'
    setErrors(err)
    if (Object.keys(err).length) return
    setState('saving'); setMessage('')
    const lines = []
    if (isStay) lines.push(`Stay: ${money.nights} night(s) · ${f.rooms} ${beds ? 'bed(s)' : 'room(s)'}`)
    if (grouped) lines.push(`Group price: ${exactMoney(perPersonAt(Number(f.guests) || 1))} per person for ${Number(f.guests) || 1} traveler(s)`)
    if (stayIncluded) lines.push(`Hotels: ${f.hotel_class ? `${f.hotel_class}-star hotels requested (extra payment applies)` : 'the most affordable hotels, as in the price'}. Car: ${f.car_class ? 'premium class requested (extra payment applies)' : 'standard class, as in the price'}.`)
    if (hotel) lines.push(`Hotel: ${hotel.name} · ${f.nights} night(s) · ${f.rooms} ${beds ? 'bed(s)' : 'room(s)'} · ${exactMoney(money.hotel)}`)
    try {
      const res = await api.post('/bookings-submit/', {
        service_type: serviceType, service_slug: serviceSlug, service_title: serviceTitle,
        full_name: f.full_name.trim(), email: f.email.trim(), phone: f.phone.trim(),
        travel_date: f.travel_date, end_date: f.end_date || null, guests: Number(f.guests) || 1,
        website: f.website, special_requests: f.special_requests, estimated_total_usd: Math.round(total * 100) / 100, ...extra,
        details_summary: [extra.details_summary, ...lines].filter(Boolean).join('\n\n'),
      })
      setReference(res.reference); setSent({ guests: Number(f.guests) || 1, perPerson: perPersonAt(Number(f.guests) || 1), total }); setState('done')
      onSubmitted?.({ reference: res.reference, date: f.travel_date, guests: Number(f.guests) || 1, hotel: hotel?.name })
    } catch (ex) { setState('error'); setMessage(ex.message) }
  }

  if (state === 'done') {
    return (
      <div>
        <Success title="Request received">{t('Reference')} <span className="font-mono text-[12.5px]">{reference}</span> — {t('status pending. Nothing is booked or charged yet: our team will reply by email to confirm availability and the final price.')}</Success>
        {serviceType === 'tour' && <ArrivalForm reference={reference} email={f.email.trim()} date={f.travel_date} />}
        {grouped && sent && <GroupPrice tiers={tiers} priceAt={perPersonAt} guests={sent.guests} perPerson={sent.perPerson} total={sent.total} />}
      </div>
    )
  }
  return (
    <form id="book" onSubmit={submit} noValidate className="scroll-mt-24 rounded-sm border border-navy/12 bg-sand-soft/40 p-5">
      <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink">{t(isStay ? 'Request a stay' : 'Send a booking request')}</p>
      <p className="mt-2 text-[12.5px] leading-relaxed text-ink">{t(intro || 'No payment is taken. Our team confirms availability and sends a written confirmation.')}</p>
      <div className="relative mt-4 space-y-3">
        <Honeypot value={f.website} onChange={set('website')} />
        <Field label="Full name" error={errors.full_name}><input className="input" value={f.full_name} onChange={set('full_name')} /></Field>
        <Field label="Email" error={errors.email}><input type="email" className="input" value={f.email} onChange={set('email')} /></Field>
        <Field label="Phone / Telegram" error={errors.phone}><input type="tel" className="input" placeholder="+998 90 123 45 67" value={f.phone} onChange={set('phone')} /></Field>
        {isStay ? (
          <>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Check-in" error={errors.travel_date}><input type="date" className="input" value={f.travel_date} onChange={set('travel_date')} /></Field>
              <Field label="Check-out" error={errors.end_date}><input type="date" min={f.travel_date} className="input" value={f.end_date} onChange={set('end_date')} /></Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Guests"><input type="number" min="1" max="30" className="input" value={f.guests} onChange={set('guests')} /></Field>
              <Field label={beds ? 'Beds' : 'Rooms'}><input type="number" min="1" max="15" className="input" value={f.rooms} onChange={set('rooms')} /></Field>
            </div>
          </>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            <Field label="Date" error={errors.travel_date}><input type="date" className="input" value={f.travel_date} onChange={set('travel_date')} /></Field>
            <Field label="Guests"><input type="number" min="1" max="30" className="input" value={f.guests} onChange={set('guests')} /></Field>
          </div>
        )}

        {stayIncluded && (
          <fieldset className="rounded-sm border border-navy/12 bg-white/70 p-3">
            <legend className="px-1 font-mono text-[10px] uppercase tracking-[0.16em] text-ink">{t('Hotel and car class')}</legend>
            <p className="rounded-sm bg-gold/15 px-3 py-2 text-[12.5px] leading-snug text-navy">{t('The price includes the most affordable hotels and a standard taxi. Hotels of 3, 4 or 5 stars and a premium-class taxi cost extra.')}</p>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <Field label="Hotel class"><select className="input" value={f.hotel_class} onChange={set('hotel_class')}>
                <option value="">{t('Included: the most affordable hotel')}</option>
                {['3', '4', '5'].map((n) => <option key={n} value={n}>{t('{n}-star hotel (extra payment)', { n })}</option>)}
              </select></Field>
              <Field label="Car class"><select className="input" value={f.car_class} onChange={set('car_class')}>
                <option value="">{t('Included: standard taxi')}</option>
                <option value="premium">{t('Premium-class taxi (extra payment)')}</option>
              </select></Field>
            </div>
            {upgrade && <p role="status" className="mt-3 rounded-sm border border-destructive/30 bg-destructive/5 px-3 py-2 text-[12.5px] leading-snug text-destructive">{t('Extra payment applies: you chose a higher class than the one in the price. Our team confirms the exact extra amount before anything is booked or charged.')}</p>}
          </fieldset>
        )}
        {!stayIncluded && hotels.length > 0 && (
          <fieldset className="rounded-sm border border-navy/12 bg-white/70 p-3">
            <legend className="px-1 font-mono text-[10px] uppercase tracking-[0.16em] text-ink">{t('Hotel (optional)')}</legend>
            <select aria-label={t('Choose a hotel')} className="input !mt-1" value={f.hotel} onChange={set('hotel')}>
              <option value="">{t('No hotel — I will arrange my own')}</option>
              {hotels.map((h) => (
                <option key={h.slug} value={h.slug}>{h.name} · {'★'.repeat(h.stars)} · {exactMoney(discounted(h.price_from_usd, h.effective_discount))} / {t(h.price_basis === 'bed' ? 'bed per night' : 'night')}</option>
              ))}
            </select>
            {hotel && (
              <div className="mt-3 space-y-3">
                <div className="flex gap-3 rounded-sm bg-sand-soft/60 p-2">
                  <Photo src={hotel.image_url} sizes="80px" alt={hotel.name} className="h-14 w-20 shrink-0 rounded object-cover" />
                  <p className="text-[12.5px] leading-snug text-ink"><span className="block font-medium text-navy">{hotel.name}</span>{hotel.summary}</p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Nights"><input type="number" min="1" max="30" className="input" value={f.nights} onChange={set('nights')} /></Field>
                  <Field label={beds ? 'Beds' : 'Rooms'}><input type="number" min="1" max="15" className="input" value={f.rooms} onChange={set('rooms')} /></Field>
                </div>
                <p className="text-[12px] text-ink">{t('If your tour already includes accommodation, our team adjusts the price to the hotel you choose.')}</p>
              </div>
            )}
          </fieldset>
        )}
        <Field label="Special requests"><textarea rows={3} className="input" value={f.special_requests} onChange={set('special_requests')} /></Field>
      </div>
      {total > 0 && (
        <p className="mt-3 text-[12.5px] text-ink">{t('Estimated total')}: <span className="font-mono text-[15px] text-navy">{exactMoney(total)}</span>
          {money.hotel > 0 && <span className="block">{t('Tour')} {exactMoney(money.base)} + {t('Hotel')} {exactMoney(money.hotel)}</span>}
          {upgrade && <span className="block text-destructive">{t('Without the extra payment for the higher class')}</span>}
          <span className="block">({t('sample rate, confirmed by our team')})</span></p>
      )}
      {grouped && total > 0 && <GroupPrice tiers={tiers} priceAt={perPersonAt} guests={f.guests} perPerson={perPersonAt(Number(f.guests) || 1)} total={money.base} />}
      {message && <p role="alert" className="mt-3 text-[12px] text-destructive">{message}</p>}
      <button type="submit" disabled={state === 'saving'} className="btn-primary mt-4 w-full">{state === 'saving' && <Spinner />}{state === 'saving' ? t('Sending') : t('Send request')}</button>
    </form>
  )
}

/**
 * Phones: the booking form sits far down a long page, so a bar at the bottom of the screen shows the price and a button that
 * scrolls to the form. The bar steps aside while the form itself is on screen.
 */
export function MobileBookBar({ price, unit }) {
  const t = useT()
  const [hidden, setHidden] = useState(false)
  useEffect(() => {
    const form = document.getElementById('book')
    document.body.classList.add('has-book-bar')
    let watch
    if (form && 'IntersectionObserver' in window) {
      watch = new IntersectionObserver(([e]) => setHidden(e.isIntersecting), { rootMargin: '0px 0px -20% 0px' })
      watch.observe(form)
    }
    return () => { document.body.classList.remove('has-book-bar'); watch?.disconnect() }
  }, [])
  const go = () => {
    const form = document.getElementById('book')
    if (!form) return
    form.scrollIntoView({ behavior: 'smooth', block: 'start' })
    setTimeout(() => form.querySelector('input:not([type=hidden]):not([tabindex="-1"])')?.focus({ preventScroll: true }), 600)
  }
  return (
    <div className={`fixed inset-x-0 bottom-0 z-40 border-t border-navy/10 bg-ivory/95 px-4 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-3 shadow-[0_-12px_30px_-24px_rgba(0,35,102,0.6)] backdrop-blur transition-transform duration-300 lg:hidden print:hidden ${hidden ? 'translate-y-full' : ''}`}>
      <div className="mx-auto flex max-w-xl items-center justify-between gap-3">
        {price ? <p className="min-w-0 text-navy"><span className="block font-mono text-[10px] uppercase tracking-[0.16em] text-ink">{t('From')}</span>
          <span className="text-[20px] font-medium">{price}</span>{unit && <span className="ml-1 text-[13px] text-ink">/ {t(unit)}</span>}</p> : <span />}
        <button type="button" onClick={go} className="btn-primary h-12 shrink-0 px-7 text-[14px]">{t('Book now')}</button>
      </div>
    </div>
  )
}
