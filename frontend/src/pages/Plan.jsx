import { useMemo, useState } from 'react'
import { isLocal } from '../market'
import { CalendarDays, Check, Compass, Info, MapPin, PartyPopper, Route, Sparkles } from 'lucide-react'
import { api } from '../api'
import { money, useAuth, useFetch } from '../hooks'
import { useT } from '../i18n'
import { PHONE_RE, Photo, Spinner } from '../components/ui'
import SignInToBook from '../components/SignInToBook'
import { DepositNote, goToPayment, useDeposit } from '../components/Deposit'
import PhoneInput from '../components/PhoneInput'
import BookingCode from '../components/BookingCode'
import { PACKAGES } from '../components/PackageCard'
import { parseStop } from '../components/DayPlan'

const INTERESTS = ['History', 'Architecture', 'Food', 'Nature', 'Photography', 'Culture']
const BUDGETS = isLocal ? ["6 mln so'mgacha", "6 – 12 mln so'm", "12 – 21 mln so'm", "21 mln so'mdan ko'p"] : ['Under $700', '$700 – $1,400', '$1,400 – $2,500', '$2,500+']
const TRANSPORT = ['Private car with driver', 'Afrosiyob high-speed train', 'Minivan for the group', 'Premium vehicle']
const STAYS = ['Boutique hotel', 'Family guesthouse', 'Four-star hotel', 'Desert yurt camp']
const TRAVELERS = [1, 2, 3, 4, 5, 6, 8, 10, 15, 20]
const MAX_DAYS = 60

const chip = (on) => `rounded-full border px-3.5 py-1.5 text-[12.5px] transition-colors ${on ? 'border-navy bg-navy text-ivory' : 'border-navy/20 text-navy/75 hover:border-navy/50'}`
const toggle = (list, set) => (v) => set(list.includes(v) ? list.filter((x) => x !== v) : [...list, v])
const addDays = (iso, n) => new Date(new Date(iso).getTime() + n * 864e5).toISOString().slice(0, 10)

/** Sends the drafted journey to the team as a booking request (a tour request for a ready tour, otherwise "custom"). */
function SendItinerary({ plan }) {
  const t = useT()
  const { user } = useAuth()
  const deposit = useDeposit()
  const [f, setF] = useState({ full_name: user?.full_name || '', phone: '', meet_date: plan.from || '', meet_time: '', meet_place: '' })
  const [errors, setErrors] = useState({})
  const [state, setState] = useState('idle')
  const [reference, setReference] = useState('')
  const [message, setMessage] = useState('')
  const set = (k) => (e) => { setF((p) => ({ ...p, [k]: e.target.value })); setErrors((er) => ({ ...er, [k]: undefined })) }   // a field's error goes away as soon as it is corrected

  async function submit(e) {
    e.preventDefault()
    const err = {}
    if (f.full_name.trim().length < 2) err.full_name = 'Please tell us your name.'
    if (!PHONE_RE.test(f.phone.trim())) err.phone = 'Please enter your phone number.'
    if (!f.meet_date) err.meet_date = 'Choose the day.'
    if (!f.meet_time) err.meet_time = 'Choose the time.'
    if (!f.meet_place.trim()) err.meet_place = 'Write where we should meet you.'
    setErrors(err)
    if (Object.keys(err).length) return
    setState('saving'); setMessage('')
    try {
      const res = await api.post('/bookings-submit/', {
        service_type: plan.tour ? 'tour' : 'custom', service_slug: plan.tour?.slug || '',
        service_title: plan.tour ? plan.tour.title : `Custom journey · ${plan.totalDays} days`,
        full_name: f.full_name.trim(), email: user.email, phone: f.phone.trim(),
        travel_date: plan.from, end_date: plan.to, guests: Number(plan.travelers),
        details_summary: `${plan.summary}\n\nMeeting: ${f.meet_date} ${f.meet_time} · ${f.meet_place.trim()}`, special_requests: plan.outline,
        arrival_date: f.meet_date, arrival_time: f.meet_time, meeting_place: f.meet_place.trim(),
      })
      if (res.verification_required) { setReference(res.reference); setState('verifying'); return }   // the code e-mailed to the account first
      if (goToPayment(res)) return
      setReference(res.reference); setState('done')
    } catch (ex) { setState('error'); setMessage(ex.message) }
  }

  if (!user) return <SignInToBook className="mt-6" id="send-itinerary" />
  if (state === 'verifying') return <BookingCode className="mt-6" reference={reference} email={user.email} onVerified={() => setState('done')} />
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
      <div className="mt-4 space-y-3">{field('full_name', 'Full name')}<label className="label">{t('Email')}<input type="email" className="input bg-sand-soft/60 text-ink" value={user.email} readOnly /></label><label className="label">{t('Phone')}<PhoneInput value={f.phone} onChange={(v) => setF((p) => ({ ...p, phone: v }))} invalid={!!errors.phone} />
        {errors.phone && <span className="mt-1 block text-[11.5px] text-destructive">{t(errors.phone)}</span>}</label>
        <div className="grid grid-cols-2 gap-3">{field('meet_date', 'Meeting day', 'date')}{field('meet_time', 'Meeting time', 'time')}</div>
        {field('meet_place', 'Meeting place', 'text', t('For example: Samarkand airport, or your hotel and its address'))}</div>
      {message && <p role="alert" className="mt-3 text-[12px] text-destructive">{t(message)}</p>}
      <DepositNote deposit={deposit} />
      <button type="submit" disabled={state === 'saving'} className="btn-primary mt-4 w-full">{state === 'saving' && <Spinner />}{state === 'saving' ? t('Sending your itinerary') : deposit ? t('Send and pay {amount}', { amount: deposit.amount }) : t('Send this itinerary to our team')}</button>
    </form>
  )
}

