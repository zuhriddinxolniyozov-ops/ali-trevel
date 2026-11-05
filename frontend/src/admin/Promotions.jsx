import { useState } from 'react'
import { isLocal } from '../market'
import { Pencil, Plus, Trash2 } from 'lucide-react'
import { api } from '../api'
import { discounted, exactMoney, useFetch } from '../hooks'
import { LANGS, useT } from '../i18n'
import { Spinner } from '../components/ui'

const APPLIES = [['all', 'Everything'], ['tours', 'Tours'], ['hotels', 'Hotels'], ['transport', 'Transport']]
const blank = { title: '', message: '', percent: 10, applies_to: 'all', starts_on: '', ends_on: '', active: true, destinations: [], tours: [], i18n: {} }
const today = () => new Date().toISOString().slice(0, 10)
const field = 'h-10 w-full rounded-sm border border-navy/15 bg-white px-3 text-[14px] text-navy outline-none focus:border-navy'

function status(p) {
  const now = today()
  if (!p.active) return ['Paused', 'bg-sand text-navy']
  if (p.starts_on && p.starts_on > now) return ['Scheduled', 'bg-sky-100 text-sky-900']
  if (p.ends_on && p.ends_on < now) return ['Ended', 'bg-slate-200 text-slate-700']
  return ['Running', 'bg-emerald-100 text-emerald-900']
}

