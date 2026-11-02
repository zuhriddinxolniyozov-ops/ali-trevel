import { Users } from 'lucide-react'
import { exactMoney } from '../hooks'
import { tierRanges } from '../groupPricing'
import { useT } from '../i18n'

const rangeLabel = (t, r) => {
  if (r.max === null) return t('{n} or more travelers', { n: r.min })
  if (r.min === r.max) return r.min === 1 ? t('1 traveler') : t('{n} travelers', { n: r.min })
  return t('{from}–{to} travelers', { from: r.min, to: r.max })
}

/**
 * The last thing a traveller sees before sending a request, and again once it is sent: what one person pays for their group size,
 * the price at every group size, and why smaller groups pay more per person.
 */
export default function GroupPrice({ tiers, priceAt, guests, perPerson, total }) {
  const t = useT()
  const ranges = tierRanges(tiers)
  const n = Math.max(1, Number(guests) || 1)
  return (
    <div className="mt-4 rounded-sm border border-gold/40 bg-white p-4">
      <p className="flex flex-wrap items-center gap-x-2 text-[13px] font-medium text-navy"><Users className="h-4 w-4 text-turquoise-deep" />
        {t('{n} travelers × {price} per person', { n, price: exactMoney(perPerson) })} = <span className="font-mono">{exactMoney(total)}</span></p>
      <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.16em] text-ink">{t('Price per person by group size')}</p>
      <ul className="mt-1.5 divide-y divide-navy/10 text-[13px]">
        {ranges.map((r) => {
          const active = n >= r.min && (r.max === null || n <= r.max)
          return (
            <li key={r.min} className={`flex items-center justify-between px-2 py-1.5 ${active ? 'rounded-sm bg-sand-soft font-medium text-navy' : 'text-ink'}`}>
              <span>{rangeLabel(t, r)}{active && ` ← ${t('your group')}`}</span>
              <span className="font-mono">{exactMoney(priceAt(r.min))}</span>
            </li>
          )
        })}
      </ul>
      <p className="mt-3 text-[12.5px] font-medium text-navy">{t('Why does the price per person change?')}</p>
      <p className="mt-1 text-[12.5px] leading-relaxed text-ink">{t('A guide, a vehicle, fuel and the organisation of a tour cost the same whether 2 people travel or 20. In a big group these fixed costs are shared by many travellers, so each person pays less; in a small group fewer people share them, so each person pays more. That is why our listed prices are for a group of 20 or more, and smaller groups pay a little more per person. You always see your exact price here before you send the request, and nothing is charged until our team confirms.')}</p>
    </div>
  )
}