/** The days of a ready tour, from its own day-by-day plan: the places visited each day (never repeated or invented). */
function tourDays(tour) {
  const stops = (tour.route || []).map(parseStop)
  return (tour.itinerary || []).map((day) => {
    const places = [...new Set(day.items.filter((x) => x.type === 'visit' || x.type === 'transfer').map((x) => stops[x.stop]?.name).filter(Boolean))]
    return { day: day.day, title: places.slice(0, 4).join(', '), more: Math.max(0, places.length - 4) }
  })
}

/** A journey of the visitor's own cities: each city's experiences once, in order; days beyond them are left to the team. */
function customDays(chosen, totalDays, t) {
  const share = Math.max(1, Math.floor(totalDays / chosen.length))
  const days = []
  chosen.forEach((d, idx) => {
    const ideas = d.activities?.length ? d.activities : [t('Guided city walk')]
    const count = Math.min(ideas.length, idx === chosen.length - 1 ? Math.max(1, totalDays - days.length) : share)
    ideas.slice(0, count).forEach((activity, i) => {
      if (days.length >= totalDays) return
      days.push({ day: days.length + 1, city: d.name, title: activity, arrive: i === 0 && idx > 0 })
    })
  })
  return days
}

export default function Plan() {
  const t = useT()
  const { data: destinations } = useFetch('/destinations/', { list: true })
  const { data: tours } = useFetch('/tours/', { list: true })
  const packages = useMemo(() => Object.keys(PACKAGES).map((slug) => tours.find((x) => x.slug === slug)).filter(Boolean), [tours])
  const [mode, setMode] = useState('tour')          // 'tour' = a ready tour, 'own' = the visitor's own cities
  const [tourSlug, setTourSlug] = useState('')
  const [cities, setCities] = useState([])
  const [arrival, setArrival] = useState('')
  const [back, setBack] = useState('')
  const [travelers, setTravelers] = useState('2')
  const [budget, setBudget] = useState(BUDGETS[1])
  const [interests, setInterests] = useState([])
  const [transport, setTransport] = useState(TRANSPORT[0])
  const [stay, setStay] = useState(STAYS[0])
  const [plan, setPlan] = useState(null)
  const [error, setError] = useState('')

  const today = new Date().toISOString().slice(0, 10)
  const tour = packages.find((x) => x.slug === tourSlug)
  const tourLength = tour?.itinerary?.length || 0
  // days of the trip, counting the arrival and the return day (1 to 7 November = 7 days)
  const tripDays = useMemo(() => {
    if (!arrival || !back) return 0
    const n = Math.round((new Date(back) - new Date(arrival)) / 864e5) + 1
    return n > 0 ? Math.min(n, MAX_DAYS) : 0
  }, [arrival, back])

  const reset = () => { setPlan(null); setError('') }
  const pickTour = (slug) => { setTourSlug(slug); reset() }

  function generate(e) {
    e.preventDefault()
    if (mode === 'tour' && !tour) { setError('Choose one of the ready tours, or switch to your own route.'); setPlan(null); return }
    if (mode === 'own' && !cities.length) { setError('Choose at least one destination for your journey.'); setPlan(null); return }
    if (!arrival) { setError('Please choose your arrival date so we can draft the route.'); setPlan(null); return }
    if (back && !tripDays) { setError('Your return date needs to be after the arrival date.'); setPlan(null); return }
    setError('')

    const chosen = destinations.filter((d) => cities.includes(d.slug))
    const totalDays = tripDays || (mode === 'tour' ? tourLength : Math.max(2, chosen.length * 2))
    const days = mode === 'tour' ? tourDays(tour) : customDays(chosen, totalDays, t)
    const planned = Math.min(days.length, totalDays)
    const to = back || addDays(arrival, totalDays - 1)
    const names = mode === 'tour' ? [tour.title] : chosen.map((d) => d.name)
    const extraDays = Math.max(0, totalDays - days.length)
    const short = mode === 'tour' && totalDays < tourLength ? tourLength : 0
    const outline = days.slice(0, mode === 'tour' ? days.length : planned).map((d) => `Day ${d.day}${d.city ? ` · ${d.city}` : ''} · ${d.title}`)
    if (extraDays) outline.push(`Days ${days.length + 1}–${totalDays}: free days — the team plans them with the traveller`)
    setPlan({
      tour: mode === 'tour' ? tour : null, days, totalDays, extraDays, short, travelers, transport, stay, interests: mode === 'own' ? interests : [],
      from: arrival, to, budget: mode === 'own' ? budget : '',
      summary: `${mode === 'tour' ? `Ready tour: ${tour.title}` : `Own route: ${names.join(' → ')}`} · ${totalDays} days (${arrival} → ${to})${extraDays ? ` · ${extraDays} extra days to plan` : ''} · ${travelers} travellers · ${transport} · ${stay}${mode === 'own' ? ` · ${budget}${interests.length ? ` · Interests: ${interests.join(', ')}` : ''}` : ''}`.slice(0, 600),
      outline: outline.join('\n').slice(0, 1900),
    })
    window.setTimeout(() => document.getElementById('plan-result')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50)
  }

  const step = (n, title) => <legend className="flex items-center gap-2.5 text-[15px] font-medium text-navy"><span className="grid h-7 w-7 place-items-center rounded-full bg-navy font-mono text-[12px] text-ivory">{n}</span>{t(title)}</legend>

  return (
    <div className="shell py-14 lg:py-20">
      <div className="max-w-2xl animate-rise-in">
        <p className="eyebrow">{t('Custom trip builder')}</p>
        <h1 className="display-lg mt-3 text-navy">{t('Your Uzbekistan, Your Way')}</h1>
        <p className="mt-4 text-[17px] leading-relaxed text-ink">{t('Pick a ready tour or your own cities, then your dates. You get a day-by-day draft that our team confirms with you.')}</p>
      </div>

      <div className="mt-10 grid gap-8 lg:grid-cols-[1.05fr_0.95fr] lg:gap-12">
        <form onSubmit={generate} className="space-y-9">
          <fieldset>
            {step(1, 'What kind of journey?')}
            <div className="mt-4 grid grid-cols-2 gap-2 rounded-full border border-navy/15 bg-white p-1" role="tablist">
              {[['tour', 'A ready tour', Compass], ['own', 'My own route', Route]].map(([key, label, Icon]) => (
                <button key={key} type="button" role="tab" aria-selected={mode === key} onClick={() => { setMode(key); reset() }}
                  className={`inline-flex h-11 items-center justify-center gap-2 rounded-full text-[13.5px] font-medium transition-colors ${mode === key ? 'bg-navy text-ivory' : 'text-navy/75 hover:bg-sand-soft'}`}><Icon className="h-4 w-4" />{t(label)}</button>
              ))}
            </div>
            {mode === 'tour' ? (
              <div className="mt-4 grid gap-3">
                {packages.map((x) => {
                  const on = tourSlug === x.slug
                  return (
                    <button key={x.slug} type="button" aria-pressed={on} onClick={() => pickTour(x.slug)}
                      className={`flex items-center gap-4 rounded-[12px] border p-3 text-left transition-colors ${on ? 'border-navy bg-sand-soft/70 ring-1 ring-navy' : 'border-navy/15 bg-white hover:border-navy/40'}`}>
                      <Photo src={x.image_url} alt="" sizes="96px" className="h-16 w-20 shrink-0 rounded-[8px] object-cover" />
                      <span className="min-w-0 flex-1">
                        <span className="block font-heading text-[18px] leading-tight text-navy">{x.title}</span>
                        <span className="mt-1 flex flex-wrap items-center gap-x-3 text-[12.5px] text-ink"><span className="inline-flex items-center gap-1"><CalendarDays className="h-3.5 w-3.5" />{t(x.duration_label)}</span>
                          <span>{t('from')} <b className="font-medium text-navy">{money(x.price_from_usd)}</b> / {t('person')}</span></span>
                      </span>
                      <span className={`grid h-6 w-6 shrink-0 place-items-center rounded-full border ${on ? 'border-navy bg-navy text-ivory' : 'border-navy/25'}`}>{on && <Check className="h-3.5 w-3.5" />}</span>
                    </button>
                  )
                })}
              </div>
            ) : (
              <div className="mt-4">
                <p className="text-[13px] text-ink">{t('Choose the cities you want to see.')}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {destinations.map((d) => <button key={d.slug} type="button" aria-pressed={cities.includes(d.slug)} onClick={() => { toggle(cities, setCities)(d.slug); reset() }} className={chip(cities.includes(d.slug))}>{d.name}</button>)}
                </div>
              </div>
            )}
          </fieldset>

          <fieldset>
            {step(2, 'When and how many people?')}
            <div className="mt-4 grid gap-4 sm:grid-cols-3">
              <label className="block text-[12px] text-ink">{t('Arrival')}<input type="date" min={today} value={arrival} onChange={(e) => { setArrival(e.target.value); reset() }} className="input" /></label>
              <label className="block text-[12px] text-ink">{t('Return')} <span className="text-ink/70">({t('optional')})</span><input type="date" min={arrival || today} value={back} onChange={(e) => { setBack(e.target.value); reset() }} className="input" /></label>
              <label className="block text-[12px] text-ink">{t('Travelers')}
                <select value={travelers} onChange={(e) => setTravelers(e.target.value)} className="input">{TRAVELERS.map((n) => <option key={n} value={n}>{n} {t(n === 1 ? 'traveler' : 'travelers')}</option>)}</select></label>
            </div>
            {tripDays > 0 && <p className="mt-2 text-[13px] text-navy"><CalendarDays className="mr-1 inline h-4 w-4 text-turquoise-deep" />{t('Your trip')}: <b className="font-medium">{tripDays} {t(tripDays === 1 ? 'day' : 'days')}</b>
              {mode === 'tour' && tour && tripDays !== tourLength && <span className="text-ink"> · {t('the tour itself takes {n} days', { n: tourLength })}</span>}</p>}
            {mode === 'tour' && tour && arrival && !back && <p className="mt-2 text-[12.5px] text-ink">{t('Without a return date we plan exactly the tour: {from} → {to}.', { from: arrival, to: addDays(arrival, tourLength - 1) })}</p>}
          </fieldset>

          <fieldset>
            {step(3, 'Comfort')}
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <label className="block text-[12px] text-ink">{t('Preferred transport')}<select value={transport} onChange={(e) => setTransport(e.target.value)} className="input">{TRANSPORT.map((x) => <option key={x} value={x}>{t(x)}</option>)}</select></label>
              <label className="block text-[12px] text-ink">{t('Accommodation')}<select value={stay} onChange={(e) => setStay(e.target.value)} className="input">{STAYS.map((x) => <option key={x} value={x}>{t(x)}</option>)}</select></label>
            </div>
            {mode === 'own' && (
              <div className="mt-5 space-y-4">
                <div><p className="text-[12px] text-ink">{t('Budget per person, excluding flights')}</p>
                  <div className="mt-2 flex flex-wrap gap-2">{BUDGETS.map((b) => <button key={b} type="button" aria-pressed={budget === b} onClick={() => setBudget(b)} className={chip(budget === b)}>{b}</button>)}</div></div>
                <div><p className="text-[12px] text-ink">{t('What interests you?')} <span className="text-ink/70">({t('optional')})</span></p>
                  <div className="mt-2 flex flex-wrap gap-2">{INTERESTS.map((i) => <button key={i} type="button" aria-pressed={interests.includes(i)} onClick={() => toggle(interests, setInterests)(i)} className={chip(interests.includes(i))}>{t(i)}</button>)}</div></div>
              </div>
            )}
          </fieldset>

          {error && <p role="alert" className="text-[13px] text-destructive">{t(error)}</p>}
          <button type="submit" className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-full bg-navy px-7 text-[14px] font-medium text-ivory hover:bg-navy-deep sm:w-auto">
            <Sparkles className="h-4 w-4" />{t('Show my day-by-day plan')}
          </button>
        </form>

        <aside id="plan-result" className="scroll-mt-24 rounded-[12px] border border-navy/12 bg-white p-5 sm:p-6 lg:sticky lg:top-24 lg:self-start lg:p-8">
          {plan ? (
            <div>
              <p className="eyebrow">{t('Your draft')}</p>
              <h2 className="mt-2 font-heading text-[26px] leading-tight text-navy">{plan.tour ? plan.tour.title : t('My own route')}</h2>
              <p className="mt-1 text-[13px] text-ink">{plan.from} → {plan.to} · {plan.totalDays} {t(plan.totalDays === 1 ? 'day' : 'days')} · {plan.travelers} {t('travelers')}</p>
              {plan.short > 0 && (
                <p className="mt-4 flex gap-2 rounded-sm border border-gold/50 bg-sand-soft/70 px-3 py-2 text-[12.5px] leading-snug text-navy">
                  <Info className="mt-0.5 h-4 w-4 shrink-0 text-gold" />{t('This tour takes {n} days but your dates give {d}. Choose a later return date or a shorter tour — or send it as it is and we will fit it together.', { n: plan.short, d: plan.totalDays })}</p>
              )}
              <ol className="mt-5 space-y-3">
                {plan.days.map((d) => (
                  <li key={d.day} className="flex gap-3">
                    <span className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full bg-navy font-mono text-[11px] text-ivory">{d.day}</span>
                    <div className="min-w-0 flex-1 border-b border-navy/10 pb-3">
                      <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-turquoise-deep">{t('Day')} {d.day}{d.city ? ` · ${d.city}` : ''}</p>
                      <p className="text-[14.5px] leading-snug text-navy">{d.arrive && <span className="text-ink">{t('Arrive by {transport}.', { transport: t(plan.transport).toLowerCase() })} </span>}{d.title || t('Free time')}{d.more > 0 && <span className="text-ink"> {t('and {n} more', { n: d.more })}</span>}</p>
                    </div>
                  </li>
                ))}
              </ol>
              {plan.extraDays > 0 && (
                <div className="mt-4 flex gap-3 rounded-[12px] border border-[#16a34a]/30 bg-[#f0fdf4] p-4">
                  <PartyPopper className="mt-0.5 h-5 w-5 shrink-0 text-[#15803d]" />
                  <div>
                    <p className="text-[14.5px] font-medium text-[#14532d]">{t('Your other {n} days will be just as enjoyable', { n: plan.extraDays })}</p>
                    <p className="mt-1 text-[13px] leading-relaxed text-[#166534]">{t(plan.tour
                      ? 'After the {tour} we plan the rest of your stay with you: cooking plov with a local family over an open fire, baking bread in a clay tandoor, strolling the bazaars and craft workshops, quiet rest days — whatever you wish.'
                      : 'We plan the rest of your stay with you: cooking plov with a local family over an open fire, baking bread in a clay tandoor, strolling the bazaars and craft workshops, quiet rest days — whatever you wish.', { tour: plan.tour?.title || '' })}</p>
                  </div>
                </div>
              )}
              <div className="mt-5 flex flex-wrap gap-2">
                {plan.interests.map((i) => <span key={i} className="inline-flex items-center gap-1 rounded-full bg-sand-soft px-2.5 py-1 text-[11px] text-navy/75"><Check className="h-3 w-3 text-turquoise-deep" />{t(i)}</span>)}
                <span className="inline-flex items-center gap-1 rounded-full bg-sand-soft px-2.5 py-1 text-[11px] text-navy/75"><MapPin className="h-3 w-3 text-turquoise-deep" />{t(plan.stay)}</span>
                <span className="inline-flex items-center rounded-full bg-sand-soft px-2.5 py-1 text-[11px] text-navy/75">{t(plan.transport)}</span>
              </div>
              <p className="mt-5 text-[12px] leading-relaxed text-ink">{t('This is a draft, not a confirmed reservation, price or availability. Send it to our team and we will confirm every detail personally.')}</p>
              <SendItinerary plan={plan} />
            </div>
          ) : (
            <div className="flex min-h-[280px] flex-col justify-center text-center">
              <div className="mx-auto grid h-12 w-12 place-items-center rounded-full border border-gold/40 bg-sand-soft"><Sparkles className="h-5 w-5 text-gold" /></div>
              <h2 className="mt-5 font-heading text-[24px] text-navy">{t('Your plan appears here')}</h2>
              <p className="mx-auto mt-3 max-w-sm text-[14px] leading-relaxed text-ink">{t('Choose a tour or your cities and the dates, then press the button.')}</p>
            </div>
          )}
        </aside>
      </div>
    </div>
  )
}
