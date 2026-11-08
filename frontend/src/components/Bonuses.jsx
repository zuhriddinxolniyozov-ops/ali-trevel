import { Clock, Gift, Sparkles, Star, CircleCheck } from 'lucide-react'
import { useI18n } from '../i18n'
import Gallery from './Gallery'

export const TAGS = { bonus: ['Bonus', Gift], exclusive: ['Exclusive', Sparkles], gift: ['Gift', Star] }

/** A bonus text in the visitor's language (the English one when it is not translated). */
export const bonusText = (b, field, lang) => b?.i18n?.[lang]?.[field] || b?.[field] || ''

/** One line for a tour card: "🎁 Bonus: In memory of Islam Karimov (+1)". */
export function BonusLine({ tour, className = '' }) {
  const { t, lang } = useI18n()
  const list = (tour.bonuses || []).filter((b) => b.title)
  if (!list.length) return null
  return (
    <p className={`flex items-start gap-1.5 text-[12.5px] font-medium leading-snug text-[#9a6b00] ${className}`}>
      <Gift className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
      <span className="line-clamp-2">{t('Bonus')}: {bonusText(list[0], 'title', lang)}{list.length > 1 ? ` (+${list.length - 1})` : ''}</span>
    </p>
  )
}

/** The special bonuses of a tour: their own golden block on the tour page, with photos and the full story of each. */
export default function TourBonuses({ tour }) {
  const { t, lang } = useI18n()
  const list = (tour.bonuses || []).filter((b) => b.title)
  if (!list.length) return null
  return (
    <section id="bonuses" aria-labelledby="bonuses-title" className="relative mt-12 scroll-mt-28 overflow-hidden rounded-[16px] border border-[#e8c36a]/60 bg-gradient-to-br from-[#fff8e6] via-[#fffdf7] to-[#fdf1d6] p-5 sm:p-7">
      <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-[#f5d27a]/30 blur-2xl" aria-hidden="true" />
      <p className="inline-flex items-center gap-1.5 rounded-full bg-[#b8860b] px-3 py-1 font-mono text-[10px] uppercase tracking-[0.18em] text-white"><Gift className="h-3.5 w-3.5" />{t('Special bonuses')}</p>
      <h3 id="bonuses-title" className="mt-3 font-heading text-[30px] leading-tight text-navy">{t(list.length > 1 ? '{n} special bonuses in this tour' : 'A special bonus in this tour', { n: list.length })}</h3>
      <p className="mt-1 text-[14px] text-ink">{t('Included in the price: no extra payment.')}</p>
      <div className={`mt-6 grid gap-5 ${list.length > 1 ? 'lg:grid-cols-2' : ''}`}>
        {list.map((b, i) => {
          const [tagLabel, TagIcon] = TAGS[b.tag] || TAGS.bonus
          const photos = [b.image, ...(b.gallery || [])].filter(Boolean)
          const duration = bonusText(b, 'duration', lang)
          return (
            <article key={i} className={`overflow-hidden rounded-[14px] border border-[#e8c36a]/50 bg-white shadow-[0_18px_40px_-28px_rgba(154,107,0,0.55)] ${list.length === 1 ? 'md:grid md:grid-cols-[1.1fr_1fr]' : ''}`}>
              <div className="relative">
                {photos.length > 1
                  ? <Gallery images={photos} alt={bonusText(b, 'title', lang)} className={list.length === 1 ? 'aspect-[4/3] md:aspect-auto md:h-full md:min-h-[300px]' : 'aspect-[16/10]'} counter={false} />
                  : photos.length === 1
                    ? <img src={photos[0]} alt={bonusText(b, 'title', lang)} loading="lazy" className={`w-full object-cover ${list.length === 1 ? 'aspect-[4/3] md:aspect-auto md:h-full md:min-h-[300px]' : 'aspect-[16/10]'}`} />
                    : <div className="grid aspect-[16/10] place-items-center bg-gradient-to-br from-[#fdf1d6] to-[#f5d27a]"><Gift className="h-12 w-12 text-[#b8860b]" /></div>}
                <span className="pointer-events-none absolute left-3 top-3 z-10 inline-flex items-center gap-1.5 rounded-full bg-gradient-to-r from-[#b8860b] to-[#e0a82e] px-3 py-1.5 text-[11px] font-bold uppercase tracking-[0.12em] text-white shadow-md">
                  <TagIcon className="h-3.5 w-3.5" />{t(tagLabel)}</span>
              </div>
              <div className="flex flex-col p-5">
                <h4 className="font-body text-[19px] font-bold leading-snug tracking-normal text-navy">{bonusText(b, 'title', lang)}</h4>
                <div className="mt-2 flex flex-wrap gap-2 text-[12.5px]">
                  {duration && <span className="inline-flex items-center gap-1 rounded-full bg-sand-soft px-2.5 py-1 text-navy"><Clock className="h-3.5 w-3.5 text-turquoise-deep" />{duration}</span>}
                  <span className="inline-flex items-center gap-1 rounded-full bg-[#f0fdf4] px-2.5 py-1 text-[#15803d]"><CircleCheck className="h-3.5 w-3.5" />{t('Included in the price')}</span>
                </div>
                <p className="mt-3 whitespace-pre-line text-[14.5px] leading-relaxed text-ink">{bonusText(b, 'text', lang)}</p>
              </div>
            </article>
          )
        })}
      </div>
    </section>
  )
}
