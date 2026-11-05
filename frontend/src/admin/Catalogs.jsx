import { useMemo, useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { Archive, Copy, MapPin, Pencil, Plus, Search, Star, Trash2 } from 'lucide-react'
import { api } from '../api'
import { money, useFetch } from '../hooks'
import { useT } from '../i18n'
import { StatusPill } from '../pages/Auth'
import RecordEditor from './Editor'

function ActionButton({ icon: Icon, children, onClick, danger }) {
  return (
    <button onClick={onClick} className={`inline-flex h-9 items-center gap-1.5 rounded-full border px-3.5 text-[13px] transition-colors ${danger ? 'border-red-200 text-destructive hover:bg-red-50' : 'border-navy/15 text-navy hover:bg-sand-soft'}`}>
      {Icon && <Icon className="h-3.5 w-3.5" />}{children}
    </button>
  )
}

const useRecords = (resource) => useFetch(`/${resource}/?all=1&raw=1`, { list: true })

/* ---------- Tours & packages ---------- */
const TOUR_FILTERS = [['all', 'All tours'], ['published', 'Published'], ['draft', 'Drafts'], ['review', 'Awaiting review'], ['archived', 'Archived']]

export function AdminTours() {
  const t = useT()
  const { refreshStats } = useOutletContext()
  const { data, reload } = useRecords('tours')
  const [filter, setFilter] = useState('all')
  const [q, setQ] = useState('')
  const [editing, setEditing] = useState(null)

  const shown = useMemo(() => data.filter((x) => (filter === 'all' || x.status === filter) && x.title.toLowerCase().includes(q.toLowerCase())), [data, filter, q])
  const refresh = () => { reload(); refreshStats() }
  const patch = async (x, body) => { await api.patch(`/tours/${x.slug}/`, body); refresh() }
  const duplicate = async (x) => { await api.post(`/tours/${x.slug}/duplicate/`); refresh() }
  const remove = async (x) => { if (window.confirm(t('Delete “{name}”? This cannot be undone.', { name: x.title }))) { await api.del(`/tours/${x.slug}/`); refresh() } }

  if (editing) return <RecordEditor resource="tours" label="tour" record={editing === 'new' ? null : editing} onDone={(saved) => { setEditing(null); if (saved) refresh() }} />
  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">{TOUR_FILTERS.map(([k, l]) => (
          <button key={k} onClick={() => setFilter(k)} className={`h-10 rounded-full border px-4 text-[14px] ${filter === k ? 'border-navy bg-navy text-ivory' : 'border-navy/10 bg-white hover:bg-sand-soft'}`}>{t(l)}</button>))}</div>
        <button onClick={() => setEditing('new')} className="inline-flex h-11 items-center gap-2 rounded-full bg-navy px-5 text-[14px] font-medium text-ivory hover:bg-navy-deep"><Plus className="h-4 w-4" />{t('New tour')}</button>
      </div>
      <div className="mt-5 flex items-center gap-4">
        <div className="relative w-full max-w-md"><Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder={t('Search tours by title')} className="h-11 w-full rounded-sm border border-navy/10 bg-white pl-10 pr-3 text-[14px] outline-none focus:border-navy" /></div>
        <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-ink">{t('{n} tours', { n: shown.length })}</span>
      </div>
      <div className="mt-5 space-y-4">
        {shown.map((x) => (
          <article key={x.slug} className="flex gap-5 rounded-sm border border-navy/10 bg-white p-4">
            <img src={x.image_url} alt="" className="hidden h-[86px] w-[136px] shrink-0 rounded-sm bg-sand-soft object-cover sm:block" />
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2.5"><h3 className="text-[17px] font-medium">{x.title}</h3><StatusPill status={x.status} />
                {x.featured && <span className="inline-flex items-center gap-1 rounded-full border border-gold/50 bg-sand-soft px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-[0.1em]"><Star className="h-3 w-3 fill-gold text-gold" />{t('Featured')}</span>}</div>
              <p className="mt-1 text-[14px] text-ink">{x.destination_name} · {x.duration_label} · {money(x.price_from_usd)} {t('per person')}{x.discount_percent > 0 && <span className="ml-2 rounded-full bg-destructive px-2 py-0.5 font-mono text-[10px] text-white">−{x.discount_percent}%</span>}</p>
              <p className="mt-0.5 font-mono text-[12px] text-ink">/tours/{x.slug}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                <ActionButton icon={Pencil} onClick={() => setEditing(x)}>{t('Edit')}</ActionButton>
                <ActionButton onClick={() => patch(x, { status: x.status === 'published' ? 'draft' : 'published' })}>{x.status === 'published' ? t('Unpublish') : t('Publish')}</ActionButton>
                <ActionButton icon={Star} onClick={() => patch(x, { featured: !x.featured })}>{x.featured ? t('Unfeature') : t('Feature')}</ActionButton>
                {!x.parent_slug && <ActionButton icon={MapPin} onClick={() => patch(x, { multi_city: !x.multi_city })}>{x.multi_city ? t('Remove from Multi-city') : t('Add to Multi-city')}</ActionButton>}
                <ActionButton icon={Copy} onClick={() => duplicate(x)}>{t('Duplicate')}</ActionButton>
                {x.status !== 'archived' && <ActionButton icon={Archive} onClick={() => patch(x, { status: 'archived', featured: false })}>{t('Archive')}</ActionButton>}
                <ActionButton icon={Trash2} danger onClick={() => remove(x)}>{t('Delete')}</ActionButton>
              </div>
            </div>
          </article>
        ))}
        {!shown.length && <p className="rounded-sm border border-dashed border-navy/20 p-8 text-center text-ink">{t('No tours match this filter.')}</p>}
      </div>
    </div>
  )
}

