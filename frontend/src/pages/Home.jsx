import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowDown, ArrowRight, Car, Headset, Palette, Route, ShieldCheck, Star, Wallet } from 'lucide-react'
import { api } from '../api'
import { Reveal, useFetch } from '../hooks'
import { useI18n, useT } from '../i18n'
import { DestinationCard, SectionHeading, Skeleton, Spinner, TourCard } from '../components/ui'
import { IMAGES } from '../data'
import { ReviewCard } from '../components/Trust'

const TRUST = ['Local, licensed guides', 'Private & small-group journeys', 'Booking confirmed by our team']
const WHY = [
  [ShieldCheck, 'Trusted Local Partners', 'We work with licensed guides, drivers and family-run guesthouses we know personally in each city.'],
  [Route, 'Personalized Itineraries', 'Every journey is shaped around your pace, interests and the season — never a fixed bus schedule.'],
  [Car, 'Comfortable Airport Transfers', 'A driver waiting with your name, flight tracked, luggage handled, and a cold water in the car.'],
  [Palette, 'Authentic Cultural Experiences', 'Plov cooked in a family courtyard, a potter’s wheel in Rishton, an evening of maqom music.'],
  [Wallet, 'Transparent Pricing', 'Clear per-person prices with what is included listed up front. No surprise extras on the road.'],
  [Headset, 'Friendly Customer Support', 'An English-speaking coordinator reachable on WhatsApp from your first question to your last day.'],
]
const STEPS = [
  ['Explore', 'Browse destinations and experiences, or generate a suggested itinerary in a few clicks.'],
  ['Choose', 'Select the tours, hotels and transfers that suit your dates, pace and budget.'],
  ['Request', 'Send one booking request with your travel details — no payment needed at this stage.'],
  ['Confirm', 'Our team checks availability and replies with a written confirmation and final price.'],
  ['Travel', 'Meet your guide and driver, and enjoy Uzbekistan with everything arranged in advance.'],
]
const TESTIMONIALS = [
  ['We asked for three cities in nine days with time to sit in tea houses. What we got felt like travelling with a knowledgeable friend rather than a tour company.', 'Lena & Matthias', 'Germany', 'Silk Road Multi-City Tour'],
  ['The guide in Bukhara knew every courtyard and every family who has lived there for generations. The cooking class was the highlight of our whole trip.', 'Claire Dubois', 'France', 'Bukhara Old City Guided Tour'],
  ['Our driver met us at Samarkand airport at 3am with tea in the car. Everything after that was effortless, including the night in the yurt camp.', 'James Whitfield', 'United Kingdom', 'Nurata Mountains Cultural Journey'],
]

function Newsletter() {
  const t = useT()
  const [email, setEmail] = useState('')
  const [state, setState] = useState('idle')
  async function submit(e) {
    e.preventDefault()
    setState('saving')
    try { await api.post('/newsletter/', { email, source: 'homepage' }); setState('done') } catch { setState('error') }
  }
  return (
    <form onSubmit={submit} className="mt-8 flex max-w-md flex-col gap-3 sm:flex-row">
      <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder={t('Your email')} aria-label={t('Your email')} className="h-12 flex-1 rounded-full border border-ivory/25 bg-ivory/10 px-5 text-[14px] text-ivory outline-none placeholder:text-ivory/50 focus:border-turquoise" />
      <button disabled={state === 'saving'} className="btn-liquid inline-flex h-12 items-center justify-center gap-2 rounded-full bg-ivory px-6 text-[13px] font-medium text-navy">{state === 'saving' && <Spinner />}{t('Subscribe')}</button>
      {state === 'done' && <p className="text-[13px] text-turquoise sm:basis-full">{t('Thank you — you are on the list.')}</p>}
      {state === 'error' && <p className="text-[13px] text-red-300 sm:basis-full">{t('Something went wrong. Please try again.')}</p>}
    </form>
  )
}

