import { useState } from 'react'
import { Link, useNavigate, useOutletContext } from 'react-router-dom'
import { ArrowRight, Building2, CalendarDays, CircleDollarSign, Compass, Layers, Mail, Users } from 'lucide-react'
import { api } from '../api'
import { money, useFetch } from '../hooks'
import { useT } from '../i18n'
import { Spinner } from '../components/ui'
import { StatusPill, cap } from '../pages/Auth'

function StatCard({ icon: Icon, value, label, note, to }) {
  const body = (
    <div className="h-full rounded-sm border border-navy/10 bg-white p-5 transition-colors hover:bg-sand-soft/40">
      <Icon className="h-[18px] w-[18px] text-turquoise-deep" strokeWidth={1.7} />
      <p className="mt-4 font-heading text-[34px] leading-none">{value}</p>
      <p className="mt-2 text-[15px] font-medium">{label}</p>
      <p className="mt-1 text-[13px] text-ink">{note}</p>
    </div>
  )
  return to ? <Link to={to}>{body}</Link> : body
}

export function Overview() {
  const t = useT()
  const { stats } = useOutletContext()
  if (!stats) return <Spinner />
  const count = (n, one, many) => t(n === 1 ? one : many, { n })
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        <StatCard icon={CalendarDays} to="/admin/bookings" value={stats.pending} label={t('Pending requests')} note={count(stats.total_bookings, '{n} request in total', '{n} requests in total')} />
        <StatCard icon={CircleDollarSign} to="/admin/bookings" value={money(stats.confirmed_value)} label={t('Confirmed value')} note={count(stats.confirmed, '{n} confirmed request', '{n} confirmed requests')} />
        <StatCard icon={Compass} to="/admin/tours" value={stats.tours_live} label={t('Tours live')} note={count(stats.tours_unpublished, '{n} draft not published', '{n} drafts not published')} />
        <StatCard icon={Layers} to="/admin/listings" value={stats.published_listings} label={t('Published listings')} note={t('Tours, hotels, experiences, transport')} />
        <StatCard icon={Users} to="/admin/customers" value={stats.customers} label={t('Registered customers')} note={t('Accounts that can sign in')} />
        <StatCard icon={Mail} to="/admin/enquiries" value={stats.new_messages} label={t('New enquiries')} note={t('Contact messages not yet handled')} />
        <StatCard icon={Building2} to="/admin/partners" value={stats.pending_partners} label={t('Partners awaiting review')} note={t('Approve or reject individually')} />
      </div>
      <div className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-sm border border-navy/10 bg-white">
          <header className="flex items-center justify-between border-b border-navy/10 px-5 py-4"><h2 className="font-heading text-[24px]">{t('Latest requests')}</h2><Link to="/admin/bookings" className="text-[14px] text-turquoise-deep">{t('Open bookings')}</Link></header>
          <ul className="divide-y divide-navy/10">
            {stats.latest.map((b) => (
              <li key={b.id} className="flex items-center justify-between gap-3 px-5 py-4">
                <div className="min-w-0"><p className="truncate text-[15px] font-medium">{b.service_title}</p><p className="truncate text-[13px] text-ink">{b.reference} · {b.full_name} · {b.travel_date || t('date TBC')}</p></div>
                <div className="flex shrink-0 items-center gap-3">{Number(b.estimated_total_usd) > 0 && <span className="text-[14px]">{money(b.estimated_total_usd)}</span>}<StatusPill status={b.status} /></div>
              </li>
            ))}
            {!stats.latest.length && <li className="px-5 py-8 text-[14px] text-ink">{t('No requests yet.')}</li>}
          </ul>
        </section>
        <section className="rounded-sm border border-navy/10 bg-white">
          <header className="flex items-center justify-between border-b border-navy/10 px-5 py-4"><h2 className="font-heading text-[24px]">{t('Next departures')}</h2><Link to="/admin/bookings" className="inline-flex items-center gap-1 text-[14px] text-turquoise-deep">{t('Open bookings')}<ArrowRight className="h-3.5 w-3.5" /></Link></header>
          <ul className="divide-y divide-navy/10">
            {stats.upcoming.map((b) => (
              <li key={b.id} className="flex items-center justify-between gap-3 px-5 py-4">
                <div className="min-w-0"><p className="truncate text-[15px] font-medium">{b.service_title}</p><p className="text-[13px] text-ink">{b.full_name} · {b.guests} {t('Guests')}</p></div>
                <div className="shrink-0 text-right"><p className="font-mono text-[13px]">{b.travel_date}</p><StatusPill status={b.status} /></div>
              </li>
            ))}
            {!stats.upcoming.length && <li className="px-5 py-8 text-[15px] text-ink">{t('No trips are booked for today onward yet.')}</li>}
          </ul>
        </section>
      </div>
      <p className="rounded-sm border border-navy/10 bg-white p-5 text-[14px]"><span className="mb-2 block font-mono text-[10px] uppercase tracking-[0.2em] text-ink">{t('Reminder')}</span>
        {t('Nothing on this site takes payment. Confirming a request in this dashboard changes its status and makes it visible to the traveller, but you still have to write to them with the final price and terms.')}</p>
    </div>
  )
}

