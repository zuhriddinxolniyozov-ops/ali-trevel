import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, CalendarX2, Clock, MapPin, Star, Users, Loader2, CheckCircle2, CarFront, ChefHat } from 'lucide-react'
import { Reveal, discounted, exactMoney, money } from '../hooks'
import { useI18n, useT } from '../i18n'
import { EditButton } from '../edit/Add'
import { SelectToggle } from './Selection'
import { biggestGroup, useGroupTiers, usesGroupPricing } from '../groupPricing'
import Gallery from './Gallery'
import CardHeart from './CardHeart'
import { BonusLine } from './Bonuses'

/** A price; with a discount the old price is crossed out, the new one follows, plus a "-20%" badge. */
export function PriceTag({ amount, percent = 0, className = '', badge = true }) {
  const t = useT()
  const pct = Number(percent) || 0
  if (!pct) return <span className={`font-mono tabular-nums ${className}`}>{exactMoney(amount)}</span>
  return (
    <span className="inline-flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
      <del className="font-mono text-[0.72em] tabular-nums text-ink/70 decoration-destructive decoration-2"><span className="sr-only">{t('Was')} </span>{exactMoney(amount)}</del>
      <span className={`font-mono tabular-nums text-destructive ${className}`}><span className="sr-only">{t('Now')} </span>{exactMoney(discounted(amount, pct))}</span>
      {badge && <span className="rounded-full bg-destructive px-2 py-0.5 font-mono text-[10px] leading-4 text-white">−{pct}%</span>}
    </span>
  )
}

/** A photo, or a soft placeholder when the record has none yet. */
// Wikimedia Commons serves any photo at a few standard widths: a phone downloads a smaller copy than a big screen.
const COMMONS_WIDTHS = [500, 960, 1280]
function commonsSrcSet(src) {
  if (!/commons\.wikimedia\.org\/wiki\/Special:FilePath\/.+[?&]width=\d+/.test(src || '')) return undefined
  return COMMONS_WIDTHS.map((w) => `${src.replace(/([?&]width=)\d+/, `$1${w}`)} ${w}w`).join(', ')
}

export function Photo({ src, alt = '', className = '', sizes = '(max-width: 639px) 85vw, (max-width: 1023px) 50vw, 34vw', ...rest }) {
  const [failed, setFailed] = useState(false)
  useEffect(() => { setFailed(false) }, [src])
  const srcSet = commonsSrcSet(src)
  return src && !failed
    ? <img src={src} srcSet={srcSet} sizes={srcSet ? sizes : undefined} alt={alt} loading="lazy" decoding="async" className={className} onError={() => setFailed(true)} {...rest} />
    : <div aria-hidden="true" className={`bg-gradient-to-br from-sand to-sand-soft ${className}`} />
}

export function SectionHeading({ eyebrow, title, description, action, align = 'left', light = false }) {
  const t = useT()
  return (
    <div className={`flex flex-col gap-6 ${align === 'between' ? 'lg:flex-row lg:items-end lg:justify-between' : ''}`}>
      <Reveal className={align === 'center' ? 'mx-auto max-w-2xl text-center' : 'max-w-2xl'}>
        {eyebrow && <p className={`eyebrow ${light ? "!text-turquoise" : ""}`}>{t(eyebrow)}</p>}
        <h2 className={`display-lg mt-3 ${light ? 'text-ivory' : 'text-navy'}`}>{t(title)}</h2>
        {description && <p className={`mt-4 text-[16px] leading-relaxed ${light ? 'text-ivory/70' : 'text-ink'}`}>{t(description)}</p>}
      </Reveal>
      {action && <Reveal delay={120} className="shrink-0">{action}</Reveal>}
    </div>
  )
}

export function PageHero({ eyebrow, title, description, image }) {
  const { t, img } = useI18n()
  return (
    <section className="relative isolate overflow-hidden bg-navy">
      {image && <img src={img(image)} data-orig={image} alt="" className="absolute inset-0 h-full w-full object-cover" />}
      <div className="absolute inset-0 bg-gradient-to-b from-navy/80 via-navy/60 to-navy/90" />
      <div className="girih absolute inset-0 opacity-[0.16]" />
      <div className="shell relative py-20 lg:py-28">
        <div className="max-w-3xl animate-rise-in">
          {eyebrow && <p className="eyebrow !text-turquoise">{t(eyebrow)}</p>}
          <h1 className="display-lg mt-3 text-ivory">{t(title)}</h1>
          {description && <p className="mt-5 max-w-xl text-[17px] leading-relaxed text-ivory/80">{t(description)}</p>}
        </div>
      </div>
    </section>
  )
}

