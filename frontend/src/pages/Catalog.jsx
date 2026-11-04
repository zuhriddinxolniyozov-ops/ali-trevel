import { useEffect, useMemo, useState } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { Check, Clock, Heart, MapPin, Star, X } from 'lucide-react'
import { api } from '../api'
import { discounted, exactMoney, money, useAuth, useFetch } from '../hooks'
import { usesGroupPricing } from '../groupPricing'
import { useT } from '../i18n'
import { PACKAGES } from '../components/PackageCard'
import PlaceMap, { PinLink, located, routeUrl } from '../components/PlaceMap'
import BookingForm, { MobileBookBar } from '../components/BookingForm'
import Gallery from '../components/Gallery'
import DayPlan, { StoryBlock, parseStop, planText } from '../components/DayPlan'
import { DestinationCard, EmptyState, PageHero, Photo, PriceTag, Skeleton, TourCard } from '../components/ui'
import { IMAGES } from '../data'
import { AddCard, EditButton, EditRecordBar } from '../edit/Add'
import { useEdit } from '../edit/context'
import { TourFaq, TourReviews, TrustPanel } from '../components/Trust'
import Seo, { tourJsonLd } from '../components/Seo'

function NotFound({ what }) {
  const t = useT()
  return <div className="shell py-24"><EmptyState title={`${t(what)} — ${t('not found')}`} body="It may have been unpublished. Browse the full catalogue to find another journey." /></div>
}

/* ---------- save (heart) ---------- */
function SaveButton({ type, slug, title, image, meta }) {
  const t = useT()
  const nav = useNavigate()
  const { isAuthenticated } = useAuth()
  const { data, reload } = useFetch(isAuthenticated ? `/saved/?item_type=${type}&item_slug=${slug}` : null, { list: true })
  const saved = data[0]
  async function toggle() {
    if (!isAuthenticated) { nav('/login'); return }
    if (saved) await api.del(`/saved/${saved.id}/`)
    else await api.post('/saved/', { item_type: type, item_slug: slug, item_title: title, item_image: image || '', item_meta: meta || '' })
    reload()
  }
  return (
    <button onClick={toggle} className="inline-flex items-center gap-2 rounded-full border border-navy/20 px-4 py-2 text-[12px] font-medium text-navy hover:bg-navy/5">
      <Heart className={`h-4 w-4 ${saved ? 'fill-red-500 text-red-500' : ''}`} />{saved ? t('Saved') : t('Save')}
    </button>
  )
}

function List({ items, title, negative = false }) {
  const t = useT()
  if (!items?.length) return null
  return (
    <div className="mt-8"><h3 className="font-heading text-[26px]">{t(title)}</h3>
      <ul className="mt-3 space-y-2">{items.map((i) => <li key={i} className="flex items-start gap-2 text-[15px] text-ink">{negative ? <X className="mt-1 h-4 w-4 shrink-0 text-ink" /> : <Check className="mt-1 h-4 w-4 shrink-0 text-turquoise-deep" />}{i}</li>)}</ul></div>
  )
}

/* ---------- destinations ---------- */
export function Destinations() {
  const t = useT()
  const { data, loading } = useFetch('/destinations/', { list: true })
  return (
    <>
      <Seo title={t('Destinations')} description={t('From the Registan to the Aral Sea — pick a region and start exploring.')} />
      <PageHero eyebrow="Destinations" title="Where the Silk Road still feels alive" description="From the Registan to the Aral Sea — pick a region and start exploring." image={IMAGES.samarkand} />
      <div className="shell py-16 lg:py-24"><div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {loading ? <Skeleton /> : <>{data.map((d, i) => <DestinationCard key={d.slug} destination={d} delay={i * 60} />)}<AddCard resource="destinations" label="Add a destination" /></>}</div></div>
    </>
  )
}

