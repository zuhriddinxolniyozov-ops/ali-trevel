import { useEffect } from 'react'
import { isLocal } from '../market'

const DEFAULT_TITLE = 'ALI TRAVEL — Discover Uzbekistan. Experience the Extraordinary.'
const DEFAULT_DESCRIPTION = 'ALI TRAVEL designs private tours, cultural experiences, hotels and airport transfers across Samarkand, Bukhara, Khiva and Tashkent.'

function setMeta(attr, key, value) {
  let el = document.head.querySelector(`meta[${attr}="${key}"]`)
  if (!value) { el?.remove(); return }
  if (!el) { el = document.createElement('meta'); el.setAttribute(attr, key); document.head.appendChild(el) }
  el.setAttribute('content', value)
}

const absolute = (url) => (url && url.startsWith('/') ? `${window.location.origin}${url}` : url)

/**
 * Sets the page title, description, social-sharing tags and (optionally) structured data for the current page, and puts the
 * defaults back when the visitor leaves. Search engines and link previews read these.
 */
export default function Seo({ title, description, image, jsonLd, noindex = false }) {
  const data = jsonLd ? JSON.stringify(jsonLd) : ''
  useEffect(() => {
    const fullTitle = title ? `${title} — ALI TRAVEL` : DEFAULT_TITLE
    const text = (description || DEFAULT_DESCRIPTION).replace(/\s+/g, ' ').trim().slice(0, 300)
    document.title = fullTitle
    setMeta('name', 'description', text)
    setMeta('property', 'og:title', fullTitle)
    setMeta('property', 'og:description', text)
    setMeta('property', 'og:type', 'website')
    setMeta('property', 'og:url', window.location.href.split('#')[0])
    setMeta('property', 'og:image', absolute(image))
    setMeta('name', 'twitter:card', image ? 'summary_large_image' : 'summary')
    setMeta('name', 'robots', noindex ? 'noindex' : '')   // e.g. the "page not found" page
    let canonical = document.head.querySelector('link[rel="canonical"]')
    if (!canonical) { canonical = document.createElement('link'); canonical.rel = 'canonical'; document.head.appendChild(canonical) }
    canonical.href = window.location.origin + window.location.pathname
    let script = document.getElementById('seo-jsonld')
    if (data) {
      if (!script) { script = document.createElement('script'); script.id = 'seo-jsonld'; script.type = 'application/ld+json'; document.head.appendChild(script) }
      script.textContent = data
    } else script?.remove()
    return () => {
      document.title = DEFAULT_TITLE
      setMeta('name', 'description', DEFAULT_DESCRIPTION)
      document.getElementById('seo-jsonld')?.remove()
      setMeta('name', 'robots', '')
    }
  }, [title, description, image, data, noindex])
  return null
}

/** Structured data for a priced tour, so search engines can show it with its price. */
export function tourJsonLd(tour) {
  const price = Number(tour.price_from_usd)
  return {
    '@context': 'https://schema.org', '@type': 'TouristTrip', name: tour.title, description: tour.summary, image: absolute(tour.image_url),
    touristType: tour.group_type, provider: { '@type': 'TravelAgency', name: 'ALI TRAVEL' },
    ...(price > 0 ? { offers: { '@type': 'Offer', price: String(price), priceCurrency: isLocal ? 'UZS' : 'USD', availability: 'https://schema.org/InStock', url: window.location.href.split('#')[0] } } : {}),
  }
}