export function DestinationCard({ destination: d, delay = 0 }) {
  const t = useT()
  return (
    <Reveal delay={delay} className="h-full">
      <article data-edit-record={`destinations:${d.slug}`} className="card-hover group relative h-full overflow-hidden rounded-[4px] border border-navy/10 bg-card">
        <EditButton resource="destinations" record={d} />
        {d.gallery?.length > 0 ? (
          <div className="relative">
            <Gallery images={[d.image_url, ...d.gallery]} alt={d.name} to={`/destinations/${d.slug}`} className="aspect-[5/4]" dots={false} />
            <div className="pointer-events-none absolute inset-0 z-[5] bg-gradient-to-t from-navy/85 via-navy/10 to-transparent" />
            <div className="pointer-events-none absolute inset-x-0 bottom-0 z-[6] p-5 lg:p-6">
              <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-turquoise">{d.region}</p>
              <h3 className="mt-1.5 font-heading text-[26px] text-ivory lg:text-[30px]">{d.name}</h3>
            </div>
          </div>
        ) : (
        <Link to={`/destinations/${d.slug}`} className="block">
          <div className="relative aspect-[5/4] overflow-hidden">
            <Photo src={d.image_url} alt={d.name} className="h-full w-full object-cover transition-transform duration-[1.2s] ease-out group-hover:scale-[1.06]" />
            <div className="absolute inset-0 bg-gradient-to-t from-navy/85 via-navy/10 to-transparent" />
            <div className="absolute inset-x-0 bottom-0 p-5 lg:p-6">
              <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-turquoise">{d.region}</p>
              <h3 className="mt-1.5 font-heading text-[26px] text-ivory lg:text-[30px]">{d.name}</h3>
            </div>
          </div>
        </Link>
        )}
        <div className="card-pad p-5 lg:p-6">
          <p className="hide-in-row text-[14.5px] leading-relaxed text-ink">{d.summary}</p>
          <div className="mt-5 flex items-center justify-between gap-3 border-t border-navy/10 pt-4">
            <span className="flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-[0.1em] text-ink"><Clock className="h-3.5 w-3.5" />{d.suggested_duration}</span>
            <Link to={`/destinations/${d.slug}`} className="inline-flex items-center gap-1 text-[13px] font-medium text-turquoise-deep hover:text-navy">{t('Explore destination')}<ArrowRight className="h-3.5 w-3.5" /></Link>
          </div>
        </div>
      </article>
    </Reveal>
  )
}

/**
 * A tour or experience card in the style of the big booking sites: photo with ♡, city, title, "duration • group • pickup",
 * rating and the "from" price. With `listOnPhone` the card is a row on phones (photo left, details right), easier to scan.
 */
