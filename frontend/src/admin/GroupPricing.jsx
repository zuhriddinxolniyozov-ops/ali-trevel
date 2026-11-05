import { useEffect, useMemo, useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { api } from '../api'
import { exactMoney, useFetch } from '../hooks'
import { DEFAULT_TIERS, sortedTiers, tierRanges, usesGroupPricing } from '../groupPricing'
import { PACKAGES } from '../components/PackageCard'
import { useT } from '../i18n'
import { Spinner } from '../components/ui'
import { isLocal, roundPrice } from '../market'

const field = 'h-10 w-full max-w-[9rem] rounded-sm border border-navy/15 bg-white px-3 text-[14px] text-navy outline-none focus:border-navy'
const cents = (x) => roundPrice(x)

/**
 * Prices by group size, written in dollars for one tour (by default the 2-day Samarkand tour). The site keeps them as
 * proportions of that tour's listed price, so every other tour follows the same steps; the preview shows them in dollars.
 */
export default function GroupPricing() {
  const t = useT()
  const { data, loading } = useFetch('/site-content/')
  const { data: tours } = useFetch('/tours/', { list: true })
  const priced = useMemo(() => tours.filter((x) => usesGroupPricing(x) && !x.parent_slug), [tours])
  const [refSlug, setRefSlug] = useState('samarkand-city-tour')
  const ref = priced.find((x) => x.slug === refSlug) || priced[0]
  const listed = Number(ref?.price_from_usd) || 0
  const [rows, setRows] = useState(null)        // [{min, price}] in dollars for the reference tour
  const [state, setState] = useState('idle')
  const [error, setError] = useState('')
  const toRows = (tiers) => sortedTiers(tiers).map((x) => ({ min: x.min, price: cents(listed * x.percent / 100) }))
  useEffect(() => { if (data && listed && !rows) setRows(toRows(data.group_pricing_tiers)) }, [data, listed, rows])   // eslint-disable-line react-hooks/exhaustive-deps
  if (loading || !rows || !ref) return <Spinner />

  const set = (i, k) => (e) => { setState('idle'); setRows((r) => r.map((x, j) => (j === i ? { ...x, [k]: e.target.value } : x))) }
  const tiersOf = (list) => list.map((x) => ({ min: Number(x.min), percent: Math.round((Number(x.price) / listed) * 100 * 1e6) / 1e6 }))
  const changeRef = (slug) => {   // the same steps, shown in the dollars of another tour
    const current = tiersOf(rows)
    const next = priced.find((x) => x.slug === slug)
    setRefSlug(slug)
    setRows(sortedTiers(current).map((x) => ({ min: x.min, price: cents(Number(next.price_from_usd) * x.percent / 100) })))
  }

  async function save(e) {
    e.preventDefault()
    if (rows.some((x) => !Number.isInteger(Number(x.min)) || Number(x.min) < 1 || !(Number(x.price) > 0))) return setError(t('Every row needs a number of travelers (1 or more) and a price.'))
    const tiers = tiersOf(rows)
    if (!tiers.some((x) => x.min === 1)) return setError(t('One row must start at 1 traveler, so every group size has a price.'))
    if (new Set(tiers.map((x) => x.min)).size !== tiers.length) return setError(t('Each group size can appear only once.'))
    setError(''); setState('saving')
    try { const res = await api.put('/site-content/', { group_pricing_tiers: tiers }); setRows(toRows(res.group_pricing_tiers)); setState('saved') } catch (ex) { setError(ex.message); setState('idle') }
  }

  const ranges = tierRanges(tiersOf(rows.filter((x) => Number(x.min) >= 1 && Number(x.price) > 0)))
  const label = (r) => (r.max === null ? t('{n} or more travelers', { n: r.min }) : r.min === r.max ? t(r.min === 1 ? '1 traveler' : '{n} travelers', { n: r.min }) : t('{from}–{to} travelers', { from: r.min, to: r.max }))
  const previewTours = [ref, ...Object.keys(PACKAGES).map((s) => priced.find((x) => x.slug === s)).filter((x) => x && x.slug !== ref.slug)].slice(0, 3)
  return (
    <form onSubmit={save} className="max-w-4xl space-y-6">
      <p className="text-[14px] leading-relaxed text-ink">{t('Write the price per person for each group size of one tour. Every other tour follows the same steps: if a group of 1–2 pays 40% more on this tour, it pays 40% more on the others too. Tours with “Price depends on group size” switched off (for example classes) are not affected.')}</p>
      <div className="rounded-md border border-navy/10 bg-white p-5">
        <label className="label max-w-md">{t('Prices written for this tour')}
          <select className="input" value={ref.slug} onChange={(e) => changeRef(e.target.value)}>
            {priced.map((x) => <option key={x.slug} value={x.slug}>{x.title} — {exactMoney(Number(x.price_from_usd))}</option>)}
          </select></label>
        <div className="mt-5 grid grid-cols-[1fr_1fr_auto] items-center gap-3 font-mono text-[10px] uppercase tracking-[0.16em] text-ink"><span>{t('From this many travelers')}</span><span>{t('Price per person ($)')}</span><span /></div>
        <div className="mt-2 space-y-2">
          {rows.map((r, i) => (
            <div key={i} className="grid grid-cols-[1fr_1fr_auto] items-center gap-3">
              <input type="number" min="1" className={field} value={r.min} onChange={set(i, 'min')} aria-label={t('From this many travelers')} />
              <div className="relative max-w-[11rem]">{!isLocal && <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[14px] text-ink">$</span>}
                <input type="number" min="1" step="any" className={`${field} ${isLocal ? 'max-w-[11rem]' : 'pl-6'}`} value={r.price} onChange={set(i, 'price')} aria-label={t('Price per person ($)')} /></div>
              <button type="button" onClick={() => setRows((x) => x.filter((_, j) => j !== i))} aria-label={t('Delete')} className="grid h-9 w-9 place-items-center rounded-full border border-red-200 text-destructive hover:bg-red-50"><Trash2 className="h-3.5 w-3.5" /></button>
            </div>
          ))}
        </div>
        <p className="mt-3 text-[12.5px] text-ink">{t('The tour page shows {price} — the price of the biggest group. Write the same amount in the first row.', { price: exactMoney(listed) })}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <button type="button" onClick={() => setRows((x) => [...x, { min: '', price: listed }])} className="inline-flex h-9 items-center gap-1.5 rounded-full border border-navy/15 px-4 text-[13px] hover:bg-sand-soft"><Plus className="h-3.5 w-3.5" />{t('Add a row')}</button>
          <button type="button" onClick={() => { setState('idle'); setRows(toRows(DEFAULT_TIERS)) }} className="h-9 rounded-full border border-navy/15 px-4 text-[13px] hover:bg-sand-soft">{t('Restore suggested values')}</button>
        </div>
      </div>
      <div className="overflow-x-auto rounded-md border border-navy/10 bg-sand-soft/50 p-5">
        <p className="text-[13px] font-medium text-navy">{t('What travelers pay per person')}</p>
        <table className="mt-2 w-full min-w-[520px] text-[14px]">
          <thead><tr className="text-left font-mono text-[10px] uppercase tracking-[0.12em] text-ink"><th className="py-1.5 font-normal">{t('Group')}</th>
            {previewTours.map((x) => <th key={x.slug} className="py-1.5 text-right font-normal">{x.title.length > 28 ? `${x.title.slice(0, 26)}…` : x.title}</th>)}</tr></thead>
          <tbody className="divide-y divide-navy/10">
            {ranges.map((r) => (
              <tr key={r.min}><td className="py-1.5">{label(r)}</td>
                {previewTours.map((x) => <td key={x.slug} className="py-1.5 text-right font-mono">{exactMoney(cents(Number(x.price_from_usd) * r.percent / 100))}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
      {error && <p role="alert" className="text-[13px] text-destructive">{error}</p>}
      <div className="flex items-center gap-3">
        <button disabled={state === 'saving'} className="btn-primary">{state === 'saving' && <Spinner />}{t('Save')}</button>
        {state === 'saved' && <span className="text-[13px] text-turquoise-deep">{t('Saved')}</span>}
      </div>
    </form>
  )
}
