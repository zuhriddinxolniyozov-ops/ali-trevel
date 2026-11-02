import { useEffect, useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { api } from '../api'
import { exactMoney, useFetch } from '../hooks'
import { DEFAULT_TIERS, sortedTiers, tierRanges } from '../groupPricing'
import { useT } from '../i18n'
import { Spinner } from '../components/ui'

const field = 'h-10 w-28 rounded-sm border border-navy/15 bg-white px-3 text-[14px] text-navy outline-none focus:border-navy'

export default function GroupPricing() {
  const t = useT()
  const { data, loading } = useFetch('/site-content/')
  const [rows, setRows] = useState(null)
  const [state, setState] = useState('idle')
  const [error, setError] = useState('')
  useEffect(() => { if (data && !rows) setRows(sortedTiers(data.group_pricing_tiers).map((x) => ({ ...x }))) }, [data, rows])
  if (loading || !rows) return <Spinner />

  const set = (i, k) => (e) => { setState('idle'); setRows((r) => r.map((x, j) => (j === i ? { ...x, [k]: e.target.value } : x))) }
  const sample = 289

  async function save(e) {
    e.preventDefault()
    const tiers = rows.map((x) => ({ min: Number(x.min), percent: Number(x.percent) }))
    if (tiers.some((x) => !Number.isInteger(x.min) || x.min < 1 || !(x.percent >= 10))) return setError(t('Every row needs a number of travelers (1 or more) and a percentage.'))
    if (!tiers.some((x) => x.min === 1)) return setError(t('One row must start at 1 traveler, so every group size has a price.'))
    if (new Set(tiers.map((x) => x.min)).size !== tiers.length) return setError(t('Each group size can appear only once.'))
    setError(''); setState('saving')
    try { const res = await api.put('/site-content/', { group_pricing_tiers: tiers }); setRows(sortedTiers(res.group_pricing_tiers)); setState('saved') } catch (ex) { setError(ex.message); setState('idle') }
  }

  const shown = tierRanges(rows.map((x) => ({ min: Number(x.min) || 0, percent: Number(x.percent) || 0 })).filter((x) => x.min >= 1))
  return (
    <form onSubmit={save} className="max-w-3xl space-y-6">
      <p className="text-[14px] leading-relaxed text-ink">{t('The price you enter on a tour is the price per person for a group of 20 or more. Smaller groups pay a higher percentage of it. Visitors see the price for their group size at the end of the booking form, with an explanation. Tours with “Price depends on group size” switched off (for example classes) are not affected.')}</p>
      <div className="rounded-md border border-navy/10 bg-white p-5">
        <div className="grid grid-cols-[1fr_1fr_auto] items-center gap-3 font-mono text-[10px] uppercase tracking-[0.16em] text-ink"><span>{t('From this many travelers')}</span><span>{t('Price per person (% of the listed price)')}</span><span /></div>
        <div className="mt-2 space-y-2">
          {rows.map((r, i) => (
            <div key={i} className="grid grid-cols-[1fr_1fr_auto] items-center gap-3">
              <input type="number" min="1" className={field} value={r.min} onChange={set(i, 'min')} aria-label={t('From this many travelers')} />
              <input type="number" min="10" className={field} value={r.percent} onChange={set(i, 'percent')} aria-label={t('Price per person (% of the listed price)')} />
              <button type="button" onClick={() => setRows((x) => x.filter((_, j) => j !== i))} aria-label={t('Delete')} className="grid h-9 w-9 place-items-center rounded-full border border-red-200 text-destructive hover:bg-red-50"><Trash2 className="h-3.5 w-3.5" /></button>
            </div>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <button type="button" onClick={() => setRows((x) => [...x, { min: '', percent: 100 }])} className="inline-flex h-9 items-center gap-1.5 rounded-full border border-navy/15 px-4 text-[13px] hover:bg-sand-soft"><Plus className="h-3.5 w-3.5" />{t('Add a row')}</button>
          <button type="button" onClick={() => { setState('idle'); setRows(DEFAULT_TIERS.map((x) => ({ ...x }))) }} className="h-9 rounded-full border border-navy/15 px-4 text-[13px] hover:bg-sand-soft">{t('Restore suggested values')}</button>
        </div>
      </div>
      <div className="rounded-md border border-navy/10 bg-sand-soft/50 p-5">
        <p className="text-[13px] font-medium text-navy">{t('Preview for a tour listed at {price}', { price: exactMoney(sample) })}</p>
        <ul className="mt-2 divide-y divide-navy/10 text-[14px]">
          {shown.map((r) => (
            <li key={r.min} className="flex justify-between py-1.5"><span>{r.max === null ? t('{n} or more travelers', { n: r.min }) : r.min === r.max ? t(r.min === 1 ? '1 traveler' : '{n} travelers', { n: r.min }) : t('{from}–{to} travelers', { from: r.min, to: r.max })}</span><span className="font-mono">{exactMoney(sample * r.percent / 100)} · {r.percent}%</span></li>
          ))}
        </ul>
      </div>
      {error && <p role="alert" className="text-[13px] text-destructive">{error}</p>}
      <div className="flex items-center gap-3">
        <button disabled={state === 'saving'} className="btn-primary">{state === 'saving' && <Spinner />}{t('Save')}</button>
        {state === 'saved' && <span className="text-[13px] text-turquoise-deep">{t('Saved')}</span>}
      </div>
    </form>
  )
}