export function TourCard({ tour: t, delay = 0, listOnPhone = false }) {
  const tr = useT()
  const top = biggestGroup(useGroupTiers())
  const href = `/tours/${t.slug}`
  const priced = Number(t.price_from_usd) > 0
  const meta = [tr(t.duration_label), tr(t.group_type), t.pickup_included && tr('Pickup available')].filter(Boolean)
  const row = listOnPhone
  const photoBox = row ? 'h-full min-h-[150px] sm:h-auto sm:min-h-0 sm:aspect-[4/3]' : 'aspect-[4/3]'
  const badges = (
    <>
      {!row && <span className="pointer-events-none absolute left-3 top-3 z-10 rounded-full bg-white/95 px-2.5 py-1 text-[11px] font-semibold text-navy shadow-sm">{tr(t.category)}</span>}
      {(t.bonuses || []).some((b) => b.title) && <span className="pointer-events-none absolute left-3 top-12 z-10 hidden items-center gap-1 rounded-full bg-gradient-to-r from-[#b8860b] to-[#e0a82e] px-2.5 py-1 text-[11px] font-bold uppercase tracking-[0.1em] text-white shadow sm:inline-flex">🎁 {tr('Bonus')}</span>}
      {t.effective_discount > 0 && priced && <span className="pointer-events-none absolute bottom-3 left-3 z-10 rounded-full bg-destructive px-2.5 py-1 font-mono text-[11px] text-white shadow">−{t.effective_discount}%</span>}
    </>
  )
  return (
    <Reveal delay={delay} className="h-full">
      <article data-edit-record={`tours:${t.slug}`} className={`card-hover group relative flex h-full overflow-hidden rounded-[12px] border border-navy/10 bg-card ${row ? 'flex-row sm:flex-col' : 'flex-col'}`}>
        <EditButton resource="tours" record={t} />
        <div className={`relative ${row ? 'w-[40%] max-w-[170px] shrink-0 sm:w-auto sm:max-w-none' : ''}`}>
          {t.gallery?.length > 0 ? (
            <Gallery images={[t.image_url, ...t.gallery]} alt={t.title} to={href} className={photoBox} counter={false} />
          ) : (
            <Link to={href} tabIndex={-1} className={`relative block overflow-hidden ${photoBox}`}>
              <Photo src={t.image_url} alt={t.title} className="absolute inset-0 h-full w-full object-cover transition-transform duration-[1.2s] ease-out group-hover:scale-[1.06]" />
            </Link>
          )}
          {badges}
          <CardHeart tour={t} className={row ? 'right-2 top-2 h-8 w-8 sm:right-3 sm:top-3 sm:h-9 sm:w-9' : ''} />
          <div className={row ? 'hidden sm:block' : ''}><SelectToggle tour={t} /></div>
        </div>
        <Link to={href} className={`card-pad flex min-w-0 flex-1 flex-col ${row ? 'p-3.5 sm:p-4' : 'p-4'}`}>
          <p className="truncate text-[11px] font-semibold uppercase tracking-[0.06em] text-ink">{t.destination_name}</p>
          <h3 className={`mt-1 font-body font-bold leading-snug tracking-normal text-navy group-hover:text-turquoise-deep ${row ? 'line-clamp-3 text-[15.5px] sm:text-[17px]' : 'line-clamp-3 text-[17px]'}`}>{t.title}</h3>
          <p className="mt-1.5 text-[13px] leading-snug text-ink">{meta.join(' • ')}</p>
          <BonusLine tour={t} className="mt-2" />
          <div className="mt-auto flex flex-wrap items-end justify-between gap-x-3 gap-y-1 pt-3">
            {t.review_count > 0 ? (
              <span className="inline-flex items-center gap-1 text-[13px]"><Star className="h-3.5 w-3.5 fill-[#ff5533] text-[#ff5533]" /><span className="font-semibold text-navy">{Number(t.rating).toFixed(1)}</span><span className="text-ink/80">({t.review_count})</span></span>
            ) : <span />}
            {priced || !t.entrance_fee_usd ? (
              <span className="ml-auto text-right">
                <span className="block text-[11.5px] leading-tight text-ink">{tr(usesGroupPricing(t) ? 'From, group of {n}+' : 'From', { n: top })}</span>
                <span className="whitespace-nowrap text-[18px] font-bold text-navy [&_del]:font-body [&_span]:font-body"><PriceTag amount={t.price_from_usd} percent={t.effective_discount} badge={false} /><span className="ml-1 text-[12px] font-normal text-ink">/ {tr('person')}</span></span>
              </span>
            ) : (
              <span className="ml-auto text-right">
                <span className="block text-[11.5px] text-ink">{tr('Entrance ticket')}</span>
                <span className="font-mono text-[18px] font-semibold tabular-nums text-navy">{money(t.entrance_fee_usd)}</span>
              </span>
            )}
          </div>
        </Link>
      </article>
    </Reveal>
  )
}

export function Skeleton({ count = 6 }) {
  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3" aria-hidden="true">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="overflow-hidden rounded-[4px] border border-navy/10 bg-white">
          <div className="aspect-[4/3] w-full animate-pulse bg-navy/10" />
          <div className="space-y-3 p-5"><div className="h-3 w-24 animate-pulse rounded bg-navy/10" /><div className="h-5 w-3/4 animate-pulse rounded bg-navy/10" /><div className="h-3 w-full animate-pulse rounded bg-navy/10" /></div>
        </div>
      ))}
    </div>
  )
}

export function EmptyState({ title = 'Nothing here yet', body }) {
  const t = useT()
  return <div className="rounded-sm border border-dashed border-navy/20 bg-sand-soft/40 p-10 text-center"><p className="font-heading text-[24px]">{t(title)}</p>{body && <p className="mt-2 text-ink">{t(body)}</p>}</div>
}

/** A hidden text box that people never see; robots fill it in, and the server then ignores the message. */
export function Honeypot({ value, onChange }) {
  return <input type="text" name="website" tabIndex={-1} autoComplete="off" aria-hidden="true" value={value} onChange={onChange} className="absolute -left-[9999px] h-0 w-0 opacity-0" />
}

export function Spinner() { return <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> }

export function Success({ title, children }) {
  const t = useT()
  return (
    <div className="rounded-sm border border-turquoise-deep/30 bg-sand-soft/60 p-5">
      <div className="flex items-start gap-3"><CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-turquoise-deep" />
        <div><p className="text-[14px] font-medium text-navy">{t(title)}</p><div className="mt-1 text-[13px] leading-relaxed text-navy/80">{children}</div></div></div>
    </div>
  )
}

export function Field({ label, error, children }) {
  const t = useT()
  return <label className="label">{t(label)}{children}{error && <span className="mt-1 block text-[11.5px] text-destructive">{t(error)}</span>}</label>
}

export const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/
export const PHONE_RE = /^\+?[0-9\s\-()]{7,20}$/
