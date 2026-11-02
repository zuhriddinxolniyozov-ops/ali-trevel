import { Link } from 'react-router-dom'
import { Car, Clock, Coffee, Landmark, Printer, Quote, Star, Utensils } from 'lucide-react'
import { money } from '../hooks'
import { useI18n } from '../i18n'
import { Photo } from './ui'

/** "Registan Square | 16" -> { name, fee } */
export const parseStop = (line) => {
  const [name, fee] = String(line).split('|')
  return { name: name.trim(), fee: fee && fee.trim() !== '' ? Number(fee) : null }
}

const LOCALES = { en: 'en-GB', uz: 'uz-UZ', ru: 'ru-RU', fr: 'fr-FR', de: 'de-DE', es: 'es-ES' }
const MEALS = { breakfast: 'Breakfast', lunch: 'Lunch', dinner: 'Dinner' }

export function printSection(id) {
  const root = document.documentElement
  root.classList.add('print-section')
  document.getElementById(id)?.setAttribute('data-print', 'true')
  window.print()
  window.setTimeout(() => { root.classList.remove('print-section'); document.getElementById(id)?.removeAttribute('data-print') }, 300)
}

/** The plan as plain text, saved with the booking request so the team sees what the traveller was shown. */
export function planText(tour) {
  const stops = (tour.route || []).map(parseStop)
  const word = { breakfast: 'Breakfast', lunch: 'Lunch', dinner: 'Dinner' }
  return (tour.itinerary || []).map((day) => [`Day ${day.day}`, ...day.items.map((item) => {
    const place = stops[item.stop]?.name
    const label = item.type === 'meal' ? `${word[item.meal] || 'Meal'}${item.included === false ? ' (not included)' : ''}`
      : item.type === 'visit' ? `Visit: ${place}` : item.type === 'transfer' ? `Transfer to ${place}` : item.type === 'free' ? 'Free time' : item.text
    return `${item.time} ${label}`
  })].join('\n')).join('\n\n')
}

/**
 * Approximate day-by-day schedule of a tour (visits, meals, transfers), then a short note about every place visited
 * with a keepsake text. Place names come from the tour's own route, so they are translated with it.
 */
