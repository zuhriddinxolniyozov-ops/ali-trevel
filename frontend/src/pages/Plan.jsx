import { useMemo, useState } from 'react'
import { Check, Info, Sparkles } from 'lucide-react'
import { api } from '../api'
import { useFetch } from '../hooks'
import { useT } from '../i18n'
import { EMAIL_RE, PHONE_RE, Spinner } from '../components/ui'

const INTERESTS = ['History', 'Architecture', 'Food', 'Nature', 'Photography', 'Culture']
const BUDGETS = ['Under $700', '$700 – $1,400', '$1,400 – $2,500', '$2,500+']
const TRANSPORT = ['Private car with driver', 'Afrosiyob high-speed train', 'Minivan for the group', 'Premium vehicle']
const STAYS = ['Boutique hotel', 'Family guesthouse', 'Four-star hotel', 'Desert yurt camp']
const TRAVELERS = [1, 2, 3, 4, 5, 6, 8, 10]

const chip = (on) => `rounded-full border px-3.5 py-1.5 text-[12.5px] transition-colors ${on ? 'border-navy bg-navy text-ivory' : 'border-navy/20 text-navy/75 hover:border-navy/50'}`
const toggle = (list, set) => (v) => set(list.includes(v) ? list.filter((x) => x !== v) : [...list, v])

/** Sends the generated itinerary to the team as a booking request of type "custom". */
function SendItinerary({ plan }) {
  const t = useT()
  const [f, setF] = useState({ full_name: '', email: '', phone: '' })
  const [errors, setErrors] = useState({})
  const [state, setState] = useState('idle')
  const [reference, setReference] = useState('')
  const [message, setMessage] = useState('')
  const set = (k) => (e) => setF((p) => ({ ...p, [k]: e.target.value }))

  async function submit(e) {
    e.preventDefault()
    const err = {}
    if (f.full_name.trim().length < 2) err.full_name = 'Please tell us your name.'
    if (!EMAIL_RE.test(f.email.trim())) err.email = 'A valid email is required.'
    if (!PHONE_RE.test(f.phone.trim())) err.phone = 'Include your country code, e.g. +998 90 123 45 67.'
    setErrors(err)
    if (Object.keys(err).length) return
    setState('saving'); setMessage('')
    try {
      const res = await api.post('/bookings-submit/', {
        service_type: 'custom', service_slug: '', service_title: `Custom journey · ${plan.nights} nights`,
        full_name: f.full_name.trim(), email: f.email.trim(), phone: f.phone.trim(),
        travel_date: plan.from, end_date: plan.to, guests: Number(plan.travelers),
        details_summary: plan.summary, special_requests: plan.outline,
      })
      setReference(res.reference); setState('done')
    } catch (ex) { setState('error'); setMessage(ex.message) }
  }

  if (state === 'done') {
    return (
      <div className="mt-6 flex items-start gap-3 rounded-sm border border-turquoise-deep/30 bg-sand-soft/60 p-5">
        <Check className="mt-0.5 h-5 w-5 shrink-0 text-turquoise-deep" />
        <div><p className="text-[14px] font-medium">{t('Itinerary request received')}</p>
          <p className="mt-1 text-[13px] leading-relaxed text-navy/80">{t('Reference')} <span className="font-mono text-[12.5px]">{reference}</span> — {t('status pending. Nothing is booked or charged yet: our team will reply by email to confirm the route, dates and price.')}</p></div>
      </div>
    )
  }
  const field = (k, label, type = 'text', placeholder) => (
    <label className="label">{t(label)}<input type={type} className="input" placeholder={placeholder} value={f[k]} onChange={set(k)} aria-invalid={!!errors[k]} />
      {errors[k] && <span className="mt-1 block text-[11.5px] text-destructive">{t(errors[k])}</span>}</label>
  )
  return (
    <form onSubmit={submit} noValidate className="mt-6 rounded-sm border border-navy/12 bg-sand-soft/40 p-5">
      <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink">{t('Send to our team')}</p>
      <p className="mt-2 text-[12.5px] leading-relaxed text-ink">{t('This saves your draft as a request so a person can reply. No payment is taken.')}</p>
      <div className="mt-4 space-y-3">{field('full_name', 'Full name')}{field('email', 'Email', 'email')}{field('phone', 'Phone / WhatsApp', 'tel', '+998 90 123 45 67')}</div>
      {message && <p role="alert" className="mt-3 text-[12px] text-destructive">{message}</p>}
      <button type="submit" disabled={state === 'saving'} className="btn-primary mt-4 w-full">{state === 'saving' && <Spinner />}{state === 'saving' ? t('Sending your itinerary') : t('Send this itinerary to our team')}</button>
    </form>
  )
}