export default function Home() {
  const { t, img } = useI18n()
  const dest = useFetch('/destinations/', { list: true })
  const tours = useFetch('/tours/', { list: true })
  const classes = useFetch('/tours/?tour_type=workshop', { list: true })
  const reviews = useFetch('/reviews/', { list: true })
  const words = t('Discover the Magic of Uzbekistan').split(' ')
  const last = words.length > 1 ? words.pop() : ''
  return (
    <>
      <section className="relative isolate overflow-hidden bg-navy" aria-labelledby="hero-heading">
        <img src={img(IMAGES.hero)} data-orig={IMAGES.hero} alt={t('Registan Square in Samarkand glowing at dusk')} className="absolute inset-0 h-full w-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-b from-navy/80 via-navy/45 to-navy/90" />
        <div className="girih absolute inset-0 opacity-[0.16]" />
        <div className="shell relative flex min-h-[calc(100svh-74px)] flex-col justify-end pb-10 pt-24 lg:pb-16">
          <div className="max-w-3xl animate-rise-in">
            <p className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.28em] text-background"><Star className="h-3 w-3 fill-gold text-gold" />{t('Samarkand · Bukhara · Khiva · Tashkent')}</p>
            <h1 id="hero-heading" className="display-xl mt-5 text-ivory">{words.join(' ')} {last && <span className="italic text-turquoise">{last}</span>}</h1>
            <p className="mt-6 max-w-xl text-[17px] leading-relaxed text-background sm:text-[18px]">{t('Unforgettable journeys, authentic experiences, and seamless travel — all in one place.')}</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/plan" className="btn-liquid inline-flex h-12 items-center rounded-full bg-ivory px-7 text-[13px] font-medium text-navy">{t('Plan My Trip')}</Link>
              <Link to="/tours" className="inline-flex h-12 items-center rounded-full border border-ivory/40 px-7 text-[13px] font-medium text-ivory hover:bg-ivory/10">{t('Browse tours')}</Link>
            </div>
          </div>
          <div className="mt-10 flex flex-wrap items-center justify-between gap-4 animate-rise-in" style={{ animationDelay: '280ms' }}>
            <ul className="flex flex-wrap items-center gap-x-6 gap-y-2 text-[12px] text-background">
              {TRUST.map((x) => <li key={x} className="flex items-center gap-2"><span className="h-1 w-1 rounded-full bg-gold" />{t(x)}</li>)}
            </ul>
            <a href="#destinations" className="group hidden items-center gap-2 font-mono text-[10px] uppercase tracking-[0.22em] text-ivory/70 hover:text-ivory sm:flex">{t('Explore')}<ArrowDown className="h-3.5 w-3.5 transition-transform duration-500 group-hover:translate-y-1" /></a>
          </div>
        </div>
      </section>

      <section id="destinations" className="shell py-20 lg:py-28">
        <SectionHeading align="between" eyebrow="Destinations" title="Seven regions, one Silk Road" description="From turquoise domes to walled desert towns — start with the places everyone dreams of."
          action={<Link to="/destinations" className="inline-flex items-center gap-2 text-[13px] font-medium text-turquoise-deep hover:text-navy">{t('All destinations')}<ArrowRight className="h-4 w-4" /></Link>} />
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {dest.loading ? <Skeleton count={3} /> : dest.data.filter((d) => d.featured).map((d, i) => <DestinationCard key={d.slug} destination={d} delay={i * 80} />)}
        </div>
      </section>

      <section className="bg-sand-soft/60 py-20 lg:py-28">
        <div className="shell">
          <SectionHeading align="between" eyebrow="Featured journeys" title="Tours & experiences" description="Sample itineraries built by our local team. Tick “Select” on any tours you like and request them together."
            action={<Link to="/tours" className="inline-flex items-center gap-2 text-[13px] font-medium text-turquoise-deep hover:text-navy">{t('All tours')}<ArrowRight className="h-4 w-4" /></Link>} />
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {tours.loading ? <Skeleton count={3} /> : tours.data.filter((x) => !x.parent_slug && Number(x.price_from_usd) > 0 && x.tour_type !== 'workshop').map((x, i) => <TourCard key={x.slug} tour={x} delay={(i % 3) * 80} />)}
          </div>
        </div>
      </section>

      {classes.data.length > 0 && (
        <section className="shell py-20 lg:py-28">
          <SectionHeading align="between" eyebrow="Hands-on experiences" title="Cook it, bake it, take it home" description="Join a local cook in Samarkand: shape non in a clay tandir, cook plov in a kazan and carry your own food home."
            action={<Link to="/tours" className="inline-flex items-center gap-2 text-[13px] font-medium text-turquoise-deep hover:text-navy">{t('All tours')}<ArrowRight className="h-4 w-4" /></Link>} />
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">{classes.data.slice(0, 3).map((x, i) => <TourCard key={x.slug} tour={x} delay={i * 80} />)}</div>
        </section>
      )}

      <section className="shell py-20 lg:py-28">
        <SectionHeading eyebrow="Why ALI TRAVEL" title="Hospitality, planned with care" align="center" />
        <div className="mt-12 grid gap-px overflow-hidden rounded-[4px] border border-navy/10 bg-navy/10 sm:grid-cols-2 lg:grid-cols-3">
          {WHY.map(([Icon, title, body], i) => (
            <Reveal key={title} delay={i * 60} className="bg-ivory"><div className="h-full p-7 transition-colors duration-500 hover:bg-sand-soft/60 lg:p-9">
              <Icon className="h-6 w-6 text-turquoise-deep" strokeWidth={1.5} /><h3 className="mt-5 font-heading text-[22px]">{t(title)}</h3><p className="mt-2 text-[14px] leading-relaxed text-ink">{t(body)}</p></div></Reveal>
          ))}
        </div>
      </section>

      <section className="bg-sand-soft/60 py-20 lg:py-28">
        <div className="shell">
          <SectionHeading eyebrow="How it works" title="From first idea to wheels down" />
          <ol className="relative mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-5 lg:gap-6">
            {STEPS.map(([title, body], i) => (
              <Reveal as="li" key={title} delay={i * 80}><span className="grid h-7 w-7 place-items-center rounded-full border border-gold/60 bg-ivory font-mono text-[11px]">{String(i + 1).padStart(2, '0')}</span>
                <h3 className="mt-5 font-heading text-[21px]">{t(title)}</h3><p className="mt-2 text-[13.5px] leading-relaxed text-ink">{t(body)}</p></Reveal>
            ))}
          </ol>
        </div>
      </section>

      <section className="shell py-20 lg:py-28">
        <p className="eyebrow">{t('Traveller stories')}</p><h2 className="display-lg mt-3">{t('Hospitality, remembered')}</h2>
        {reviews.data.length > 0 ? (
          <div className="mt-10 grid gap-6 lg:grid-cols-3">{reviews.data.slice(0, 3).map((r) => <ReviewCard key={r.id} review={r} />)}</div>
        ) : (<>
        <div className="mt-10 grid gap-6 lg:grid-cols-3">
            {TESTIMONIALS.map(([quote, name, country, trip], i) => (
              <Reveal key={name} delay={i * 80}><figure className="h-full rounded-[4px] border border-navy/10 bg-card p-7">
                <blockquote className="font-heading text-[21px] leading-snug">“{t(quote)}”</blockquote>
                <figcaption className="mt-5 text-[13px] text-ink"><span className="font-medium text-navy">{name}</span>, {t(country)}<br /><span className="font-mono text-[10px] uppercase tracking-[0.14em]">{t(trip)}</span></figcaption></figure></Reveal>
            ))}
          </div>
          <p className="mt-4 text-[12px] text-ink/70">{t('Demonstration testimonials.')}</p>
        </>)}
      </section>

      <section className="relative overflow-hidden bg-navy py-20 text-ivory lg:py-24">
        <div className="girih absolute inset-0 opacity-[0.16]" />
        <div className="shell relative"><h2 className="display-lg max-w-xl">{t('Letters from the Silk Road')}</h2>
          <p className="mt-4 max-w-md text-ivory/70">{t('Occasional notes on seasons, festivals and new routes. No spam.')}</p><Newsletter /></div>
      </section>
    </>
  )
}
