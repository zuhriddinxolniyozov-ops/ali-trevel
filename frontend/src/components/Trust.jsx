import { useState } from 'react'
import { Link } from 'react-router-dom'
import { BadgeCheck, CalendarX2, ChevronDown, ShieldCheck, Star, Users, Wallet } from 'lucide-react'
import { api } from '../api'
import { useFetch, useSettings } from '../hooks'
import { useT } from '../i18n'
import { Field, Honeypot, Spinner, Success } from './ui'
import { Socials } from './Socials'

/* Reasons to book, taken from the tour itself and from the real policies: nothing here promises more than the Terms and the Cancellation Policy. */
export function TrustPanel({ tour }) {
  const t = useT()
  const items = [
    [CalendarX2, t('Free cancellation up to 30 days before the start'), <Link key="p" to="/legal/cancellation" className="underline underline-offset-2 hover:text-navy">{t('See the cancellation policy')}</Link>],
    [Wallet, t('Reserve now, pay later'), t('No payment is taken online. Our team confirms your booking in writing first.')],
    tour.max_travelers ? [Users, t('Small groups — up to {n} travelers', { n: tour.max_travelers }), t('Private departures are available on request.')] : null,
    tour.pickup_included ? [ShieldCheck, t('Pickup included'), t('Your local guide meets you at the agreed place.')] : null,
  ].filter(Boolean)
  return (
    <ul className="space-y-3 rounded-sm border border-navy/10 bg-white p-5">
      {items.map(([Icon, title, body], i) => (
        <li key={i} className="flex gap-3">
          <Icon className="mt-0.5 h-5 w-5 shrink-0 text-turquoise-deep" strokeWidth={1.6} />
          <div><p className="text-[14px] font-medium text-navy">{title}</p><p className="text-[12.5px] leading-snug text-ink">{body}</p></div>
        </li>
      ))}
    </ul>
  )
}

const FAQ = [
  ['Can I cancel or change my booking?', 'Yes. Cancellation is free up to 30 days before the start, and date changes made 14 days or more ahead are free, subject to availability. The full rules are in our Cancellation Policy.'],
  ['When do I pay?', 'You pay nothing when you send the request. After our team confirms availability in writing, we agree the payment with you.'],
  ['Can I join a private tour instead of a group?', 'Yes. Write it in the special requests and we will offer a private departure and its price.'],
  ['I am vegetarian or have an allergy. What should I do?', 'Tell us in the special requests when you book. Our team will pass it on to the cook, the guesthouse and your guide.'],
  ['What happens after I send the request?', 'You receive a booking reference at once. Our team replies by email with the confirmed schedule, so you can plan with peace of mind.'],
]

export function TourFaq() {
  const t = useT()
  return (
    <div className="mt-12">
      <h3 className="font-heading text-[26px]">{t('Good to know')}</h3>
      <div className="mt-3 divide-y divide-navy/10 rounded-sm border border-navy/10 bg-white">
        {FAQ.map(([q, a]) => (
          <details key={q} className="group px-4 py-3">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-[15px] font-medium text-navy">{t(q)}<ChevronDown className="h-4 w-4 shrink-0 transition-transform group-open:rotate-180" /></summary>
            <p className="mt-2 text-[14px] leading-relaxed text-ink">{t(a)}</p>
          </details>
        ))}
      </div>
    </div>
  )
}

function Stars({ value, size = 'h-4 w-4' }) {
  return <span className="inline-flex" aria-label={`${value} / 5`}>{[1, 2, 3, 4, 5].map((i) => <Star key={i} className={`${size} ${i <= value ? 'fill-gold text-gold' : 'text-navy/20'}`} />)}</span>
}

export function ReviewCard({ review: r }) {
  const t = useT()
  return (
    <figure className="rounded-[4px] border border-navy/10 bg-card p-6">
      <Stars value={r.rating} />
      <blockquote className="mt-3 text-[15px] leading-relaxed text-navy">“{r.text}”</blockquote>
      <figcaption className="mt-4 text-[13px] text-ink">
        <span className="font-medium text-navy">{r.name}</span>{r.country ? `, ${r.country}` : ''}
        {r.verified && <span className="ml-2 inline-flex items-center gap-1 text-turquoise-deep"><BadgeCheck className="h-3.5 w-3.5" />{t('Verified traveller')}</span>}
      </figcaption>
    </figure>
  )
}