export function DestinationDetail() {
  const t = useT()
  const { editing } = useEdit()
  const { slug } = useParams()
  const { data: d, loading, error } = useFetch(`/destinations/${slug}/`)
  const tours = useFetch(`/tours/?destination_slug=${slug}`, { list: true })
  const { hash } = useLocation()
  useEffect(() => { if (hash === '#tours' && !tours.loading) document.getElementById('tours')?.scrollIntoView({ block: 'start' }) }, [hash, tours.loading, slug])  // the map's green cities open here
  if (loading) return <div className="shell py-24"><Skeleton count={3} /></div>
  if (error || !d) return <NotFound what="Destination" />
  // Single historical places (they belong to a bigger tour) get their own section below the main tours.
  const mainTours = tours.data.filter((x) => !x.parent_slug)
  const places = tours.data.filter((x) => x.parent_slug)
  const here = { destination_slug: d.slug, destination_name: d.name }
  // Blank template for a single historical place: it starts attached to this destination's main tour.
  const placePreset = { ...here, parent_slug: (mainTours.find((x) => x.route?.length) || mainTours[0])?.slug || '', tour_type: 'walking', price_from_usd: 0, duration_label: 'Flexible hours' }
  return (
    <div data-edit-record={`destinations:${d.slug}`}>
      <PageHero eyebrow={d.region} title={d.name} description={d.summary} image={d.image_url} />
      <EditRecordBar resource="destinations" record={d} label="Edit destination" />
      <div className="shell py-16 lg:py-24">
        <p className="max-w-2xl text-[17px] leading-relaxed text-ink">{d.description}</p>
        <p className="mt-4 flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.1em] text-ink"><Clock className="h-4 w-4" />{t('Suggested')}: {t(d.suggested_duration)}</p>
        {(mainTours.length > 0 || editing) && <>
          <h2 id="tours" className="display-lg mt-14 scroll-mt-28">{t('Tours in {name}', { name: d.name })}</h2>
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">{mainTours.map((x, i) => <TourCard key={x.slug} tour={x} delay={i * 60} />)}<AddCard resource="tours" preset={here} label="Add a tour" /></div>
        </>}
        {(places.length > 0 || editing) && <>
          <h2 className="display-lg mt-16">{t('Historical places in {name}', { name: d.name })}</h2>
          <p className="mt-3 max-w-2xl text-[16px] leading-relaxed text-ink">{t('Visit a single place with a guide, or combine them all in the city tour.')}</p>
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">{places.map((x, i) => <TourCard key={x.slug} tour={x} delay={i * 50} />)}<AddCard resource="tours" preset={placePreset} label="Add a historical place" /></div>
        </>}
        {!tours.loading && !tours.data.length && <div className="mt-8"><EmptyState title="No tours listed yet" body="Ask us for a custom journey." /><Link to="/plan" className="btn-primary mt-4">{t('Plan My Trip')}</Link></div>}
      </div>
    </div>
  )
}

/* ---------- tours ---------- */
export function Tours() {
  const t = useT()
  const { data, loading } = useFetch('/tours/', { list: true })
  const [cat, setCat] = useState('All')
  const cats = useMemo(() => ['All', ...new Set(data.map((x) => x.category))], [data])
  const rank = (x) => { const i = Object.keys(PACKAGES).indexOf(x.slug); return i < 0 ? 99 : i }  // the three packages come first, then the rest as before
  const shown = (cat === 'All' ? data : data.filter((x) => x.category === cat)).map((x, i) => [x, i]).sort((a, b) => rank(a[0]) - rank(b[0]) || a[1] - b[1]).map(([x]) => x)
  return (
    <>
      <Seo title={t('Tours & Experiences')} description={t('Private and small-group tours led by local, licensed guides.')} />
      <PageHero eyebrow="Tours & Experiences" title="Journeys shaped around you" description="Private and small-group tours led by local, licensed guides." image={IMAGES.bukhara} />
      <div className="shell py-16 lg:py-24">
        <div className="mb-8 flex flex-wrap gap-2">{cats.map((c) => (
          <button key={c} onClick={() => setCat(c)} className={`rounded-full border px-4 py-1.5 text-[12px] ${cat === c ? 'border-navy bg-navy text-ivory' : 'border-navy/15 text-navy/70 hover:border-navy'}`}>{t(c)}</button>))}</div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">{loading ? <Skeleton /> : <>{shown.map((x, i) => <TourCard key={x.slug} tour={x} delay={i * 60} />)}<AddCard resource="tours" label="Add a tour" /></>}</div>
        {!loading && !shown.length && <EmptyState title="No tours match" />}
      </div>
    </>
  )
}

