import { ExternalLink, MapPin, Navigation } from 'lucide-react'
import { useT } from '../i18n'

/** A place (a single-place tour) has an exact location when both coordinates are set. */
export const located = (p) => p && p.latitude != null && p.longitude != null && p.latitude !== '' && p.longitude !== ''
const pair = (p) => `${Number(p.latitude).toFixed(6)},${Number(p.longitude).toFixed(6)}`
export const mapUrl = (p) => `https://www.google.com/maps/search/?api=1&query=${pair(p)}`
export const directionsUrl = (p) => `https://www.google.com/maps/dir/?api=1&destination=${pair(p)}`
/** Google Maps route through several places, in the order of the tour (the first is the start, the last the destination). */
export const routeUrl = (places) => (places.length > 1
  ? `https://www.google.com/maps/dir/?api=1&origin=${pair(places[0])}&destination=${pair(places[places.length - 1])}${places.length > 2 ? `&waypoints=${places.slice(1, -1).slice(0, 8).map(pair).join('%7C')}` : ''}`
  : mapUrl(places[0]))

/** A small "pin" link next to a place name. */
export function PinLink({ place, className = '' }) {
  const t = useT()
  if (!located(place)) return null
  return (
    <a href={mapUrl(place)} target="_blank" rel="noopener noreferrer" className={`inline-flex items-center gap-1 text-[12px] text-turquoise-deep hover:text-navy ${className}`}>
      <MapPin className="h-3.5 w-3.5" />{t('Show on map')}
    </a>
  )
}

/** The exact location of a place: an OpenStreetMap map with a marker, and links to open it in Google Maps or get directions. */
export default function PlaceMap({ place }) {
  const t = useT()
  if (!located(place)) return null
  const lat = Number(place.latitude)
  const lon = Number(place.longitude)
  const d = 0.004
  const src = `https://www.openstreetmap.org/export/embed.html?bbox=${lon - d},${lat - d / 1.6},${lon + d},${lat + d / 1.6}&layer=mapnik&marker=${lat},${lon}`
  return (
    <section aria-label={t('Location')} className="mt-10">
      <h3 className="font-heading text-[26px]">{t('Location')}</h3>
      <div className="mt-3 overflow-hidden rounded-sm border border-navy/10 bg-white">
        <iframe title={t('Map of the place')} src={src} loading="lazy" className="block h-[300px] w-full border-0" referrerPolicy="no-referrer" />
        <div className="flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-navy/10 px-4 py-3 text-[13px]">
          <span className="inline-flex items-center gap-1.5 text-ink"><MapPin className="h-4 w-4 text-turquoise-deep" /><span className="font-mono text-[12px]">{lat.toFixed(5)}, {lon.toFixed(5)}</span></span>
          <a href={mapUrl(place)} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 font-medium text-turquoise-deep hover:text-navy"><ExternalLink className="h-3.5 w-3.5" />{t('Open in Google Maps')}</a>
          <a href={directionsUrl(place)} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 font-medium text-turquoise-deep hover:text-navy"><Navigation className="h-3.5 w-3.5" />{t('Get directions')}</a>
        </div>
        {place.location_note && <p className="border-t border-navy/10 bg-sand-soft/60 px-4 py-2 text-[12.5px] text-ink">{place.location_note}</p>}
      </div>
    </section>
  )
}