/* ---------- Other listings ---------- */
const LISTINGS = [
  { key: 'destinations', tab: 'Destinations', one: 'destination', newLabel: 'New destination', title: 'name', sub: (r) => r.region },
  { key: 'hotels', tab: 'Hotels', one: 'hotel', newLabel: 'New hotel', title: 'name', sub: (r, t) => `${r.destination_name} · ${r.stars}★ · ${money(r.price_from_usd)} / ${t('night')}` },
  { key: 'food', tab: 'Experiences', one: 'experience', newLabel: 'New experience', title: 'name', sub: (r) => `${r.kind}${r.destination_name ? ` · ${r.destination_name}` : ''}` },
  { key: 'transport', tab: 'Transport', one: 'transport option', newLabel: 'New transport option', title: 'name', sub: (r, t) => `${r.vehicle} · ${t('from')} ${money(r.base_price_usd)}` },
]

function ListingTable({ cfg }) {
  const t = useT()
  const { refreshStats } = useOutletContext()
  const { data, reload } = useRecords(cfg.key)
  const [q, setQ] = useState('')
  const [editing, setEditing] = useState(null)
  const shown = data.filter((r) => r[cfg.title].toLowerCase().includes(q.toLowerCase()))
  const refresh = () => { reload(); refreshStats() }
  const toggle = async (r) => { await api.patch(`/${cfg.key}/${r.slug}/`, { status: r.status === 'published' ? 'draft' : 'published' }); refresh() }
  const remove = async (r) => { if (window.confirm(t('Delete “{name}”? This cannot be undone.', { name: r[cfg.title] }))) { await api.del(`/${cfg.key}/${r.slug}/`); refresh() } }

  if (editing) return <RecordEditor key={cfg.key} resource={cfg.key} label={cfg.one} record={editing === 'new' ? null : editing} onDone={(saved) => { setEditing(null); if (saved) refresh() }} />
  return (
    <div>
      <div className="flex flex-wrap items-center gap-4">
        <div className="relative w-full max-w-sm"><Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder={`${t('Search')} ${t(cfg.tab).toLowerCase()}`} className="h-11 w-full rounded-sm border border-navy/10 bg-white pl-10 pr-3 text-[14px] outline-none focus:border-navy" /></div>
        <button onClick={() => setEditing('new')} className="inline-flex h-11 items-center gap-2 rounded-full bg-navy px-5 text-[14px] font-medium text-ivory hover:bg-navy-deep"><Plus className="h-4 w-4" />{t(cfg.newLabel)}</button>
        <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-ink">{t('{n} records', { n: shown.length })}</span>
      </div>
      <div className="mt-5 overflow-hidden rounded-sm border border-navy/10 bg-white">
        <div className="grid grid-cols-[1fr_auto_auto] gap-4 border-b border-navy/10 px-5 py-3 font-mono text-[10px] uppercase tracking-[0.18em] text-ink sm:grid-cols-[1fr_200px_260px]"><span>{t('Name')}</span><span>{t('Status')}</span><span className="text-right">{t('Actions')}</span></div>
        {shown.map((r) => (
          <div key={r.slug} className="grid grid-cols-[1fr_auto_auto] items-center gap-4 border-b border-navy/10 px-5 py-4 last:border-0 sm:grid-cols-[1fr_200px_260px]">
            <div className="min-w-0"><p className="truncate text-[15px] font-medium">{r[cfg.title]}</p><p className="truncate text-[13px] text-ink">{cfg.sub(r, t)}</p></div>
            <div><StatusPill status={r.status} /></div>
            <div className="flex justify-end gap-2"><ActionButton icon={Pencil} onClick={() => setEditing(r)}>{t('Edit')}</ActionButton>
              <ActionButton onClick={() => toggle(r)}>{r.status === 'published' ? t('Unpublish') : t('Publish')}</ActionButton>
              <button onClick={() => remove(r)} aria-label={t('Delete')} className="grid h-9 w-9 place-items-center rounded-full border border-red-200 text-destructive hover:bg-red-50"><Trash2 className="h-3.5 w-3.5" /></button></div>
          </div>
        ))}
        {!shown.length && <p className="p-8 text-center text-ink">{t('Nothing here yet')}</p>}
      </div>
    </div>
  )
}

export function AdminListings() {
  const t = useT()
  const [tab, setTab] = useState(LISTINGS[0].key)
  const cfg = LISTINGS.find((l) => l.key === tab)
  return (
    <div>
      <div className="flex flex-wrap gap-2">{LISTINGS.map((l) => (
        <button key={l.key} onClick={() => setTab(l.key)} className={`h-10 rounded-full border px-5 text-[14px] ${tab === l.key ? 'border-navy bg-navy text-ivory' : 'border-navy/10 bg-white hover:bg-sand-soft'}`}>{t(l.tab)}</button>))}</div>
      <p className="mt-4 text-[14px] text-ink">{t('Tours are managed in “Tours & packages”. Destinations, hotels, experiences and transport can be created, translated into six languages, published or hidden here.')}</p>
      <div className="mt-5"><ListingTable key={tab} cfg={cfg} /></div>
    </div>
  )
}