const TOUR_TYPES = { workshop: 'Hands-on experience', car: 'Car tour', walking: 'Walking tour', mixed: 'Car + walking', train: 'Train tour' }

function Fact({ label, children }) {
  return (
    <div className="border-b border-navy/10 py-3 sm:grid sm:grid-cols-[170px_1fr] sm:gap-4">
      <dt className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink">{label}</dt>
      <dd className="mt-1 text-[15px] text-navy sm:mt-0">{children}</dd>
    </div>
  )
}

function Yes({ yes }) {
  const t = useT()
  return yes
    ? <span className="inline-flex items-center gap-1.5 text-turquoise-deep"><Check className="h-4 w-4" />{t('Included')}</span>
    : <span className="inline-flex items-center gap-1.5 text-ink"><X className="h-4 w-4" />{t('Not included')}</span>
}

export function TourDetail() {
  const t = useT()
  const { slug } = useParams()
  const [booked, setBooked] = useState(null) // set once a request is sent, so the plan can show real dates
  useEffect(() => { if (booked) document.getElementById('booked-plan')?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }, [booked])
  const { data: tour, loading, error } = useFetch(`/tours/${slug}/`)
  const parent = useFetch(tour?.parent_slug ? `/tours/${tour.parent_slug}/` : null)
  const places = useFetch(tour && !tour.parent_slug ? '/tours/?has_parent=1' : null, { list: true })
  const hotels = useFetch(tour?.destination_slug ? `/hotels/?destination_slug=${tour.destination_slug}` : null, { list: true })
  if (loading) return <div className="shell py-24"><Skeleton count={3} /></div>
  if (error || !tour) return <NotFound what="Tour" />

  const stops = (tour.route || []).map(parseStop)
  const placeByName = Object.fromEntries(places.data.map((p) => [parseStop(p.route?.[0] || '').name.toLowerCase(), p]))
  const priceless = Number(tour.price_from_usd) <= 0
  return (
    <div data-edit-record={`tours:${tour.slug}`}>
      <Seo title={tour.title} description={tour.summary} image={tour.image_url} jsonLd={priceless ? null : tourJsonLd(tour)} />
      <PageHero eyebrow={`${t(tour.category)} · ${tour.destination_name}`} title={tour.title} description={tour.summary} image={tour.image_url} />
      <EditRecordBar resource="tours" record={tour} label="Edit tour" />
      <div className="shell grid gap-12 py-16 lg:grid-cols-[1.5fr_1fr] lg:py-24">
        <div>
          <div className="flex flex-wrap items-center gap-4 text-[13px] text-ink">
            <span className="inline-flex items-center gap-1"><Clock className="h-4 w-4" />{t(tour.duration_label)}</span>
            <span className="inline-flex items-center gap-1"><MapPin className="h-4 w-4 text-turquoise-deep" />{tour.destination_name}</span>
            {tour.review_count > 0 && <span className="inline-flex items-center gap-1"><Star className="h-4 w-4 fill-gold text-gold" />{Number(tour.rating).toFixed(1)} ({tour.review_count} {t('demo reviews')})</span>}
            <SaveButton type="tour" slug={tour.slug} title={tour.title} image={tour.image_url} meta={tour.duration_label} />
          </div>
          <p className="mt-8 text-[17px] leading-relaxed text-ink">{tour.description}</p>

          <h3 className="mt-10 font-heading text-[26px]">{t('Tour details')}</h3>
          <dl className="mt-3 border-t border-navy/10">
            {tour.tour_type && <Fact label={t('Tour type')}>{t(TOUR_TYPES[tour.tour_type] || tour.tour_type)}</Fact>}
            <Fact label={t('Duration')}>{t(tour.duration_label)}</Fact>
            <Fact label={t('Group type')}>{t(tour.group_type)}{tour.max_travelers ? ` · ${t('Up to {n} travelers', { n: tour.max_travelers })}` : ''}</Fact>
            {tour.languages?.length > 0 && <Fact label={t('Tour languages')}>{tour.languages.map((l) => t(l)).join(', ')}</Fact>}
            <Fact label={t('Transport')}><Yes yes={tour.transport_included} /></Fact>
            <Fact label={t('Entrance tickets')}><Yes yes={tour.tickets_included} /></Fact>
            <Fact label={t('Pickup')}><Yes yes={tour.pickup_included} /></Fact>
            {tour.guide && <Fact label={t('Guide')}>{t(tour.guide)}</Fact>}
            {tour.meeting_point && <Fact label={t('Meeting point')}>{t(tour.meeting_point)}</Fact>}
          </dl>

          {tour.parent_slug && <PlaceMap place={tour} />}

          {stops.length > 0 && <>
            <h3 className="mt-10 font-heading text-[26px]">{t('Route and entrance tickets')}</h3>
            <ol className="mt-3 divide-y divide-navy/10 rounded-sm border border-navy/10 bg-white">
              {stops.map((s, i) => {
                const place = placeByName[s.name.toLowerCase()]
                return (
                  <li key={`${s.name}-${i}`} className="flex items-center gap-4 px-4 py-3">
                    <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-navy font-mono text-[11px] text-ivory">{i + 1}</span>
                    <span className="flex-1 text-[15px]">{place ? <Link to={`/tours/${place.slug}`} className="hover:text-turquoise-deep">{s.name}</Link> : s.name}</span>
                    {place && <PinLink place={place} className="shrink-0" />}
                    {s.fee !== null && <span className="font-mono text-[14px] text-navy">{money(s.fee)}</span>}
                  </li>
                )
              })}
            </ol>
            {!tour.tickets_included && <p className="mt-2 text-[12.5px] text-ink">{t('Entrance tickets are not included in the tour price and are paid at each site.')}</p>}
            {(() => { const pins = stops.map((s) => placeByName[s.name.toLowerCase()]).filter(located); return pins.length > 1 && <a href={routeUrl(pins)} target="_blank" rel="noopener noreferrer" className="mt-3 inline-flex items-center gap-1.5 text-[13px] font-medium text-turquoise-deep hover:text-navy"><MapPin className="h-4 w-4" />{t('Open the whole route on Google Maps')}</a> })()}
          </>}

          {booked && tour.itinerary?.length > 0 && (
            <div id="booked-plan" className="mt-10 scroll-mt-28 rounded-sm border border-turquoise-deep/30 bg-sand-soft/70 p-5">
              <p className="font-medium text-navy">{t('Request received')} · <span className="font-mono text-[13px]">{booked.reference}</span></p>
              <p className="mt-1 text-[14px] leading-relaxed text-ink">{t('Here is your approximate plan. Our team will confirm the final schedule by email.')}</p>
            </div>
          )}
          <DayPlan tour={tour} places={places.data} startDate={booked?.date} />
          <List title="Highlights" items={tour.highlights} /><List title="Included" items={tour.included} /><List title="Not included" items={tour.excluded} negative />
          <StoryBlock story={tour.story} />
          {!priceless && <><TourFaq /><TourReviews tour={tour} /></>}
        </div>

        <aside className="space-y-5 lg:sticky lg:top-28 lg:self-start lg:max-h-[calc(100vh-8rem)] lg:overflow-y-auto lg:pr-1 side-scroll">
          {priceless && tour.entrance_fee_usd ? (
            <div><p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink">{t('Entrance ticket')}</p>
              <p className="text-[28px] font-medium"><span className="font-mono">{money(tour.entrance_fee_usd)}</span><span className="ml-1 text-[14px] text-ink">/ {t('person')}</span></p></div>
          ) : (
            <div><p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink">{t(usesGroupPricing(tour) ? 'From, group of 20+' : 'From')}</p>
              <p className="text-[28px] font-medium"><PriceTag amount={tour.price_from_usd} percent={tour.effective_discount} /><span className="ml-1 text-[14px] text-ink">/ {t('person')}</span></p>
              {usesGroupPricing(tour) && <p className="mt-1 text-[12.5px] text-ink">{t('Price for a group of 20 or more. Smaller groups pay a little more per person; you see the exact price for your group when you book.')}</p>}
              {tour.effective_discount > 0 && tour.promo_title && <p className="mt-1 text-[12.5px] text-destructive">{tour.promo_title}</p>}</div>
          )}
          {parent.data && (
            <div className="rounded-sm border border-gold/40 bg-sand-soft/60 p-4">
              <p className="text-[13px] text-ink">{t('This place is part of')}</p>
              <Link to={`/tours/${parent.data.slug}`} className="mt-1 block font-heading text-[22px] hover:text-turquoise-deep">{parent.data.title}</Link>
              <p className="mt-1 text-[13px] text-ink">{t('From')} <span className="font-mono text-navy">{money(parent.data.price_from_usd)}</span> / {t('person')}</p>
              <Link to={`/tours/${parent.data.slug}`} className="btn-outline mt-3 !h-9 !px-4 text-[12px]">{t('View the full city tour')}</Link>
            </div>
          )}
          <BookingForm serviceType="tour" serviceSlug={tour.slug} serviceTitle={tour.title} estimatedTotal={priceless ? 0 : discounted(tour.price_from_usd, tour.effective_discount)}
            groupPriced={usesGroupPricing(tour)} stayIncluded={(tour.itinerary?.length || 0) >= 2} hotels={priceless ? [] : hotels.data} defaultNights={Math.max(1, tour.itinerary?.length || 1)}
            extra={tour.itinerary?.length ? { details_summary: planText(tour) } : {}} onSubmitted={setBooked} />
          {!booked && <MobileBookBar price={priceless ? null : money(discounted(tour.price_from_usd, tour.effective_discount))} unit="person" />}
          {!priceless && <TrustPanel tour={tour} />}
        </aside>
      </div>
    </div>
  )
}