function PromotionForm({ initial, onDone }) {
  const t = useT()
  const [f, setF] = useState({ ...blank, ...initial, destinations: initial?.destinations || [], tours: initial?.tours || [], i18n: initial?.i18n || {} })
  const places = useFetch('/destinations/?all=1&raw=1', { list: true })
  const allTours = useFetch('/tours/?all=1&raw=1', { list: true })
  const [find, setFind] = useState('')
  const flip = (k, slug) => setF((p) => ({ ...p, [k]: p[k].includes(slug) ? p[k].filter((x) => x !== slug) : [...p[k], slug] }))
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setF((p) => ({ ...p, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }))
  const setLang = (code, k, v) => setF((p) => ({ ...p, i18n: { ...p.i18n, [code]: { ...(p.i18n[code] || {}), [k]: v } } }))

  async function save(e) {
    e.preventDefault(); setBusy(true); setError('')
    const i18n = Object.fromEntries(Object.entries(f.i18n).map(([c, v]) => [c, Object.fromEntries(Object.entries(v).filter(([, x]) => x))]).filter(([, v]) => Object.keys(v).length))
    const body = { title: f.title, message: f.message, percent: Number(f.percent), applies_to: f.applies_to, destinations: f.destinations, tours: f.tours, starts_on: f.starts_on || null, ends_on: f.ends_on || null, active: f.active, i18n }
    try { f.id ? await api.patch(`/promotions/${f.id}/`, body) : await api.post('/promotions/', body); onDone(true) } catch (ex) { setError(ex.message); setBusy(false) }
  }
  const sample = isLocal ? 2000000 : 289

  return (
    <form onSubmit={save} className="max-w-3xl space-y-5 rounded-md border border-navy/10 bg-white p-6">
      <h2 className="font-heading text-[28px]">{t(f.id ? 'Edit promotion' : 'New promotion')}</h2>
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="label sm:col-span-2">{t('Title')} <span className="text-destructive">*</span><input required className={`${field} mt-1`} value={f.title} onChange={set('title')} placeholder={t('Autumn sale — 20% off all tours')} />
          <span className="mt-1 block text-[12px] font-normal text-ink/80">{t('Shown in the banner at the top of the website.')}</span></label>
        <label className="label sm:col-span-2">{t('Message')}<input className={`${field} mt-1`} value={f.message} onChange={set('message')} placeholder={t('Prices already include the discount.')} /></label>
        <label className="label">{t('Discount (%)')} <span className="text-destructive">*</span><input required type="number" min="1" max="90" className={`${field} mt-1`} value={f.percent} onChange={set('percent')} />
          <span className="mt-1 block text-[12px] font-normal text-ink/80">{t('Example')}: {exactMoney(sample)} → {exactMoney(discounted(sample, f.percent))}</span></label>
        <label className="label">{t('Applies to')}<select className={`${field} mt-1`} value={f.applies_to} onChange={set('applies_to')}>{APPLIES.map(([k, l]) => <option key={k} value={k}>{t(l)}</option>)}</select></label>
        <label className="label">{t('Starts on')}<input type="date" className={`${field} mt-1`} value={f.starts_on || ''} onChange={set('starts_on')} /></label>
        <label className="label">{t('Ends on')}<input type="date" className={`${field} mt-1`} value={f.ends_on || ''} onChange={set('ends_on')} />
          <span className="mt-1 block text-[12px] font-normal text-ink/80">{t('Leave dates empty for no limit.')}</span></label>
        <label className="flex items-center gap-2 text-[14px] sm:col-span-2"><input type="checkbox" className="h-4 w-4" checked={f.active} onChange={set('active')} />{t('Active (tick to publish the offer)')}</label>
      </div>
      <fieldset className="rounded-sm border border-navy/10 p-4">
        <legend className="px-1 text-[14px] font-medium">{t('Limit the discount to (optional)')}</legend>
        <p className="text-[12.5px] text-ink">{t('Leave everything unticked to discount all matching prices. Tick destinations, tours or both to discount only those, for example only Samarkand, or only the plov class.')}</p>
        <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.16em] text-ink">{t('Destinations')}</p>
        <div className="mt-1.5 flex flex-wrap gap-2">{places.data.map((d) => (
          <label key={d.slug} className={`inline-flex cursor-pointer items-center gap-2 rounded-full border px-3 py-1.5 text-[13px] ${f.destinations.includes(d.slug) ? 'border-navy bg-navy text-ivory' : 'border-navy/15 bg-white'}`}>
            <input type="checkbox" className="sr-only" checked={f.destinations.includes(d.slug)} onChange={() => flip('destinations', d.slug)} />{d.name}</label>))}</div>
        <p className="mt-4 font-mono text-[10px] uppercase tracking-[0.16em] text-ink">{t('Tours')} · {t('{n} selected', { n: f.tours.length })}</p>
        <input className={`${field} mt-1.5`} placeholder={t('Search tours by title')} value={find} onChange={(e) => setFind(e.target.value)} />
        <div className="mt-2 max-h-56 overflow-y-auto rounded-sm border border-navy/10 bg-white">{allTours.data.filter((x) => x.title.toLowerCase().includes(find.toLowerCase())).map((x) => (
          <label key={x.slug} className="flex cursor-pointer items-center gap-2.5 border-b border-navy/5 px-3 py-1.5 text-[13.5px] last:border-0 hover:bg-sand-soft/60">
            <input type="checkbox" className="h-4 w-4" checked={f.tours.includes(x.slug)} onChange={() => flip('tours', x.slug)} /><span className="flex-1">{x.title}</span>
            <span className="text-[12px] text-ink">{x.destination_name}</span></label>))}</div>
      </fieldset>
      <details className="rounded-sm border border-navy/10 p-4">
        <summary className="cursor-pointer text-[14px] font-medium">{t('Translations of the banner')}</summary>
        <div className="mt-3 space-y-3">{LANGS.slice(1).map((l) => (
          <div key={l.code} className="grid gap-2 sm:grid-cols-[90px_1fr_1fr] sm:items-center"><span className="font-mono text-[12px] uppercase text-ink">{l.label}</span>
            <input aria-label={`${l.label} ${t('Title')}`} placeholder={t('Title')} className={field} value={f.i18n[l.code]?.title || ''} onChange={(e) => setLang(l.code, 'title', e.target.value)} />
            <input aria-label={`${l.label} ${t('Message')}`} placeholder={t('Message')} className={field} value={f.i18n[l.code]?.message || ''} onChange={(e) => setLang(l.code, 'message', e.target.value)} /></div>))}</div>
      </details>
      <p className="text-[13px] text-ink">{t('While an offer is running, matching prices show the old price crossed out and the new price. If a tour has its own discount too, the larger one applies.')}</p>
      {error && <p role="alert" className="text-[13px] text-destructive">{error}</p>}
      <div className="flex gap-3"><button className="btn-primary" disabled={busy}>{t(f.id ? 'Save changes' : 'Create')}</button><button type="button" className="btn-outline" onClick={() => onDone(false)}>{t('Cancel')}</button></div>
    </form>
  )
}