const BOOKING_STATUSES = ['pending', 'confirmed', 'completed', 'cancelled']

export function Bookings() {
  const t = useT()
  const { refreshStats } = useOutletContext()
  const nav = useNavigate()
  const { data, reload } = useFetch('/bookings/', { list: true })
  const [filter, setFilter] = useState('all')
  const [open, setOpen] = useState(null)
  const [notes, setNotes] = useState({})
  const shown = filter === 'all' ? data : data.filter((b) => b.status === filter)
  const update = async (b, body) => { await api.patch(`/bookings/${b.id}/update_status/`, body); reload(); refreshStats() }
  return (
    <div>
      <div className="flex flex-wrap gap-2">{['all', ...BOOKING_STATUSES].map((s) => (
        <button key={s} onClick={() => setFilter(s)} className={`h-10 rounded-full border px-4 text-[14px] ${filter === s ? 'border-navy bg-navy text-ivory' : 'border-navy/10 bg-white hover:bg-sand-soft'}`}>{t(cap(s))}</button>))}</div>
      <div className="mt-5 divide-y divide-navy/10 rounded-sm border border-navy/10 bg-white">
        {shown.map((b) => (
          <div key={b.id} className="p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <button onClick={() => setOpen(open === b.id ? null : b.id)} className="min-w-0 text-left">
                <p className="text-[16px] font-medium">{b.service_title}</p>
                <p className="text-[13px] text-ink"><span className="font-mono">{b.reference}</span> · {b.full_name} · {b.travel_date || t('date TBC')} · {b.guests} {t('Guests')}{Number(b.estimated_total_usd) > 0 && ` · ${t('est.')} ${money(b.estimated_total_usd)}`}</p>
              </button>
              <select value={b.status} onChange={(e) => update(b, { status: e.target.value })} className="h-10 rounded-full border border-navy/15 bg-white px-3 text-[14px]">{BOOKING_STATUSES.map((s) => <option key={s} value={s}>{t(cap(s))}</option>)}</select>
            </div>
            {open === b.id && (
              <div className="mt-4 grid gap-4 rounded-sm bg-sand-soft/50 p-4 text-[14px] md:grid-cols-2">
                <div className="space-y-1"><p><a className="text-turquoise-deep" href={`mailto:${b.email}`}>{b.email}</a> · <a className="text-turquoise-deep" href={`tel:${b.phone}`}>{b.phone}</a></p>
                  {b.details_summary && <p className="text-ink">{b.details_summary}</p>}{b.special_requests && <p className="whitespace-pre-wrap text-ink">{b.special_requests}</p>}</div>
                <div><label className="label">{t('Internal notes')}<textarea rows={3} className="input" value={notes[b.id] ?? b.admin_notes} onChange={(e) => setNotes({ ...notes, [b.id]: e.target.value })} /></label>
                  <button className="btn-outline mt-2 !h-9" onClick={() => update(b, { admin_notes: notes[b.id] ?? b.admin_notes })}>{t('Save notes')}</button>
                  {b.status === 'completed' && <button className="btn-primary mt-2 ml-2 !h-9" onClick={() => nav('/admin/accounting')}>{t('Open in Accounting')}</button>}</div>
              </div>
            )}
          </div>
        ))}
        {!shown.length && <p className="p-8 text-center text-ink">{t('No booking requests here.')}</p>}
      </div>
    </div>
  )
}

export function Customers() {
  const t = useT()
  const { data } = useFetch('/customers/', { list: true })
  return (
    <div className="divide-y divide-navy/10 rounded-sm border border-navy/10 bg-white">
      {data.map((u) => (
        <div key={u.id} className="flex flex-wrap items-center justify-between gap-2 px-5 py-4 text-[15px]">
          <span><span className="font-medium">{[u.first_name, u.last_name].join(' ').trim() || '—'}</span> <span className="text-ink">· {u.email}</span></span>
          <span className="text-[13px] text-ink">{u.is_staff ? `${t('Admin')} · ` : ''}{t('joined')} {new Date(u.date_joined).toLocaleDateString()}</span>
        </div>
      ))}
    </div>
  )
}