/* ---------- hotels ---------- */
const HOTEL_FILTERS = [['all', 'All'], ['stars4', '4–5 star hotels'], ['hotel', '3-star hotels'], ['small', 'Boutique & guesthouses'], ['hostel', 'Hostels']]
const TYPE_LABEL = { hotel: 'Hotel', boutique: 'Boutique hotel', guesthouse: 'Guesthouse', hostel: 'Hostel' }
const matchesKind = (h, key) => key === 'all' || (key === 'stars4' ? h.stars >= 4 : key === 'hotel' ? h.property_type === 'hotel' && h.stars < 4 : key === 'small' ? ['boutique', 'guesthouse'].includes(h.property_type) : h.property_type === 'hostel')
const nightUnit = (h) => (h.price_basis === 'bed' ? 'bed per night' : 'night')
const hotelPhotos = (h) => [h.image_url, ...(h.gallery || [])].filter(Boolean)
const stars = (h) => (h.stars > 0 ? '★'.repeat(h.stars) : '')

export function Hotels() {
  const t = useT()
  const { data, loading } = useFetch('/hotels/', { list: true })
  const [kind, setKind] = useState('all')
  const [where, setWhere] = useState('all')
  const places = useMemo(() => [...new Map(data.map((h) => [h.destination_slug, h.destination_name])).entries()], [data])
  const shown = data.filter((h) => matchesKind(h, kind) && (where === 'all' || h.destination_slug === where))
  const chip = (on) => `rounded-full border px-4 py-1.5 text-[12px] ${on ? 'border-navy bg-navy text-ivory' : 'border-navy/15 text-navy/70 hover:border-navy'}`
  return (
    <>
      <Seo title={t('Hotels')} description={t('From 4–5 star hotels to guesthouses and hostels: real places to stay across Uzbekistan, with indicative prices.')} />
      <PageHero eyebrow="Hotels" title="Places to stay, chosen by locals" description="From 4–5 star hotels to guesthouses and hostels: real places to stay across Uzbekistan, with indicative prices." image={IMAGES.hotel} />
      <div className="shell py-16 lg:py-24">
        <div className="mb-3 flex flex-wrap gap-2">{HOTEL_FILTERS.map(([k, l]) => <button key={k} onClick={() => setKind(k)} className={chip(kind === k)}>{t(l)}</button>)}</div>
        <div className="mb-8 flex flex-wrap gap-2">
          <button onClick={() => setWhere('all')} className={chip(where === 'all')}>{t('All destinations')}</button>
          {places.map(([slug, name]) => <button key={slug} onClick={() => setWhere(slug)} className={chip(where === slug)}>{name}</button>)}
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {loading ? <Skeleton /> : <>{shown.map((h) => (
            <article key={h.slug} data-edit-record={`hotels:${h.slug}`} className="card-hover relative overflow-hidden rounded-[4px] border border-navy/10 bg-card">
              <EditButton resource="hotels" record={h} />
              <div className="relative">
                <Gallery images={hotelPhotos(h)} alt={h.name} to={`/hotels/${h.slug}`} className="aspect-[4/3]" />
                <span className="pointer-events-none absolute left-3 top-3 z-10 rounded-full bg-ivory/90 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.14em] text-navy">{t(TYPE_LABEL[h.property_type] || 'Hotel')}</span>
              </div>
              <div className="p-5"><p className="text-[12px] text-ink">{h.destination_name}{stars(h) && ` · ${stars(h)}`}</p>
                <h3 className="mt-1 font-heading text-[23px]"><Link to={`/hotels/${h.slug}`}>{h.name}</Link></h3>
                <p className="mt-2 line-clamp-3 text-[14px] text-ink">{h.summary}</p>
                <p className="mt-4 border-t border-navy/10 pt-4 text-[13px] text-ink">{t('From')} <PriceTag amount={h.price_from_usd} percent={h.effective_discount} className="text-[18px] text-navy" /> / {t(nightUnit(h))}</p></div>
            </article>))}
            <AddCard resource="hotels" label="Add a hotel" /></>}
        </div>
        {!loading && !shown.length && <EmptyState title="No hotels match these filters." />}
        <p className="mt-10 max-w-3xl text-[12.5px] leading-relaxed text-ink/80">{t('Prices are indicative “from” rates based on public booking listings. Our team confirms the exact rate and availability for your dates.')}</p>
      </div>
    </>
  )
}