export default function Promotions() {
  const t = useT()
  const { data, loading, reload } = useFetch('/promotions/?raw=1', { list: true })
  const places = useFetch('/destinations/?all=1&raw=1', { list: true })
  const tourList = useFetch('/tours/?all=1&raw=1', { list: true })
  const [editing, setEditing] = useState(null)
  const done = (saved) => { setEditing(null); if (saved) reload() }
  const toggle = async (p) => { await api.patch(`/promotions/${p.id}/`, { active: !p.active }); reload() }
  const remove = async (p) => { if (window.confirm(t('Delete “{name}”? This cannot be undone.', { name: p.title }))) { await api.del(`/promotions/${p.id}/`); reload() } }

  if (editing) return <PromotionForm initial={editing === 'new' ? null : editing} onDone={done} />
  return (
    <div>
      <p className="max-w-3xl text-[14px] text-ink">{t('Announce a sale such as “20% off all tours”. Visitors see a banner, and every matching price shows the old price crossed out with the new one beside it. You can also give a single tour, hotel or transfer its own discount in its editor.')}</p>
      <button onClick={() => setEditing('new')} className="mt-4 inline-flex h-11 items-center gap-2 rounded-full bg-navy px-5 text-[14px] font-medium text-ivory hover:bg-navy-deep"><Plus className="h-4 w-4" />{t('New promotion')}</button>
      <div className="mt-5 space-y-3">
        {loading ? <Spinner /> : data.map((p) => {
          const [label, tone] = status(p)
          return (
            <article key={p.id} className="flex flex-wrap items-center justify-between gap-4 rounded-sm border border-navy/10 bg-white p-4">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2.5"><h3 className="text-[17px] font-medium">{p.title}</h3>
                  <span className="rounded-full bg-destructive px-2.5 py-0.5 font-mono text-[11px] text-white">−{p.percent}%</span>
                  <span className={`rounded-full px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-[0.1em] ${tone}`}>{t(label)}</span></div>
                {(p.destinations?.length > 0 || p.tours?.length > 0) && <p className="mt-1 text-[13px] text-navy">{t('Only')}: {[...(p.destinations || []).map((s) => places.data.find((d) => d.slug === s)?.name || s), ...(p.tours || []).map((s) => tourList.data.find((x) => x.slug === s)?.title || s)].join(', ')}</p>}
                <p className="mt-1 text-[13.5px] text-ink">{t(APPLIES.find(([k]) => k === p.applies_to)?.[1] || 'Everything')} · {p.starts_on || t('from now')} → {p.ends_on || t('no end date')}</p>
                {p.message && <p className="mt-0.5 text-[13px] text-ink">{p.message}</p>}
              </div>
              <div className="flex flex-wrap gap-2 text-[13px]">
                <button onClick={() => setEditing(p)} className="inline-flex h-9 items-center gap-1.5 rounded-full border border-navy/15 px-3.5 hover:bg-sand-soft"><Pencil className="h-3.5 w-3.5" />{t('Edit')}</button>
                <button onClick={() => toggle(p)} className="h-9 rounded-full border border-navy/15 px-3.5 hover:bg-sand-soft">{p.active ? t('Pause') : t('Activate')}</button>
                <button onClick={() => remove(p)} aria-label={t('Delete')} className="grid h-9 w-9 place-items-center rounded-full border border-red-200 text-destructive hover:bg-red-50"><Trash2 className="h-3.5 w-3.5" /></button>
              </div>
            </article>
          )
        })}
        {!loading && !data.length && <p className="rounded-sm border border-dashed border-navy/20 p-8 text-center text-ink">{t('No promotions yet.')}</p>}
      </div>
    </div>
  )
}
