import { Link } from 'react-router-dom'
import { ArrowRight, Landmark, Users } from 'lucide-react'
import { Reveal, money } from '../hooks'
import { useT } from '../i18n'
import { EditButton } from '../edit/Add'
import { Photo } from './ui'

/**
 * An advert between the home page's Destinations and Tours sections: the three cheapest places to visit (by entrance ticket).
 * A place cannot be visited on its own, so every card leads to the full tour it belongs to.
 */
export default function BestValue({ tours }) {
  const t = useT()
  const byslug = Object.fromEntries(tours.map((x) => [x.slug, x]))
  const places = tours.filter((x) => x.parent_slug && byslug[x.parent_slug] && Number(x.entrance_fee_usd) > 0)
    .sort((a, b) => Number(a.entrance_fee_usd) - Number(b.entrance_fee_usd)).slice(0, 3)
  if (places.length < 3) return null
  return (
    <section className="border-y border-gold/30 bg-gold/10 py-12 lg:py-14" aria-label={t('Best value stops')}>
      <div className="shell">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="eyebrow">{t('Best value stops')}</p>
            <h2 className="mt-2 font-heading text-[28px] leading-tight text-navy lg:text-[34px]">{t('Great places, small tickets')}</h2>
          </div>
          <p className="max-w-md text-[13px] leading-relaxed text-ink">{t('These places are visited as part of a full tour; they cannot be booked on their own.')}</p>
        </div>
        <div className="swipe-row mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {places.map((p, i) => {
            const parent = byslug[p.parent_slug]
            return (
              <Reveal key={p.slug} delay={i * 80} className="h-full">
                <article data-edit-record={`tours:${p.slug}`} className="card-hover group relative flex h-full flex-col overflow-hidden rounded-[4px] border border-navy/10 bg-card">
                  <EditButton resource="tours" record={p} />
                  <Link to={`/tours/${parent.slug}`} className="relative block aspect-[16/9] overflow-hidden" aria-label={p.title}>
                    <Photo src={p.image_url} alt={p.title} className="h-full w-full object-cover transition-transform duration-[1.2s] ease-out group-hover:scale-[1.05]" />
                    <span className="absolute left-3 top-3 rounded-full bg-gold px-3 py-1 font-mono text-[10px] uppercase tracking-[0.14em] text-navy">{t('Entrance ticket')} {money(p.entrance_fee_usd)}</span>
                  </Link>
                  <div className="card-pad flex flex-1 flex-col p-5">
                    <h3 className="font-heading text-[22px] leading-tight text-navy">{p.title}</h3>
                    <p className="hide-in-row mt-2 line-clamp-2 text-[14px] leading-relaxed text-ink">{p.summary}</p>
                    <p className="mt-3 flex items-start gap-1.5 text-[12px] text-ink"><Landmark className="mt-0.5 h-3.5 w-3.5 shrink-0 text-turquoise-deep" />{t('Part of')}: <span className="font-medium text-navy">{parent.title}</span></p>
                    <div className="mt-auto flex items-end justify-between gap-3 border-t border-navy/10 pt-4">
                      <div>
                        <p className="inline-flex items-center gap-1 text-[12px] text-ink"><Users className="h-3.5 w-3.5" />{t(p.group_type)}</p>
                        <p className="text-[20px] font-medium text-navy"><span className="font-mono tabular-nums">{money(p.entrance_fee_usd)}</span><span className="ml-1 text-[0.78em] text-ink">/ {t('person')}</span></p>
                      </div>
                      <Link to={`/tours/${parent.slug}`} className="inline-flex items-center gap-1 rounded-full border border-navy/20 px-4 py-2 text-[12px] font-medium text-navy transition-colors hover:border-navy hover:bg-navy hover:text-ivory">{t('View the full tour')}<ArrowRight className="h-3.5 w-3.5" /></Link>
                    </div>
                  </div>
                </article>
              </Reveal>
            )
          })}
        </div>
      </div>
    </section>
  )
}