export function HotelDetail() {
  const t = useT()
  const { slug } = useParams()
  const { data: h, loading, error } = useFetch(`/hotels/${slug}/`)
  if (loading) return <div className="shell py-24"><Skeleton count={3} /></div>
  if (error || !h) return <NotFound what="Hotel" />
  return (
    <div data-edit-record={`hotels:${h.slug}`}>
      <Seo title={h.name} description={h.summary} image={h.image_url} />
      <PageHero eyebrow={`${h.destination_name}${stars(h) ? ` · ${stars(h)}` : ` · ${t(TYPE_LABEL[h.property_type] || 'Hotel')}`}`} title={h.name} description={h.summary} image={h.image_url} />
      <EditRecordBar resource="hotels" record={h} label="Edit hotel" />
      <div className="shell grid gap-12 py-16 lg:grid-cols-[1.5fr_1fr] lg:py-24">
        <div className="min-w-0">
          <Gallery images={hotelPhotos(h)} alt={h.name} className="aspect-[16/10]" rounded="rounded-sm" thumbs arrows="always" />
          {h.photos_illustrative && <p className="mt-2 text-[12.5px] text-ink/80">{t('These are photos of similar places to stay in Uzbekistan, not of this property itself. The property’s own photos are added by our team.')}</p>}
          <div className="mt-8 flex flex-wrap items-center gap-3"><SaveButton type="hotel" slug={h.slug} title={h.name} image={h.image_url} meta={h.destination_name} />
            <span className="rounded-full bg-sand-soft px-3 py-1 font-mono text-[10px] uppercase tracking-[0.14em] text-navy">{t(TYPE_LABEL[h.property_type] || 'Hotel')}</span></div>
          <p className="mt-6 text-[17px] leading-relaxed text-ink">{h.description}</p><List title="Amenities" items={h.amenities} /></div>
        <aside className="lg:sticky lg:top-28 lg:self-start lg:max-h-[calc(100vh-8rem)] lg:overflow-y-auto lg:pr-1 side-scroll">
          <p className="text-[28px] font-medium"><PriceTag amount={h.price_from_usd} percent={h.effective_discount} /><span className="ml-1 text-[14px] text-ink">/ {t(nightUnit(h))}</span></p>
          <p className="mb-4 mt-1 text-[12.5px] leading-snug text-ink/80">{t('Indicative “from” price based on public booking listings. Our team confirms the exact rate and availability for your dates.')}</p>
          <BookingForm serviceType="hotel" serviceSlug={h.slug} serviceTitle={h.name} estimatedTotal={discounted(h.price_from_usd, h.effective_discount)} perGuest={false} mode="hotel" unit={h.price_basis} intro="Tell us your dates and rooms. No payment is taken; our team confirms the stay." />
          <MobileBookBar price={money(discounted(h.price_from_usd, h.effective_discount))} unit={nightUnit(h)} /></aside>
      </div>
    </div>
  )
}