export function Partners() {
  const t = useT()
  const { refreshStats } = useOutletContext()
  const { data, reload } = useFetch('/partners/', { list: true })
  const review = async (p, status) => { await api.patch(`/partners/${p.id}/review/`, { status }); reload(); refreshStats() }
  return (
    <div className="space-y-3">
      {data.map((p) => (
        <div key={p.id} className="flex flex-wrap items-center justify-between gap-3 rounded-sm border border-navy/10 bg-white p-5">
          <div><p className="text-[16px] font-medium">{p.business_name} <span className="font-normal text-ink">· {t(p.partner_type)}{p.city && ` · ${p.city}`}</span></p>
            <p className="text-[13px] text-ink">{p.contact_name} · {p.email} · {p.phone}</p>{p.description && <p className="mt-1 text-[14px] text-ink">{p.description}</p>}</div>
          <div className="flex items-center gap-2"><StatusPill status={p.status} />
            {p.status !== 'approved' && <button className="btn-outline !h-9 !px-4" onClick={() => review(p, 'approved')}>{t('Approve')}</button>}
            {p.status !== 'rejected' && <button className="h-9 rounded-full border border-red-200 px-4 text-[13px] text-destructive hover:bg-red-50" onClick={() => review(p, 'rejected')}>{t('Reject')}</button>}</div>
        </div>
      ))}
      {!data.length && <p className="rounded-sm border border-dashed border-navy/20 p-8 text-center text-ink">{t('No partner applications yet.')}</p>}
    </div>
  )
}

export function Enquiries() {
  const t = useT()
  const { refreshStats } = useOutletContext()
  const { data, reload } = useFetch('/messages/', { list: true })
  const set = async (m, status) => { await api.patch(`/messages/${m.id}/`, { status }); reload(); refreshStats() }
  return (
    <div className="space-y-3">
      {data.map((m) => (
        <div key={m.id} className="rounded-sm border border-navy/10 bg-white p-5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-[16px] font-medium">{m.subject || t('(no subject)')} <span className="font-normal text-ink">— {m.full_name}</span></p>
            <select value={m.status} onChange={(e) => set(m, e.target.value)} className="h-10 rounded-full border border-navy/15 bg-white px-3 text-[14px]">{['new', 'read', 'replied'].map((s) => <option key={s} value={s}>{t(cap(s))}</option>)}</select>
          </div>
          <p className="text-[13px] text-ink"><a className="text-turquoise-deep" href={`mailto:${m.email}`}>{m.email}</a>{m.phone && ` · ${m.phone}`} · {new Date(m.created).toLocaleString()}</p>
          <p className="mt-3 whitespace-pre-wrap text-[15px]">{m.message}</p>
        </div>
      ))}
      {!data.length && <p className="rounded-sm border border-dashed border-navy/20 p-8 text-center text-ink">{t('No enquiries yet.')}</p>}
    </div>
  )
}

const SETTING_FIELDS = [
  ['email', 'Email'], ['phone_primary', 'Primary phone'], ['phone_secondary', 'Secondary phone'], ['address', 'Address'], ['hours', 'Opening hours'],
  ['instagram_url', 'Instagram URL'], ['telegram_url', 'Telegram URL'], ['facebook_url', 'Facebook URL'], ['youtube_url', 'YouTube URL'],
  ['analytics_id', 'Google Analytics ID (optional)'],
]

export function Settings() {
  const t = useT()
  const { data } = useFetch('/site-content/')
  const [form, setForm] = useState(null)
  const [saved, setSaved] = useState(false)
  const current = form || data
  if (!current) return <Spinner />
  const save = async (e) => { e.preventDefault(); await api.put('/site-content/', current); setSaved(true) }
  return (
    <form onSubmit={save} className="max-w-3xl rounded-sm border border-navy/10 bg-white p-6">
      <p className="mb-5 text-[14px] text-ink">{t('These contact details appear in the header menu, footer and contact page. Leave a field empty to hide it.')}</p>
      <div className="grid gap-4 sm:grid-cols-2">
        {SETTING_FIELDS.map(([k, label]) => <label key={k} className="label">{t(label)}<input className="input" value={current[k] || ''} onChange={(e) => { setSaved(false); setForm({ ...current, [k]: e.target.value }) }} /></label>)}
      </div>
      <div className="mt-6 flex items-center gap-3"><button className="btn-primary">{t('Save settings')}</button>{saved && <span className="text-[14px] text-turquoise-deep">{t('Saved')}</span>}</div>
    </form>
  )
}