export default function DayPlan({ tour, places = [], startDate }) {
  const { t, lang } = useI18n()
  const days = tour.itinerary || []
  if (!days.length) return null
  const stops = (tour.route || []).map(parseStop)
  const placeByName = Object.fromEntries(places.map((p) => [parseStop(p.route?.[0] || '').name.toLowerCase(), p]))
  const placeOf = (index) => placeByName[stops[index]?.name.toLowerCase()]
  const dateOf = (n) => {
    if (!startDate) return ''
    const d = new Date(`${startDate}T12:00:00`)
    d.setDate(d.getDate() + n - 1)
    return d.toLocaleDateString(LOCALES[lang] || 'en-GB', { weekday: 'short', day: 'numeric', month: 'short' })
  }

  const visited = [...new Set(days.flatMap((d) => d.items).filter((i) => i.type === 'visit').map((i) => i.stop))].filter((i) => placeOf(i)?.description)

  function Row({ item }) {
    const stop = stops[item.stop]
    const place = placeOf(item.stop)
    let icon = Clock
    let title = ''
    let note = ''
    let chip = null
    if (item.type === 'meal') {
      icon = item.meal === 'breakfast' ? Coffee : Utensils
      title = t(MEALS[item.meal] || 'Meal')
      chip = item.included === false ? { text: t('Not included'), muted: true } : { text: t('Included') }
      if (item.included === false) note = t('Pay on the day')
    } else if (item.type === 'visit' && stop) {
      icon = Landmark
      title = stop.name
      note = place?.summary || ''
      if (stop.fee !== null) chip = { text: `${t('Entrance ticket')} ${money(stop.fee)}${tour.tickets_included ? '' : ` · ${t('paid at the site')}`}`, muted: true }
    } else if (item.type === 'transfer' && stop) {
      icon = Car
      title = t('Transfer to {place}', { place: stop.name })
    } else if (item.type === 'free') title = t('Free time')
    else { icon = Star; title = item.i18n?.[lang] || item.text || '' }
    const Icon = icon
    return (
      <li data-edit-record={item.type === 'visit' && place ? `tours:${place.slug}` : undefined} className="grid grid-cols-[64px_1fr] gap-3 py-3 sm:grid-cols-[76px_1fr]">
        <span className="pt-0.5 font-mono text-[14px] text-navy">{item.time}</span>
        <div className="flex gap-3">
          <span className="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-full bg-sand-soft text-turquoise-deep"><Icon className="h-4 w-4" /></span>
          <div className="min-w-0">
            <p className="text-[15px] font-medium text-navy">{place && item.type === 'visit' ? <Link to={`/tours/${place.slug}`} className="hover:text-turquoise-deep">{title}</Link> : title}</p>
            {note && <p className="mt-0.5 text-[13px] leading-snug text-ink">{note}</p>}
            {chip && <span className={`mt-1.5 inline-block rounded-full px-2.5 py-0.5 text-[11px] ${chip.muted ? 'bg-sand text-navy/70' : 'bg-turquoise/15 text-turquoise-deep'}`}>{chip.text}</span>}
          </div>
        </div>
      </li>
    )
  }

  return (
    <section id="day-plan" className="mt-10 scroll-mt-28">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h3 className="font-heading text-[26px]">{t('Sample day-by-day plan')}</h3>
        <button type="button" onClick={() => printSection('day-plan')} className="inline-flex items-center gap-1.5 rounded-full border border-navy/20 px-4 py-2 text-[12px] font-medium text-navy hover:bg-navy hover:text-ivory print:hidden"><Printer className="h-3.5 w-3.5" />{t('Print plan')}</button>
      </div>
      <p className="mt-1 text-[13px] text-ink">{t('Times are approximate; our team confirms the final schedule with you.')}</p>

      <div className="mt-4 grid gap-5">
        {days.map((day) => (
          <div key={day.day} className="rounded-sm border border-navy/10 bg-white p-4 sm:p-5">
            <h4 className="flex items-baseline justify-between gap-3 border-b border-navy/10 pb-2 font-heading text-[22px]">
              {t('Day {n}', { n: day.day })}<span className="font-body text-[13px] text-ink">{dateOf(day.day)}</span>
            </h4>
            <ol className="divide-y divide-navy/10">{day.items.map((item, i) => <Row key={`${day.day}-${i}`} item={item} />)}</ol>
          </div>
        ))}
      </div>

      {visited.length > 0 && (
        <div className="mt-10">
          <h3 className="font-heading text-[26px]">{t('About the places')}</h3>
          <div className="mt-4 space-y-5">
            {visited.map((index) => {
              const place = placeOf(index)
              return (
                <article key={index} data-edit-record={`tours:${place.slug}`} className="grid gap-5 rounded-sm border border-navy/10 bg-white p-4 sm:grid-cols-[200px_1fr] sm:p-5">
                  <Photo src={place.image_url} alt={stops[index].name} className="aspect-[4/3] w-full rounded-sm object-cover sm:aspect-auto sm:h-full sm:min-h-[150px]" />
                  <div>
                    <h4 className="font-heading text-[24px]"><Link to={`/tours/${place.slug}`} className="hover:text-turquoise-deep">{stops[index].name}</Link></h4>
                    <p className="mt-2 text-[14.5px] leading-relaxed text-ink">{place.description}</p>
                    {place.story && (
                      <blockquote className="mt-4 flex gap-3 border-l-2 border-gold pl-4">
                        <Quote className="mt-1 h-4 w-4 shrink-0 text-gold" aria-hidden="true" />
                        <p className="font-heading text-[19px] italic leading-snug text-navy">{place.story}</p>
                      </blockquote>
                    )}
                  </div>
                </article>
              )
            })}
          </div>
        </div>
      )}
    </section>
  )
}

/** The keepsake text of a single place, shown at the end of its page. */
export function StoryBlock({ story }) {
  const { t } = useI18n()
  if (!story) return null
  return (
    <figure className="mt-10 rounded-sm border border-gold/40 bg-sand-soft/60 p-6 sm:p-8">
      <Quote className="h-5 w-5 text-gold" aria-hidden="true" />
      <blockquote className="mt-3 font-heading text-[24px] italic leading-snug text-navy">{story}</blockquote>
      <figcaption className="mt-4 font-mono text-[10px] uppercase tracking-[0.2em] text-ink">{t('A few words to remember')}</figcaption>
    </figure>
  )
}
