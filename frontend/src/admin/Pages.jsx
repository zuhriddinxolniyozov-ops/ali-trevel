import { useState } from 'react'
import { Link, useNavigate, useOutletContext } from 'react-router-dom'
import { ArrowRight, Building2, CalendarDays, CheckCheck, CircleDollarSign, Compass, Eye, Layers, Mail, MessageCircle, Plus, Send, Trash2, Users } from 'lucide-react'
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
        <section className="min-w-0 rounded-sm border border-navy/10 bg-white">
          <header className="flex items-center justify-between border-b border-navy/10 px-5 py-4"><h2 className="font-heading text-[24px]">{t('Latest requests')}</h2><Link to="/admin/bookings" className="text-[14px] text-turquoise-deep">{t('Open bookings')}</Link></header>
          <ul className="divide-y divide-navy/10">
            {stats.latest.map((b) => (
              <li key={b.id} className="flex items-center justify-between gap-3 px-5 py-4">
                <div className="min-w-0"><p className="truncate text-[15px] font-medium">{b.service_title_local || b.service_title}</p><p className="truncate text-[13px] text-ink">{b.reference} · {b.full_name} · {b.travel_date || t('date TBC')}</p></div>
                <div className="flex shrink-0 items-center gap-3">{Number(b.estimated_total_usd) > 0 && <span className="text-[14px]">{money(b.estimated_total_usd)}</span>}<StatusPill status={b.status} /></div>
              </li>
            ))}
            {!stats.latest.length && <li className="px-5 py-8 text-[14px] text-ink">{t('No requests yet.')}</li>}
          </ul>
        </section>
        <section className="min-w-0 rounded-sm border border-navy/10 bg-white">
          <header className="flex items-center justify-between border-b border-navy/10 px-5 py-4"><h2 className="font-heading text-[24px]">{t('Next departures')}</h2><Link to="/admin/bookings" className="inline-flex items-center gap-1 text-[14px] text-turquoise-deep">{t('Open bookings')}<ArrowRight className="h-3.5 w-3.5" /></Link></header>
          <ul className="divide-y divide-navy/10">
            {stats.upcoming.map((b) => (
              <li key={b.id} className="flex items-center justify-between gap-3 px-5 py-4">
                <div className="min-w-0"><p className="truncate text-[15px] font-medium">{b.service_title_local || b.service_title}</p><p className="text-[13px] text-ink">{b.full_name} · {b.guests} {t('Guests')}</p></div>
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
                <p className="text-[16px] font-medium">{b.service_title_local || b.service_title}</p>
                <p className="text-[13px] text-ink"><span className="font-mono">{b.reference}</span> · {b.full_name} · {b.travel_date || t('date TBC')} · {b.guests} {t('Guests')}{Number(b.estimated_total_usd) > 0 && ` · ${t('est.')} ${money(b.estimated_total_usd)}`}</p>
              </button>
              <select value={b.status} onChange={(e) => update(b, { status: e.target.value })} className="h-10 rounded-full border border-navy/15 bg-white px-3 text-[14px]">{BOOKING_STATUSES.map((s) => <option key={s} value={s}>{t(cap(s))}</option>)}</select>
            </div>
            {open === b.id && (
              <div className="mt-4 grid gap-4 rounded-sm bg-sand-soft/50 p-4 text-[14px] md:grid-cols-2">
                <div className="space-y-1"><p><a className="text-turquoise-deep" href={`mailto:${b.email}`}>{b.email}</a> · <a className="text-turquoise-deep" href={`tel:${b.phone}`}>{b.phone}</a></p>
                  {(b.arrival_date || b.arrival_note) && <p className="font-medium text-navy">✈ {t('Arrives at Samarkand airport')}: {[b.arrival_date, b.arrival_time?.slice(0, 5), b.arrival_flight, b.arrival_note].filter(Boolean).join(' · ')}</p>}{b.details_summary && <p className="text-ink">{b.details_summary}</p>}{b.special_requests && <p className="whitespace-pre-wrap text-ink">{b.special_requests}</p>}</div>
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

const KINDS = [['all', 'All'], ['account', 'Website accounts'], ['guest', 'Guests (no account)'], ['telegram', 'Telegram bot']]
const KIND_TONE = { account: 'bg-navy/10 text-navy', guest: 'bg-sand text-navy', telegram: 'bg-sky-100 text-sky-900' }

export function Customers() {
  const t = useT()
  const { data, loading } = useFetch('/customers/', { list: true })
  const [kind, setKind] = useState('all')
  const [q, setQ] = useState('')
  const [open, setOpen] = useState(null)
  const counts = KINDS.reduce((o, [k]) => ({ ...o, [k]: k === 'all' ? data.length : data.filter((p) => p.kind === k).length }), {})
  const needle = q.trim().toLowerCase()
  const shown = data.filter((p) => (kind === 'all' || p.kind === kind) && (!needle || [p.name, p.email, p.phone, p.username].some((v) => String(v || '').toLowerCase().includes(needle))))
  return (
    <div>
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex flex-wrap gap-2">{KINDS.map(([k, label]) => (
          <button key={k} onClick={() => setKind(k)} className={`h-10 rounded-full border px-4 text-[14px] ${kind === k ? 'border-navy bg-navy text-ivory' : 'border-navy/10 bg-white hover:bg-sand-soft'}`}>{t(label)} <span className="ml-1 font-mono text-[12px] opacity-70">{counts[k]}</span></button>))}</div>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder={t('Search name, email, phone or @username')} className="h-10 w-full max-w-sm rounded-sm border border-navy/10 bg-white px-3 text-[14px] outline-none focus:border-navy" />
      </div>
      <div className="mt-4 divide-y divide-navy/10 rounded-sm border border-navy/10 bg-white">
        {shown.map((p) => (
          <div key={p.key}>
            <button onClick={() => setOpen(open === p.key ? null : p.key)} className="flex w-full flex-wrap items-center justify-between gap-2 px-5 py-4 text-left text-[15px] hover:bg-sand-soft/40">
              <span className="min-w-0">
                <span className="font-medium">{p.name || '—'}</span>
                <span className={`ml-2 rounded-full px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-[0.08em] ${KIND_TONE[p.kind]}`}>{p.kind === 'telegram' ? 'Telegram' : t(KINDS.find(([k]) => k === p.kind)[1])}</span>
                {p.is_staff && <span className="ml-1 rounded-full bg-gold/30 px-2 py-0.5 font-mono text-[10px] uppercase text-navy">{t('Admin')}</span>}
                <span className="block truncate text-[13px] text-ink">{[p.username && `@${p.username}`, p.email, p.phone].filter(Boolean).join(' · ') || '—'}{p.lang && ` · ${p.lang.toUpperCase()}`}</span>
              </span>
              <span className="text-right text-[13px] text-ink">
                <span className="block"><span className="font-mono text-navy">{p.bookings}</span> {t('bookings')}{p.total_usd > 0 && <> · <span className="font-mono text-navy">{money(p.total_usd)}</span></>}</span>
                <span className="block">{p.last_booking_at ? `${t('Last booking')} ${new Date(p.last_booking_at).toLocaleDateString()}` : `${t('joined')} ${new Date(p.joined).toLocaleDateString()}`}</span>
              </span>
            </button>
            {open === p.key && (
              <div className="space-y-2 bg-sand-soft/40 px-5 py-4 text-[14px]">
                {p.kind === 'telegram' && <p className="text-ink"><Send className="mr-1 inline h-4 w-4 text-sky-700" />{t('Booked and chatted in the Telegram bot')}{p.username && <> · <a className="text-turquoise-deep" href={`https://t.me/${p.username}`} target="_blank" rel="noopener noreferrer">@{p.username}</a></>} · chat {p.chat_id}</p>}
                {p.recent_bookings.map((b) => (
                  <p key={b.reference} className="flex flex-wrap items-center gap-x-3 gap-y-1">
                    <span className="font-mono text-[12.5px]">{b.reference}</span><span className="font-medium">{b.service_title_local || b.service_title}</span>
                    <span className="text-ink">{b.travel_date || t('date TBC')} · {b.guests} {t('Guests')}</span><StatusPill status={b.status} />
                    {b.arrival && <span className="text-ink">✈ {b.arrival}</span>}
                  </p>
                ))}
                {!p.recent_bookings.length && <p className="text-ink">{t('No bookings yet.')}</p>}
              </div>
            )}
          </div>
        ))}
        {!loading && !shown.length && <p className="p-8 text-center text-ink">{t('No customers here yet.')}</p>}
      </div>
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

const ENQUIRY_STATES = [['new', 'New'], ['read', 'Read'], ['replied', 'Replied']]

export function Enquiries() {
  const t = useT()
  const { refreshStats } = useOutletContext()
  const { data, reload } = useFetch('/messages/', { list: true })
  const [filter, setFilter] = useState('all')
  const [error, setError] = useState('')
  const set = async (m, status) => {
    setError('')
    try { await api.patch(`/messages/${m.id}/`, { status }); reload(); refreshStats() } catch (ex) { setError(ex.message) }
  }
  const shown = filter === 'all' ? data : data.filter((m) => m.status === filter)
  const count = (k) => (k === 'all' ? data.length : data.filter((m) => m.status === k).length)
  return (
    <div>
      <div className="flex flex-wrap gap-2">{[['all', 'All'], ...ENQUIRY_STATES].map(([k, label]) => (
        <button key={k} onClick={() => setFilter(k)} className={`h-10 rounded-full border px-4 text-[14px] ${filter === k ? 'border-navy bg-navy text-ivory' : 'border-navy/10 bg-white hover:bg-sand-soft'}`}>{t(label)} <span className="ml-1 font-mono text-[12px] opacity-70">{count(k)}</span></button>))}</div>
      {error && <p role="alert" className="mt-3 text-[13px] text-destructive">{error}</p>}
      <div className="mt-4 space-y-3">
        {shown.map((m) => {
          const telegram = m.email.endsWith('.invalid')
          return (
            <div key={m.id} className={`rounded-sm border bg-white p-5 ${m.status === 'new' ? 'border-turquoise-deep/50 shadow-[inset_4px_0_0_0] shadow-turquoise-deep' : 'border-navy/10'}`}>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-[16px] font-medium">{m.subject || t('(no subject)')} <span className="font-normal text-ink">— {m.full_name}</span></p>
                <StatusPill status={m.status} />
              </div>
              <p className="text-[13px] text-ink">{telegram ? <span className="inline-flex items-center gap-1 text-sky-800"><Send className="h-3.5 w-3.5" />{t('Sent from the Telegram bot')}</span> : <a className="text-turquoise-deep" href={`mailto:${m.email}`}>{m.email}</a>}{m.phone && ` · ${m.phone}`} · {new Date(m.created).toLocaleString()}</p>
              <p className="mt-3 whitespace-pre-wrap text-[15px]">{m.message}</p>
              <div className="mt-4 flex flex-wrap items-center gap-2">
                {m.status === 'new' && <button className="btn-outline !h-9" onClick={() => set(m, 'read')}><Eye className="h-4 w-4" />{t('Mark as read')}</button>}
                {m.status !== 'replied' && <button className="btn-primary !h-9" onClick={() => set(m, 'replied')}><CheckCheck className="h-4 w-4" />{t('Mark as replied')}</button>}
                {m.status !== 'new' && <button className="h-9 rounded-full border border-navy/15 px-4 text-[13px] text-navy hover:bg-sand-soft" onClick={() => set(m, 'new')}>{t('Mark as new')}</button>}
                {!telegram && <a className="inline-flex h-9 items-center gap-1.5 rounded-full border border-navy/15 px-4 text-[13px] text-navy hover:bg-sand-soft" href={`mailto:${m.email}?subject=${encodeURIComponent(`Re: ${m.subject || 'ALI TRAVEL'}`)}`} onClick={() => m.status === 'new' && set(m, 'read')}><MessageCircle className="h-4 w-4" />{t('Reply by email')}</a>}
              </div>
            </div>
          )
        })}
        {!shown.length && <p className="rounded-sm border border-dashed border-navy/20 p-8 text-center text-ink">{t('No enquiries yet.')}</p>}
      </div>
    </div>
  )
}

const SETTING_FIELDS = [
  ['email', 'Email'], ['phone_primary', 'Primary phone'], ['phone_secondary', 'Secondary phone'], ['address', 'Address'], ['hours', 'Opening hours'],
  ['instagram_url', 'Instagram URL'], ['telegram_url', 'Telegram URL'], ['facebook_url', 'Facebook URL'], ['youtube_url', 'YouTube URL'], ['x_url', 'X (Twitter) URL'],
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
      <fieldset className="mt-8 rounded-sm border border-navy/12 p-4">
        <legend className="px-1 font-mono text-[10px] uppercase tracking-[0.16em] text-ink">{t('More contact lines')}</legend>
        <p className="text-[13px] text-ink">{t('Add any extra line you like (WhatsApp, a second office, a licence number…). It appears under the contact details in the footer and on the contact page.')}</p>
        <div className="mt-3 space-y-3">
          {(current.extra_contacts || []).map((r, i) => {
            const change = (k) => (e) => { setSaved(false); setForm({ ...current, extra_contacts: current.extra_contacts.map((x, j) => (j === i ? { ...x, [k]: e.target.value } : x)) }) }
            return (
              <div key={i} className="grid gap-2 rounded-sm bg-sand-soft/50 p-3 sm:grid-cols-[1fr_1.4fr_1.4fr_auto]">
                <label className="label">{t('Name')}<input className="input" maxLength={60} placeholder="WhatsApp" value={r.label || ''} onChange={change('label')} /></label>
                <label className="label">{t('Text shown')}<input className="input" maxLength={200} placeholder="+998 90 123 45 67" value={r.value || ''} onChange={change('value')} /></label>
                <label className="label">{t('Link (optional)')}<input className="input" maxLength={300} placeholder="https://wa.me/998901234567" value={r.url || ''} onChange={change('url')} /></label>
                <button type="button" aria-label={t('Remove this line')} className="mt-6 h-10 rounded-full border border-red-200 px-3 text-destructive hover:bg-red-50" onClick={() => { setSaved(false); setForm({ ...current, extra_contacts: current.extra_contacts.filter((_, j) => j !== i) }) }}><Trash2 className="mx-auto h-4 w-4" /></button>
              </div>
            )
          })}
        </div>
        <button type="button" className="btn-outline mt-3 !h-9" onClick={() => { setSaved(false); setForm({ ...current, extra_contacts: [...(current.extra_contacts || []), { label: '', value: '', url: '' }] }) }}><Plus className="h-4 w-4" />{t('Add a line')}</button>
      </fieldset>
      <div className="mt-6 flex items-center gap-3"><button className="btn-primary">{t('Save settings')}</button>{saved && <span className="text-[14px] text-turquoise-deep">{t('Saved')}</span>}</div>
    </form>
  )
}
