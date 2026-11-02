import { ArrowDown, ArrowUp, Plus, Trash2 } from 'lucide-react'
import { useT } from '../i18n'
import { parseStop } from '../components/DayPlan'

const TYPES = [['visit', 'Visit a place'], ['meal', 'Meal'], ['transfer', 'Transfer to a place'], ['free', 'Free time'], ['custom', 'Custom']]
const MEALS = [['breakfast', 'Breakfast'], ['lunch', 'Lunch'], ['dinner', 'Dinner']]
const LANGS = [['uz', "O'zbekcha"], ['ru', 'Русский'], ['fr', 'Français'], ['de', 'Deutsch'], ['es', 'Español']]
const CATEGORIES = ['guide', 'transport', 'meals', 'hotel', 'tickets', 'marketing', 'office', 'other']
const PER = [['person', 'per person'], ['group', 'per group'], ['day', 'per day']]
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1)

const blank = { visit: { stop: 0 }, meal: { meal: 'lunch', included: false }, transfer: { stop: 0 }, free: {}, custom: { text: '' } }
const small = 'h-9 rounded-sm border border-navy/15 bg-white px-2 text-[13px] text-navy outline-none focus:border-navy'

function IconButton({ label, onClick, disabled, children }) {
  return <button type="button" aria-label={label} title={label} disabled={disabled} onClick={onClick} className="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-navy/15 text-navy hover:bg-sand-soft disabled:opacity-30">{children}</button>
}

/** Day-by-day plan editor: days, each a list of timed items (visit, meal, transfer, free time or custom text). */
export function ItineraryField({ label, help, value, onChange, route }) {
  const t = useT()
  const stops = (Array.isArray(route) ? route : String(route || '').split('\n')).filter((l) => String(l).trim()).map(parseStop)
  const days = value || []
  const setDays = (next) => onChange(next.map((d, i) => ({ ...d, day: i + 1 })))
  const setItem = (di, ii, patch) => setDays(days.map((d, i) => (i === di ? { ...d, items: d.items.map((it, j) => (j === ii ? { ...it, ...patch } : it)) } : d)))
  const move = (di, ii, by) => setDays(days.map((d, i) => {
    if (i !== di) return d
    const items = [...d.items]
    ;[items[ii], items[ii + by]] = [items[ii + by], items[ii]]
    return { ...d, items }
  }))
  const changeType = (di, ii, type) => setDays(days.map((d, i) => (i === di ? { ...d, items: d.items.map((it, j) => (j === ii ? { time: it.time, type, ...blank[type] } : it)) } : d)))

  return (
    <div className="label sm:col-span-2">{label}
      {help && <span className="mt-1 block text-[12px] font-normal text-ink/80">{help}</span>}
      <div className="mt-3 space-y-4 font-normal">
        {days.map((day, di) => (
          <div key={di} className="rounded-sm border border-navy/12 bg-sand-soft/30 p-3">
            <div className="mb-2 flex items-center justify-between">
              <p className="font-heading text-[20px] text-navy">{t('Day {n}', { n: di + 1 })}</p>
              <button type="button" onClick={() => setDays(days.filter((_, i) => i !== di))} className="text-[12px] text-destructive hover:underline">{t('Remove day')}</button>
            </div>
            <div className="space-y-2">
              {day.items.map((item, ii) => (
                <div key={ii} className="rounded-sm border border-navy/10 bg-white p-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <input type="time" aria-label={t('Time')} className={`${small} w-[104px]`} value={item.time || ''} onChange={(e) => setItem(di, ii, { time: e.target.value })} />
                    <select aria-label={t('Type')} className={small} value={item.type} onChange={(e) => changeType(di, ii, e.target.value)}>
                      {TYPES.map(([k, l]) => <option key={k} value={k}>{t(l)}</option>)}</select>
                    {(item.type === 'visit' || item.type === 'transfer') && (
                      <select aria-label={t('Place')} className={`${small} min-w-[180px] flex-1`} value={item.stop ?? 0} onChange={(e) => setItem(di, ii, { stop: Number(e.target.value) })}>
                        {stops.length === 0 && <option value={0}>{t('Add route stops first')}</option>}
                        {stops.map((s, i) => <option key={i} value={i}>{s.name}</option>)}</select>)}
                    {item.type === 'meal' && <>
                      <select aria-label={t('Meal type')} className={small} value={item.meal} onChange={(e) => setItem(di, ii, { meal: e.target.value })}>{MEALS.map(([k, l]) => <option key={k} value={k}>{t(l)}</option>)}</select>
                      <label className="flex items-center gap-1.5 text-[13px]"><input type="checkbox" checked={item.included !== false} onChange={(e) => setItem(di, ii, { included: e.target.checked })} />{t('Included in the price')}</label></>}
                    {item.type === 'custom' && <input aria-label={t('Text')} className={`${small} min-w-[200px] flex-1`} placeholder={t('What happens at this time')} value={item.text || ''} onChange={(e) => setItem(di, ii, { text: e.target.value })} />}
                    <span className="ml-auto flex gap-1">
                      <IconButton label={t('Move up')} disabled={ii === 0} onClick={() => move(di, ii, -1)}><ArrowUp className="h-3.5 w-3.5" /></IconButton>
                      <IconButton label={t('Move down')} disabled={ii === day.items.length - 1} onClick={() => move(di, ii, 1)}><ArrowDown className="h-3.5 w-3.5" /></IconButton>
                      <IconButton label={t('Delete')} onClick={() => setDays(days.map((d, i) => (i === di ? { ...d, items: d.items.filter((_, j) => j !== ii) } : d)))}><Trash2 className="h-3.5 w-3.5 text-destructive" /></IconButton>
                    </span>
                  </div>
                  {item.type === 'custom' && (
                    <details className="mt-2 text-[12px] text-ink"><summary className="cursor-pointer">{t('Translations')}</summary>
                      <div className="mt-2 grid gap-2 sm:grid-cols-2">{LANGS.map(([code, name]) => (
                        <input key={code} aria-label={name} placeholder={name} className={small} value={item.i18n?.[code] || ''}
                          onChange={(e) => setItem(di, ii, { i18n: { ...(item.i18n || {}), [code]: e.target.value } })} />))}</div></details>)}
                </div>
              ))}
            </div>
            <button type="button" onClick={() => setDays(days.map((d, i) => (i === di ? { ...d, items: [...d.items, { time: '09:00', type: 'visit', stop: 0 }] } : d)))}
              className="mt-2 inline-flex items-center gap-1.5 rounded-full border border-navy/20 px-3.5 py-1.5 text-[12px] text-navy hover:bg-white"><Plus className="h-3.5 w-3.5" />{t('Add an item')}</button>
          </div>
        ))}
        <button type="button" onClick={() => setDays([...days, { items: [{ time: '08:00', type: 'meal', meal: 'breakfast', included: true }] }])}
          className="btn-outline !h-10 !text-[13px]"><Plus className="h-4 w-4" />{t('Add a day')}</button>
      </div>
    </div>
  )
}

