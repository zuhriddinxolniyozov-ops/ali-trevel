import { Link } from 'react-router-dom'
import { ArrowRight, CalendarDays, Check, MapPin } from 'lucide-react'
import { Reveal } from '../hooks'
import { useT } from '../i18n'
import { usesGroupPricing } from '../groupPricing'
import { EditButton } from '../edit/Add'
import { Photo, PriceTag } from './ui'

// The packages shown in the first row of the Destinations section, in this order, and the cities each one visits.
export const PACKAGES = {
  'samarkand-city-tour': ['Samarkand'],
  'silk-road-7-day-journey': ['Samarkand', 'Shahrisabz', 'Qarshi', 'Bukhara', 'Samarkand'],
  'silk-road-11-day-journey': ['Samarkand', 'Shahrisabz', 'Qarshi', 'Bukhara', 'Khiva', 'Bukhara', 'Samarkand'],
}

/** A multi-day package: photo, length, cities on the way, highlights and the price. */
export default function PackageCard({ tour, delay = 0 }) {
  const t = useT()
  const cities = PACKAGES[tour.slug] || [tour.destination_name]
  return (
    <Reveal delay={delay} className="h-full">
      <article data-edit-record={`tours:${tour.slug}`} className="card-hover group relative flex h-full flex-col overflow-hidden rounded-[4px] border border-navy/10 bg-card">
        <EditButton resource="tours" record={tour} />
        <Link to={`/tours/${tour.slug}`} className="relative block aspect-[16/10] overflow-hidden" aria-label={tour.title}>
          <Photo src={tour.image_url} alt={tour.title} className="h-full w-full object-cover transition-transform duration-[1.2s] ease-out group-hover:scale-[1.05]" />
          <div className="absolute inset-0 bg-gradient-to-t from-navy/60 via-transparent to-transparent" />
          <span className="absolute left-4 top-4 inline-flex items-center gap-1.5 rounded-full bg-gold px-3.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.16em] text-navy"><CalendarDays className="h-3.5 w-3.5" />{t(tour.duration_label)}</span>
        </Link>
        <div className="card-pad flex flex-1 flex-col p-5 lg:p-6">
          <h3 className="font-heading text-[24px] leading-tight text-navy"><Link to={`/tours/${tour.slug}`} className="hover:text-turquoise-deep">{tour.title}</Link></h3>
          <p className="hide-in-row mt-2 line-clamp-3 text-[14px] leading-relaxed text-ink">{tour.summary}</p>
          <ol className="hide-in-row mt-4 flex flex-wrap items-center gap-x-1.5 gap-y-1 text-[11.5px] text-navy" aria-label={t('Route')}>
            {cities.map((name, i) => (
              <li key={i} className="inline-flex items-center gap-1.5"><span className="inline-flex items-center gap-1 rounded-full bg-sand-soft px-2 py-0.5"><MapPin className="h-3 w-3 text-turquoise-deep" />{t(name)}</span>{i < cities.length - 1 && <ArrowRight className="h-3 w-3 text-ink/60" aria-hidden="true" />}</li>
            ))}
          </ol>
          <ul className="hide-in-row mt-4 space-y-1.5 text-[13px] leading-snug text-ink">
            {(tour.highlights || []).slice(0, 3).map((h) => <li key={h} className="flex gap-2"><Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-turquoise-deep" />{h}</li>)}
          </ul>
          <div className="mt-auto border-t border-navy/10 pt-4">
            <p className="font-mono text-[9px] uppercase tracking-[0.18em] text-ink">{t(usesGroupPricing(tour) ? 'From, group of 20+' : 'From')}</p>
            <p className="text-[20px] font-medium text-navy"><PriceTag amount={tour.price_from_usd} percent={tour.effective_discount} /><span className="ml-1 text-[0.78em] text-ink">/ {t('person')}</span></p>
            <Link to={`/tours/${tour.slug}`} className="hide-in-row mt-3 inline-flex items-center gap-1 text-[13px] font-medium text-turquoise-deep hover:text-navy">{t('View the full plan')}<ArrowRight className="h-3.5 w-3.5" /></Link>
          </div>
        </div>
      </article>
    </Reveal>
  )
}
