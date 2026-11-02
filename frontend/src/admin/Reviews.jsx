import { useState } from 'react'
import { BadgeCheck, Check, EyeOff, Star, Trash2 } from 'lucide-react'
import { useOutletContext } from 'react-router-dom'
import { api } from '../api'
import { useFetch } from '../hooks'
import { useT } from '../i18n'

const FILTERS = [['pending', 'Awaiting review'], ['published', 'Published'], ['hidden', 'Hidden'], ['all', 'All']]

export default function Reviews() {
  const t = useT()
  const { refreshStats } = useOutletContext()
  const { data, reload } = useFetch('/reviews/?all=1', { list: true })
  const [filter, setFilter] = useState('pending')
  const shown = data.filter((r) => filter === 'all' || r.status === filter)
  const set = async (r, status) => { await api.patch(`/reviews/${r.id}/`, { status }); reload(); refreshStats?.() }
  const remove = async (r) => { if (window.confirm(t('Delete this review? This cannot be undone.'))) { await api.del(`/reviews/${r.id}/`); reload(); refreshStats?.() } }
  return (
    <div>
      <p className="max-w-3xl text-[14px] text-ink">{t('Visitors send reviews from a tour page. Nothing appears on the website until you publish it. A “Verified traveller” mark is added when the booking reference and email match a confirmed or completed booking. Published reviews also update the tour’s star rating.')}</p>
      <div className="mt-5 flex flex-wrap gap-2">{FILTERS.map(([k, l]) => (
        <button key={k} onClick={() => setFilter(k)} className={`h-10 rounded-full border px-4 text-[14px] ${filter === k ? 'border-navy bg-navy text-ivory' : 'border-navy/10 bg-white hover:bg-sand-soft'}`}>{t(l)} ({k === 'all' ? data.length : data.filter((r) => r.status === k).length})</button>))}</div>
      <div className="mt-5 space-y-4">
        {shown.map((r) => (
          <article key={r.id} className="rounded-sm border border-navy/10 bg-white p-5">
            <div className="flex flex-wrap items-center gap-3">
              <span className="inline-flex">{[1, 2, 3, 4, 5].map((i) => <Star key={i} className={`h-4 w-4 ${i <= r.rating ? 'fill-gold text-gold' : 'text-navy/20'}`} />)}</span>
              <span className="font-medium text-navy">{r.name}{r.country ? `, ${r.country}` : ''}</span>
              {r.verified && <span className="inline-flex items-center gap-1 text-[12px] text-turquoise-deep"><BadgeCheck className="h-3.5 w-3.5" />{t('Verified traveller')}</span>}
              <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-ink">{t(FILTERS.find(([k]) => k === r.status)?.[1] || r.status)}</span>
            </div>
            <p className="mt-1 text-[13px] text-ink">{r.tour_title || r.tour_slug} · {new Date(r.created).toLocaleDateString()}{r.reference ? ` · ${r.reference}` : ''}{r.email ? ` · ${r.email}` : ''}</p>
            <p className="mt-3 text-[15px] leading-relaxed text-navy">{r.text}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {r.status !== 'published' && <button onClick={() => set(r, 'published')} className="inline-flex h-9 items-center gap-1.5 rounded-full bg-navy px-4 text-[13px] text-ivory hover:bg-navy-deep"><Check className="h-3.5 w-3.5" />{t('Publish')}</button>}
              {r.status !== 'hidden' && <button onClick={() => set(r, 'hidden')} className="inline-flex h-9 items-center gap-1.5 rounded-full border border-navy/15 px-4 text-[13px] text-navy hover:bg-sand-soft"><EyeOff className="h-3.5 w-3.5" />{t('Hide')}</button>}
              <button onClick={() => remove(r)} className="inline-flex h-9 items-center gap-1.5 rounded-full border border-red-200 px-4 text-[13px] text-destructive hover:bg-red-50"><Trash2 className="h-3.5 w-3.5" />{t('Delete')}</button>
            </div>
          </article>
        ))}
        {!shown.length && <p className="rounded-sm border border-dashed border-navy/20 p-8 text-center text-ink">{t('No reviews here yet.')}</p>}
      </div>
    </div>
  )
}