/** Expected costs of delivering the tour; Accounting turns them into real expenses for a finished booking. */
export function CostsField({ label, help, value, onChange }) {
  const t = useT()
  const rows = value || []
  const set = (i, patch) => onChange(rows.map((r, j) => (j === i ? { ...r, ...patch } : r)))
  const guests = 2
  const days = 2
  const estimate = rows.reduce((sum, r) => sum + Number(r.amount_usd || 0) * (r.per === 'person' ? guests : r.per === 'day' ? days : 1), 0)
  return (
    <div className="label sm:col-span-2">{label}
      {help && <span className="mt-1 block text-[12px] font-normal text-ink/80">{help}</span>}
      <div className="mt-3 space-y-2 font-normal">
        {rows.map((r, i) => (
          <div key={i} className="flex flex-wrap items-center gap-2 rounded-sm border border-navy/10 bg-white p-2">
            <input aria-label={t('Cost name')} className={`${small} min-w-[160px] flex-1`} placeholder={t('Cost name')} value={r.name || ''} onChange={(e) => set(i, { name: e.target.value })} />
            <select aria-label={t('Category')} className={small} value={r.category || 'other'} onChange={(e) => set(i, { category: e.target.value })}>{CATEGORIES.map((c) => <option key={c} value={c}>{t(cap(c))}</option>)}</select>
            <select aria-label={t('Per')} className={small} value={r.per || 'group'} onChange={(e) => set(i, { per: e.target.value })}>{PER.map(([k, l]) => <option key={k} value={k}>{t(l)}</option>)}</select>
            <input type="number" min="0" step="any" aria-label={t('Amount (USD)')} className={`${small} w-28`} placeholder="USD" value={r.amount_usd ?? ''} onChange={(e) => set(i, { amount_usd: e.target.value === '' ? '' : Number(e.target.value) })} />
            <IconButton label={t('Delete')} onClick={() => onChange(rows.filter((_, j) => j !== i))}><Trash2 className="h-3.5 w-3.5 text-destructive" /></IconButton>
          </div>
        ))}
        <div className="flex flex-wrap items-center gap-3">
          <button type="button" onClick={() => onChange([...rows, { name: '', category: 'guide', per: 'group', amount_usd: '' }])} className="btn-outline !h-10 !text-[13px]"><Plus className="h-4 w-4" />{t('Add a cost')}</button>
          {rows.length > 0 && <span className="text-[12.5px] text-ink">{t('Example: 2 travelers, 2 days')} → <span className="font-mono text-navy">${estimate.toLocaleString('en-US')}</span></span>}
        </div>
      </div>
    </div>
  )
}