function ReviewForm({ tour }) {
  const t = useT()
  const { settings } = useSettings()
  const [f, setF] = useState({ name: '', country: '', rating: 5, text: '', email: '', reference: '', website: '' })
  const [state, setState] = useState('idle')
  const [message, setMessage] = useState('')
  const set = (k) => (e) => setF((x) => ({ ...x, [k]: e.target.value }))
  const submit = async (e) => {
    e.preventDefault()
    setState('sending'); setMessage('')
    try { await api.post('/reviews/', { ...f, rating: Number(f.rating), tour_slug: tour.slug }); setState('done') }
    catch (ex) { setState('error'); setMessage(ex.message) }
  }
  if (state === 'done') {
    return (
      <Success title={t('Thank you for your review')}>
        <p>{t('Thank you from all of us at ALI TRAVEL — your words help other travellers choose with confidence.')}</p>
        <p className="mt-2">{t('We publish reviews after a quick check. Reviews from travellers with a matching booking reference get a “Verified traveller” mark.')}</p>
        <p className="mt-4 font-medium text-navy">{t('Follow us on social networks for more photos, videos and travel stories from Uzbekistan:')}</p>
        <Socials settings={settings} className="mt-2" />
        <p className="mt-4 font-medium text-navy">{t('We look forward to welcoming you again!')}</p>
      </Success>
    )
  }
  return (
    <form onSubmit={submit} className="relative mt-6 space-y-4 rounded-sm border border-navy/10 bg-white p-5">
      <Honeypot value={f.website} onChange={set('website')} />
      <p className="font-medium text-navy">{t('Share your experience')}</p>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Your name"><input required className="input" value={f.name} onChange={set('name')} /></Field>
        <Field label="Country"><input className="input" value={f.country} onChange={set('country')} /></Field>
      </div>
      <Field label="Rating"><select className="input" value={f.rating} onChange={set('rating')}>{[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{'★'.repeat(n)}</option>)}</select></Field>
      <Field label="Your review"><textarea required rows={4} maxLength={2000} className="input" value={f.text} onChange={set('text')} /></Field>
      <details className="text-[13px] text-ink">
        <summary className="cursor-pointer">{t('I travelled with ALI TRAVEL (optional)')}</summary>
        <div className="mt-3 grid gap-4 sm:grid-cols-2">
          <Field label="Booking reference"><input className="input" value={f.reference} onChange={set('reference')} /></Field>
          <Field label="Email used for the booking"><input type="email" className="input" value={f.email} onChange={set('email')} /></Field>
        </div>
      </details>
      {state === 'error' && <p className="text-[13px] text-destructive">{message}</p>}
      <button disabled={state === 'sending'} className="btn-primary">{state === 'sending' ? <Spinner /> : t('Send review')}</button>
    </form>
  )
}

export function TourReviews({ tour }) {
  const t = useT()
  const { data } = useFetch(`/reviews/?tour_slug=${tour.slug}`, { list: true })
  const [open, setOpen] = useState(false)
  return (
    <div className="mt-12">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="font-heading text-[26px]">{t('Traveller reviews')}</h3>
        {data.length > 0 && <span className="inline-flex items-center gap-2 text-[14px] text-ink"><Stars value={Math.round(Number(tour.rating))} /><span className="font-mono text-navy">{Number(tour.rating).toFixed(1)}</span>({data.length})</span>}
      </div>
      {data.length === 0 && <p className="mt-3 text-[14px] text-ink">{t('No reviews yet. Travelled with us? Be the first to share your experience.')}</p>}
      <div className="mt-4 grid gap-4">{data.map((r) => <ReviewCard key={r.id} review={r} />)}</div>
      {open ? <ReviewForm tour={tour} /> : <button onClick={() => setOpen(true)} className="btn-outline mt-5 !h-10 text-[13px]">{t('Write a review')}</button>}
    </div>
  )
}

/* A round Telegram button on every page: it opens the company's Telegram (the link in Contact & settings). */
export function ChatButton() {
  const t = useT()
  const { settings } = useSettings()
  const url = String(settings.telegram_url || '')
  if (!url.startsWith('https://')) return null
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" aria-label={t('Chat with us on Telegram')} title={t('Chat with us on Telegram')}
      className="chat-button fixed bottom-5 right-5 z-40 grid h-14 w-14 place-items-center rounded-full bg-[#229ED9] text-white shadow-lg shadow-[#229ED9]/30 transition-transform hover:scale-105 print:hidden">
      <svg viewBox="0 0 24 24" className="-ml-0.5 h-7 w-7" fill="currentColor" aria-hidden="true"><path d="M21.6 3.3 2.9 10.5c-1.3.5-1.3 1.2-.2 1.6l4.8 1.5 1.8 5.6c.2.6.1.9.8.9.5 0 .7-.2 1-.5l2.3-2.2 4.8 3.5c.9.5 1.5.2 1.7-.8l3.1-14.7c.3-1.3-.5-1.9-1.4-1.5zM8.3 13.3l10.4-6.6c.5-.3.9-.1.6.2l-8.9 8-.3 3.8z" /></svg>
    </a>
  )
}