/* ---------- food ---------- */
export function Food() {
  const { data, loading } = useFetch('/food/', { list: true })
  return (
    <>
      <PageHero eyebrow="Local Food" title="Eat where the city eats" description="Dishes, bazaars and cooking classes with the people who make them." image={IMAGES.plov} />
      <div className="shell py-16 lg:py-24"><div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {loading ? <Skeleton /> : <>{data.map((f) => (
          <article key={f.slug} data-edit-record={`food:${f.slug}`} className="card-hover relative overflow-hidden rounded-[4px] border border-navy/10 bg-card">
            <EditButton resource="food" record={f} />
            <Photo src={f.image_url} alt={f.name} className="aspect-[4/3] w-full object-cover" />
            <div className="p-5"><p className="font-mono text-[10px] uppercase tracking-[0.14em] text-turquoise-deep">{f.kind}{f.destination_name && ` · ${f.destination_name}`}</p>
              <h3 className="mt-1 font-heading text-[23px]">{f.name}</h3><p className="mt-2 text-[14px] text-ink">{f.summary}</p></div>
          </article>))}<AddCard resource="food" label="Add an experience" /></>}</div></div>
    </>
  )
}

/* ---------- transport ---------- */
export function Transport() {
  const t = useT()
  const { data, loading } = useFetch('/transport/', { list: true })
  const [pick, setPick] = useState(null)
  const [pax, setPax] = useState(2)
  const opt = data.find((o) => o.slug === pick) || data[0]
  const gross = opt ? Number(opt.base_price_usd) + Math.max(0, pax - opt.included_passengers) * Number(opt.extra_passenger_usd) : 0
  const total = discounted(gross, opt?.effective_discount)
  return (
    <>
      <PageHero eyebrow="Transport" title="Airport transfers & drivers" description="Prices below are sample starting rates per vehicle. Extra passengers beyond the included allowance are priced separately." image={IMAGES.transfer} />
      <div className="shell grid gap-12 py-16 lg:grid-cols-[1.4fr_1fr] lg:py-24">
        <div className="space-y-4">{loading ? <Skeleton count={2} /> : <>{data.map((o) => (
          <button key={o.slug} data-edit-record={`transport:${o.slug}`} onClick={() => setPick(o.slug)} className={`flex w-full gap-4 rounded-[4px] border p-4 text-left ${opt?.slug === o.slug ? 'border-navy bg-sand-soft/50' : 'border-navy/10 bg-card'}`}>
            {o.image_url && <img src={o.image_url} alt="" className="h-24 w-32 rounded object-cover" />}
            <div><h3 className="font-heading text-[22px]">{o.name}</h3><p className="text-[13px] text-ink">{o.vehicle} · {t('up to')} {o.capacity} {t('passengers')}</p>
              <p className="mt-1 text-[14px] text-ink">{o.summary}</p><p className="mt-2 text-navy">{t('from')} <PriceTag amount={o.base_price_usd} percent={o.effective_discount} /></p></div></button>))}<AddCard resource="transport" label="Add a transport option" /></>}</div>
        {opt && <aside className="space-y-4 lg:sticky lg:top-28 lg:self-start lg:max-h-[calc(100vh-8rem)] lg:overflow-y-auto lg:pr-1 side-scroll">
          <label className="label">{t('Passengers')}<input type="number" min="1" max={opt.capacity} className="input" value={pax} onChange={(e) => setPax(Number(e.target.value) || 1)} /></label>
          <p className="text-[13px] text-ink">{t('Estimate')}: <PriceTag amount={gross} percent={opt.effective_discount} className="text-[20px] text-navy" /> — {t('sample rate, final price confirmed by our team.')}</p>
          <BookingForm serviceType="transport" serviceSlug={opt.slug} serviceTitle={opt.name} estimatedTotal={total} perGuest={false} /></aside>}
      </div>
    </>
  )
}