export default function Plan() {
  const t = useT()
  const { data: destinations } = useFetch('/destinations/', { list: true })
  const [cities, setCities] = useState([])
  const [arrival, setArrival] = useState('')
  const [back, setBack] = useState('')
  const [travelers, setTravelers] = useState('2')
  const [budget, setBudget] = useState(BUDGETS[2])
  const [interests, setInterests] = useState([])
  const [transport, setTransport] = useState(TRANSPORT[0])
  const [stay, setStay] = useState(STAYS[0])
  const [plan, setPlan] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const today = new Date().toISOString().slice(0, 10)
  const nights = useMemo(() => {
    if (!arrival || !back) return 0
    const n = Math.round((new Date(back) - new Date(arrival)) / 864e5)
    return n > 0 ? Math.min(n, 21) : 0
  }, [arrival, back])

  function generate(e) {
    e.preventDefault()
    if (!cities.length) { setError('Choose at least one destination for your journey.'); setPlan(null); return }
    if (!arrival) { setError('Please choose your arrival date so we can draft the route.'); setPlan(null); return }
    if (back && !nights) { setError('Your return date needs to be after the arrival date.'); setPlan(null); return }
    setError(''); setBusy(true)

    const chosen = destinations.filter((d) => cities.includes(d.slug))
    const total = nights || chosen.length * 2
    const base = Math.floor(total / chosen.length)
    const extra = total % chosen.length
    const days = []
    let day = 1
    chosen.forEach((d, idx) => {
      const count = Math.max(1, base + (idx < extra ? 1 : 0))
      for (let i = 0; i < count; i += 1) {
        const activity = d.activities?.[i % (d.activities?.length || 1)] || t('Guided city walk')
        days.push({
          day, city: d.name, title: activity,
          detail: i === 0 && idx > 0 ? `${t('Arrive in {city} by {transport}.', { city: d.name, transport: t(transport).toLowerCase() })} ${activity}` : t('{activity} · overnight in {city}', { activity, city: d.name }),
        })
        day += 1
      }
    })
    window.setTimeout(() => {
      const to = back || new Date(new Date(arrival).getTime() + total * 864e5).toISOString().slice(0, 10)
      const names = chosen.map((d) => d.name)
      setPlan({
        days, nights: total, travelers, budget, interests, transport, stay, cities: names, from: arrival, to,
        summary: `Custom journey · ${total} nights · ${names.join(' → ')} · ${travelers} travellers · ${budget} · ${transport} · ${stay}${interests.length ? ` · Interests: ${interests.join(', ')}` : ''}`.slice(0, 600),
        outline: days.map((d) => `Day ${d.day} · ${d.city} · ${d.title} — ${d.detail}`).join('\n').slice(0, 1900),
      })
      setBusy(false)
    }, 500)
  }

  return (
    <div className="shell py-14 lg:py-20">
      <div className="max-w-2xl animate-rise-in">
        <p className="eyebrow">{t('Custom trip builder')}</p>
        <h1 className="display-lg mt-3 text-navy">{t('Your Uzbekistan, Your Way')}</h1>
        <p className="mt-4 text-[17px] leading-relaxed text-ink">{t('Tell us your cities, dates and interests. We will sketch the outline, then refine it together over email or WhatsApp.')}</p>
      </div>

      <div className="mt-12 grid gap-8 lg:grid-cols-[1.05fr_0.95fr] lg:gap-12">
        <form onSubmit={generate} className="space-y-7">
          <fieldset>
            <legend className="eyebrow">{t('1 · Where would you like to go?')}</legend>
            <div className="mt-3 flex flex-wrap gap-2">
              {destinations.map((d) => <button key={d.slug} type="button" aria-pressed={cities.includes(d.slug)} onClick={() => toggle(cities, setCities)(d.slug)} className={chip(cities.includes(d.slug))}>{d.name}</button>)}
            </div>
          </fieldset>

          <fieldset className="grid gap-4 sm:grid-cols-3">
            <legend className="eyebrow mb-3">{t('2 · When and with whom?')}</legend>
            <label className="block text-[12px] text-ink">{t('Arrival')}<input type="date" min={today} value={arrival} onChange={(e) => setArrival(e.target.value)} className="input" /></label>
            <label className="block text-[12px] text-ink">{t('Return')}<input type="date" min={arrival || today} value={back} onChange={(e) => setBack(e.target.value)} className="input" /></label>
            <label className="block text-[12px] text-ink">{t('Travelers')}
              <select value={travelers} onChange={(e) => setTravelers(e.target.value)} className="input">{TRAVELERS.map((n) => <option key={n} value={n}>{n} {t(n === 1 ? 'traveler' : 'travelers')}</option>)}</select></label>
          </fieldset>

          <fieldset>
            <legend className="eyebrow">{t('3 · Budget per person, excluding flights')}</legend>
            <div className="mt-3 flex flex-wrap gap-2">{BUDGETS.map((b) => <button key={b} type="button" aria-pressed={budget === b} onClick={() => setBudget(b)} className={chip(budget === b)}>{b}</button>)}</div>
          </fieldset>

          <fieldset>
            <legend className="eyebrow">{t('4 · What interests you?')}</legend>
            <div className="mt-3 flex flex-wrap gap-2">{INTERESTS.map((i) => <button key={i} type="button" aria-pressed={interests.includes(i)} onClick={() => toggle(interests, setInterests)(i)} className={chip(interests.includes(i))}>{t(i)}</button>)}</div>
          </fieldset>

          <fieldset className="grid gap-4 sm:grid-cols-2">
            <legend className="eyebrow mb-3">{t('5 · Comfort and transport')}</legend>
            <label className="block text-[12px] text-ink">{t('Preferred transport')}<select value={transport} onChange={(e) => setTransport(e.target.value)} className="input">{TRANSPORT.map((x) => <option key={x} value={x}>{t(x)}</option>)}</select></label>
            <label className="block text-[12px] text-ink">{t('Accommodation')}<select value={stay} onChange={(e) => setStay(e.target.value)} className="input">{STAYS.map((x) => <option key={x} value={x}>{t(x)}</option>)}</select></label>
          </fieldset>

          {error && <p role="alert" className="text-[13px] text-destructive">{t(error)}</p>}
          <button type="submit" disabled={busy} className="inline-flex h-12 items-center gap-2 rounded-full bg-navy px-7 text-[14px] font-medium text-ivory hover:bg-navy-deep disabled:opacity-70">
            {busy ? <Spinner /> : <Sparkles className="h-4 w-4" />}{busy ? t('Building your itinerary') : t('Generate my itinerary')}
          </button>
        </form>

        <aside className="rounded-[4px] border border-navy/12 bg-white p-6 lg:p-8">
          {plan ? (
            <div>
              <div className="flex items-start justify-between gap-4">
                <div><p className="eyebrow">{t('Recommendation')}</p>
                  <h2 className="mt-2 font-heading text-[26px] text-navy">{plan.nights} {t(plan.nights === 1 ? 'night' : 'nights')} · {plan.cities.length} {t(plan.cities.length === 1 ? 'city' : 'cities')}</h2></div>
                <span className="rounded-full border border-gold/50 bg-sand-soft px-3 py-1 font-mono text-[9px] uppercase tracking-[0.16em] text-navy/70">{t('Draft')}</span>
              </div>
              <ol className="mt-6 space-y-4">
                {plan.days.map((d) => (
                  <li key={d.day} className="flex gap-4">
                    <span className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full bg-navy font-mono text-[11px] text-ivory">{d.day}</span>
                    <div className="border-b border-navy/10 pb-3"><p className="font-mono text-[10px] uppercase tracking-[0.16em] text-turquoise-deep">{d.city}</p>
                      <p className="text-[15px] font-medium text-navy">{d.title}</p><p className="text-[13px] leading-relaxed text-ink">{d.detail}</p></div>
                  </li>
                ))}
              </ol>
              <div className="mt-6 flex flex-wrap gap-2">
                {plan.interests.map((i) => <span key={i} className="inline-flex items-center gap-1 rounded-full bg-sand-soft px-2.5 py-1 text-[11px] text-navy/75"><Check className="h-3 w-3 text-turquoise-deep" />{t(i)}</span>)}
                <span className="inline-flex items-center rounded-full bg-sand-soft px-2.5 py-1 text-[11px] text-navy/75">{t(plan.stay)}</span>
                <span className="inline-flex items-center rounded-full bg-sand-soft px-2.5 py-1 text-[11px] text-navy/75">{t(plan.transport)}</span>
              </div>
              <div className="mt-6 flex gap-3 rounded-sm border border-gold/40 bg-sand-soft/70 p-4">
                <Info className="mt-0.5 h-4 w-4 shrink-0 text-gold" />
                <p className="text-[12.5px] leading-relaxed text-navy/75">{t('This is a recommendation based on sample itineraries — not a confirmed reservation, price or availability. Send it to our team and we will confirm every detail personally.')}</p>
              </div>
              <p className="mt-5 text-[12px] text-ink">{plan.from} → {plan.to} · {plan.travelers} {t('travelers')}</p>
              <SendItinerary plan={plan} />
            </div>
          ) : (
            <div className="flex h-full min-h-[320px] flex-col justify-center text-center">
              <div className="mx-auto grid h-12 w-12 place-items-center rounded-full border border-gold/40 bg-sand-soft"><Sparkles className="h-5 w-5 text-gold" /></div>
              <h2 className="mt-5 font-heading text-[26px] text-navy">{t('Your suggested journey appears here')}</h2>
              <p className="mx-auto mt-3 max-w-sm text-[14px] leading-relaxed text-ink">{t('Pick your cities, dates and interests. We will draft a day-by-day outline from our current sample itineraries — a starting point our team refines with you.')}</p>
            </div>
          )}
        </aside>
      </div>
    </div>
  )
}
