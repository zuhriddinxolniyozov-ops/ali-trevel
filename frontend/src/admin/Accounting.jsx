import { useEffect, useMemo, useState } from 'react'
import { Download, FileText, Plus, Printer, Trash2, Wand2 } from 'lucide-react'
import { api } from '../api'
import { useFetch } from '../hooks'
import { useI18n, useT } from '../i18n'
import { Spinner } from '../components/ui'
import { printSection } from '../components/DayPlan'
import { cap } from '../pages/Auth'

const usd = (v) => `$${Number(v || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
const ymd = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
const today = () => ymd(new Date())
const CATEGORIES = ['guide', 'transport', 'meals', 'hotel', 'tickets', 'marketing', 'office', 'other']
const METHODS = [['cash', 'Cash'], ['card', 'Card'], ['transfer', 'Bank transfer'], ['other', 'Other']]
const field = 'h-9 rounded-sm border border-navy/15 bg-white px-2.5 text-[13px] text-navy outline-none focus:border-navy'

function periodRange(key) {
  const now = new Date()
  const [y, m] = [now.getFullYear(), now.getMonth()]
  const span = (a, b) => ({ from: ymd(a), to: ymd(b) })
  if (key === 'month') return span(new Date(y, m, 1), new Date(y, m + 1, 0))
  if (key === 'last') return span(new Date(y, m - 1, 1), new Date(y, m, 0))
  if (key === 'year') return span(new Date(y, 0, 1), new Date(y, 11, 31))
  return { from: '', to: '' }
}
const query = (range) => [range.from && `from=${range.from}`, range.to && `to=${range.to}`].filter(Boolean).join('&')

const STATE = {
  settled: ['Settled', 'bg-emerald-100 text-emerald-900'], partial: ['Partly paid', 'bg-amber-100 text-amber-900'],
  unpaid: ['Unpaid', 'bg-red-100 text-red-900'], unpriced: ['No price', 'bg-sand text-navy'],
}
function StateChip({ state }) {
  const t = useT()
  const [label, tone] = STATE[state] || STATE.unpriced
  return <span className={`rounded-full px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-[0.08em] ${tone}`}>{t(label)}</span>
}

function Kpi({ label, value, note, tone = '' }) {
  return (
    <div className="rounded-sm border border-navy/10 bg-white p-5">
      <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink">{label}</p>
      <p className={`mt-3 font-heading text-[32px] leading-none ${tone}`}>{value}</p>
      <p className="mt-2 text-[12.5px] text-ink">{note}</p>
    </div>
  )
}

/* ---------- summary ---------- */
function Summary({ range, openBooking }) {
  const t = useT()
  const { lang } = useI18n()
  const { data: s, loading } = useFetch(`/accounting/summary/?${query(range)}`)
  if (loading || !s) return <Spinner />
  const max = Math.max(1, ...s.trend.flatMap((m) => [m.revenue, m.expenses]))
  const bar = (v) => (v ? `${Math.max(3, (v / max) * 100)}%` : '0')
  const month = (key) => new Date(`${key}-15T12:00:00`).toLocaleDateString(lang === 'uz' ? 'uz-UZ' : lang, { month: 'short' })
  const topCategory = Math.max(1, ...s.by_category.map((c) => c.amount))
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-3">
        <Kpi label={t('Revenue')} value={usd(s.revenue)} note={t('Completed tours: {n}', { n: s.completed })} />
        <Kpi label={t('Received')} value={usd(s.received)} note={t('Payments received in the period')} />
        <Kpi label={t('Outstanding')} value={usd(s.outstanding)} note={t('Unpaid balance of completed tours')} tone={s.outstanding > 0 ? 'text-amber-700' : ''} />
        <Kpi label={t('Expenses')} value={usd(s.expenses)} note={t('Costs of tours plus general expenses')} />
        <Kpi label={t('Net profit')} value={usd(s.profit)} note={t('Revenue minus expenses')} tone={s.profit < 0 ? 'text-destructive' : 'text-emerald-700'} />
        <Kpi label={t('Margin')} value={`${s.margin}%`} note={t('Profit as a share of revenue')} />
      </div>

      <section className="rounded-sm border border-navy/10 bg-white p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-heading text-[24px]">{t('Revenue and expenses by month')}</h2>
          <div className="flex gap-4 text-[12px] text-ink"><span className="flex items-center gap-1.5"><i className="h-2.5 w-2.5 rounded-sm bg-navy" />{t('Revenue')}</span><span className="flex items-center gap-1.5"><i className="h-2.5 w-2.5 rounded-sm bg-turquoise" />{t('Expenses')}</span></div>
        </div>
        <div className="mt-5 flex gap-1.5 sm:gap-3">
          {s.trend.map((m) => (
            <div key={m.month} className="flex min-w-0 flex-1 flex-col items-center gap-2">
              <div className="flex h-40 w-full items-end justify-center gap-1" title={`${m.month}: ${usd(m.revenue)} / ${usd(m.expenses)}`}>
                <div style={{ height: bar(m.revenue) }} className="w-1/2 max-w-[20px] rounded-t bg-navy" />
                <div style={{ height: bar(m.expenses) }} className="w-1/2 max-w-[20px] rounded-t bg-turquoise" />
              </div>
              <span className="text-[10px] uppercase text-ink">{month(m.month)}</span>
            </div>
          ))}
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-sm border border-navy/10 bg-white p-5">
          <h2 className="font-heading text-[24px]">{t('Expenses by category')}</h2>
          <ul className="mt-4 space-y-3">
            {s.by_category.map((c) => (
              <li key={c.category}>
                <div className="flex justify-between text-[14px]"><span>{t(cap(c.category))}</span><span className="font-mono">{usd(c.amount)}</span></div>
                <div className="mt-1 h-2 rounded-full bg-sand-soft"><div className="h-2 rounded-full bg-turquoise" style={{ width: `${(c.amount / topCategory) * 100}%` }} /></div>
              </li>
            ))}
            {!s.by_category.length && <li className="text-[14px] text-ink">{t('No expenses in this period.')}</li>}
          </ul>
        </section>
        <section className="rounded-sm border border-navy/10 bg-white">
          <header className="border-b border-navy/10 px-5 py-4"><h2 className="font-heading text-[24px]">{t('Ready to settle')}</h2><p className="text-[12.5px] text-ink">{t('Completed tours with a balance to collect')}</p></header>
          <ul className="divide-y divide-navy/10">
            {s.receivables.map((r) => (
              <li key={r.id}>
                <button onClick={() => openBooking(r.id)} className="flex w-full items-center justify-between gap-3 px-5 py-3 text-left hover:bg-sand-soft/50">
                  <span className="min-w-0"><span className="block truncate text-[14.5px] font-medium">{r.service_title}</span><span className="block truncate text-[12.5px] text-ink">{r.reference} · {r.full_name}</span></span>
                  <span className="shrink-0 font-mono text-[14px] text-amber-700">{usd(r.balance)}</span>
                </button>
              </li>
            ))}
            {!s.receivables.length && <li className="px-5 py-6 text-[14px] text-ink">{s.completed ? t('All completed tours are paid.') : t('No completed tours in this period.')}</li>}
          </ul>
        </section>
      </div>
    </div>
  )
}

/* ---------- forms ---------- */
function PaymentForm({ booking, onSaved }) {
  const t = useT()
  const [f, setF] = useState({ amount_usd: '', method: 'cash', paid_on: today(), note: '' })
  const [error, setError] = useState('')
  const set = (k) => (e) => setF((p) => ({ ...p, [k]: e.target.value }))
  async function submit(e) {
    e.preventDefault(); setError('')
    try { await api.post('/payments/', { ...f, booking: booking.id, amount_usd: Number(f.amount_usd) }); setF((p) => ({ ...p, amount_usd: '', note: '' })); onSaved() } catch (ex) { setError(ex.message) }
  }
  return (
    <form onSubmit={submit} className="mt-3 flex flex-wrap items-center gap-2">
      <input required type="number" min="0.01" step="0.01" aria-label={t('Amount (USD)')} placeholder={t('Amount (USD)')} className={`${field} w-32`} value={f.amount_usd} onChange={set('amount_usd')} />
      <select aria-label={t('Method')} className={field} value={f.method} onChange={set('method')}>{METHODS.map(([k, l]) => <option key={k} value={k}>{t(l)}</option>)}</select>
      <input type="date" aria-label={t('Date')} className={field} value={f.paid_on} onChange={set('paid_on')} />
      <input aria-label={t('Note')} placeholder={t('Note')} className={`${field} min-w-[120px] flex-1`} value={f.note} onChange={set('note')} />
      <button className="inline-flex h-9 items-center gap-1.5 rounded-full bg-navy px-4 text-[13px] text-ivory"><Plus className="h-3.5 w-3.5" />{t('Add payment')}</button>
      {error && <span role="alert" className="basis-full text-[12px] text-destructive">{error}</span>}
    </form>
  )
}

function ExpenseForm({ booking, onSaved }) {
  const t = useT()
  const [f, setF] = useState({ category: booking ? 'guide' : 'office', description: '', amount_usd: '', spent_on: today(), paid_to: '' })
  const [error, setError] = useState('')
  const set = (k) => (e) => setF((p) => ({ ...p, [k]: e.target.value }))
  async function submit(e) {
    e.preventDefault(); setError('')
    try {
      await api.post('/expenses/', { ...f, amount_usd: Number(f.amount_usd), ...(booking ? { booking: booking.id } : {}) })
      setF((p) => ({ ...p, description: '', amount_usd: '', paid_to: '' })); onSaved()
    } catch (ex) { setError(ex.message) }
  }
  return (
    <form onSubmit={submit} className="mt-3 flex flex-wrap items-center gap-2">
      <select aria-label={t('Category')} className={field} value={f.category} onChange={set('category')}>{CATEGORIES.map((c) => <option key={c} value={c}>{t(cap(c))}</option>)}</select>
      <input required aria-label={t('Description')} placeholder={t('Description')} className={`${field} min-w-[150px] flex-1`} value={f.description} onChange={set('description')} />
      <input required type="number" min="0.01" step="0.01" aria-label={t('Amount (USD)')} placeholder={t('Amount (USD)')} className={`${field} w-32`} value={f.amount_usd} onChange={set('amount_usd')} />
      <input type="date" aria-label={t('Date')} className={field} value={f.spent_on} onChange={set('spent_on')} />
      <input aria-label={t('Paid to')} placeholder={t('Paid to')} className={`${field} w-36`} value={f.paid_to} onChange={set('paid_to')} />
      <button className="inline-flex h-9 items-center gap-1.5 rounded-full bg-navy px-4 text-[13px] text-ivory"><Plus className="h-3.5 w-3.5" />{t('Add expense')}</button>
      {error && <span role="alert" className="basis-full text-[12px] text-destructive">{error}</span>}
    </form>
  )
}

function MoneyList({ rows, kind, onChanged }) {
  const t = useT()
  const remove = async (r) => { await api.del(`/${kind}/${r.id}/`); onChanged() }
  return (
    <ul className="mt-2 divide-y divide-navy/10 rounded-sm border border-navy/10 bg-white text-[13.5px]">
      {rows.map((r) => (
        <li key={r.id} className="flex items-center gap-3 px-3 py-2">
          <span className="w-24 shrink-0 font-mono text-[12px] text-ink">{r.paid_on || r.spent_on}</span>
          <span className="min-w-0 flex-1 truncate">{kind === 'payments' ? `${t(METHODS.find(([k]) => k === r.method)?.[1] || 'Other')}${r.note ? ` · ${r.note}` : ''}` : `${t(cap(r.category))} · ${r.description}${r.paid_to ? ` · ${r.paid_to}` : ''}`}{r.auto && <span className="ml-2 rounded-full bg-sand px-2 py-0.5 text-[10px] text-navy/70">{t('auto')}</span>}</span>
          <span className="font-mono">{usd(r.amount_usd)}</span>
          <button type="button" aria-label={t('Delete')} onClick={() => remove(r)} className="text-destructive"><Trash2 className="h-3.5 w-3.5" /></button>
        </li>
      ))}
      {!rows.length && <li className="px-3 py-3 text-ink">{kind === 'payments' ? t('No payments yet.') : t('No costs yet.')}</li>}
    </ul>
  )
}

/* ---------- invoice ---------- */
function Invoice({ id, onClose }) {
  const t = useT()
  const { data: inv } = useFetch(`/accounting/invoice/${id}/`)
  return (
    <div className="fixed inset-0 z-[100] overflow-y-auto bg-navy/60 p-4 sm:p-8">
      <div className="mx-auto max-w-2xl">
        <div className="mb-3 flex justify-end gap-2 print:hidden">
          <button onClick={() => printSection('invoice-sheet')} className="btn-primary !h-10"><Printer className="h-4 w-4" />{t('Print invoice')}</button>
          <button onClick={onClose} className="btn-outline !h-10 !bg-white">{t('Close')}</button>
        </div>
        {!inv ? <div className="grid place-items-center rounded-md bg-white p-16"><Spinner /></div> : (
          <div id="invoice-sheet" className="rounded-md bg-white p-8 text-[14px] text-navy">
            <div className="flex items-start justify-between gap-6">
              <div><p className="font-heading text-[30px]">{inv.company.name}</p><p className="text-ink">{[inv.company.address, inv.company.phone, inv.company.email].filter(Boolean).join(' · ')}</p></div>
              <div className="text-right"><p className="font-heading text-[26px]">{t('Invoice')}</p><p className="font-mono text-[13px]">{inv.number}</p><p className="text-ink">{t('Issued')}: {inv.issued}</p></div>
            </div>
            <div className="mt-6"><p className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink">{t('Billed to')}</p><p className="mt-1 font-medium">{inv.customer.name}</p><p className="text-ink">{inv.customer.email} · {inv.customer.phone}</p></div>
            <table className="mt-6 w-full text-left">
              <thead><tr className="border-b border-navy/20 font-mono text-[10px] uppercase tracking-[0.12em] text-ink"><th className="py-2">{t('Description')}</th><th className="py-2 text-right">{t('Qty')}</th><th className="py-2 text-right">{t('Unit price')}</th><th className="py-2 text-right">{t('Amount')}</th></tr></thead>
              <tbody>{inv.lines.map((l, i) => <tr key={i} className="border-b border-navy/10"><td className="py-2">{l.description}<span className="block text-[12px] text-ink">{inv.service.from}{inv.service.to ? ` → ${inv.service.to}` : ''}</span></td><td className="py-2 text-right">{l.quantity}</td><td className="py-2 text-right font-mono">{usd(l.unit)}</td><td className="py-2 text-right font-mono">{usd(l.amount)}</td></tr>)}</tbody>
            </table>
            <dl className="ml-auto mt-4 w-64 space-y-1.5">
              {inv.discount > 0 && <div className="flex justify-between"><dt>{t('Discount')}</dt><dd className="font-mono">−{usd(inv.discount)}</dd></div>}
              <div className="flex justify-between font-medium"><dt>{t('Total due')}</dt><dd className="font-mono">{usd(inv.total)}</dd></div>
              <div className="flex justify-between"><dt>{t('Paid')}</dt><dd className="font-mono">{usd(inv.paid)}</dd></div>
              <div className="flex justify-between border-t border-navy/20 pt-1.5 font-medium"><dt>{t('Balance')}</dt><dd className="font-mono">{usd(inv.balance)}</dd></div>
            </dl>
            <p className="mt-8 text-center text-ink">{t('Thank you for travelling with ALI TRAVEL.')}</p>
          </div>
        )}
      </div>
    </div>
  )
}

/* ---------- ledger ---------- */
function Panel({ row, reload, onInvoice }) {
  const t = useT()
  const [price, setPrice] = useState(row.final_price_usd ?? '')
  const [discount, setDiscount] = useState(row.discount_usd || '')
  const [message, setMessage] = useState('')
  const savePrice = async () => {
    setMessage('')
    try { await api.patch(`/accounting/bookings/${row.id}/`, { final_price_usd: price === '' ? null : Number(price), discount_usd: Number(discount || 0) }); reload() } catch (ex) { setMessage(ex.message) }
  }
  const payRest = async () => { await api.post('/payments/', { booking: row.id, amount_usd: row.balance, method: 'cash', paid_on: today(), note: t('Paid in full') }); reload() }
  const autoCosts = async () => {
    setMessage('')
    try { await api.post(`/accounting/bookings/${row.id}/auto-costs/`); reload() } catch (ex) { setMessage(ex.message) }
  }
  return (
    <div className="grid gap-6 border-t border-navy/10 bg-sand-soft/40 p-4 lg:grid-cols-2">
      <div>
        <h4 className="font-heading text-[20px]">{t('Price')}</h4>
        <div className="mt-2 flex flex-wrap items-end gap-2">
          <label className="text-[12px] text-ink">{t('Agreed price (USD)')}<input type="number" min="0" step="0.01" className={`${field} mt-1 block w-36`} placeholder={String(row.estimated_total_usd)} value={price} onChange={(e) => setPrice(e.target.value)} /></label>
          <label className="text-[12px] text-ink">{t('Discount (USD)')}<input type="number" min="0" step="0.01" className={`${field} mt-1 block w-32`} value={discount} onChange={(e) => setDiscount(e.target.value)} /></label>
          <button onClick={savePrice} className="h-9 rounded-full border border-navy/20 px-4 text-[13px] hover:bg-white">{t('Save')}</button>
        </div>
        <p className="mt-1 text-[12px] text-ink">{t('Leave empty to use the estimate')} ({usd(row.estimated_total_usd)})</p>
        <h4 className="mt-5 font-heading text-[20px]">{t('Payments')}</h4>
        <MoneyList rows={row.payments} kind="payments" onChanged={reload} />
        <PaymentForm booking={row} onSaved={reload} />
        {row.balance > 0 && <button onClick={payRest} className="mt-2 text-[13px] text-turquoise-deep underline">{t('Mark as paid in full')} ({usd(row.balance)})</button>}
      </div>
      <div>
        <div className="flex flex-wrap items-center justify-between gap-2"><h4 className="font-heading text-[20px]">{t('Tour costs')}</h4>
          <button onClick={autoCosts} className="inline-flex h-9 items-center gap-1.5 rounded-full border border-navy/20 px-3.5 text-[12.5px] hover:bg-white"><Wand2 className="h-3.5 w-3.5" />{t('Fill estimated costs from the tour template')}</button></div>
        <MoneyList rows={row.expenses} kind="expenses" onChanged={reload} />
        <ExpenseForm booking={row} onSaved={reload} />
        <div className="mt-5 flex flex-wrap gap-2"><button onClick={() => onInvoice(row.id)} className="inline-flex h-9 items-center gap-1.5 rounded-full bg-navy px-4 text-[13px] text-ivory"><FileText className="h-3.5 w-3.5" />{t('Invoice')}</button></div>
      </div>
      {message && <p role="alert" className="text-[13px] text-destructive lg:col-span-2">{message}</p>}
    </div>
  )
}

function Ledger({ range, focusId }) {
  const t = useT()
  const [filter, setFilter] = useState(focusId ? 'open' : 'completed')
  const [q, setQ] = useState('')
  const [open, setOpen] = useState(focusId || null)
  const [invoice, setInvoice] = useState(null)
  const params = { completed: 'status=completed', open: 'status=completed&state=open', settled: 'status=completed&state=settled', all: 'status=all' }[filter]
  const { data, loading, reload } = useFetch(`/accounting/ledger/?${params}&q=${encodeURIComponent(q)}&${query(range)}`, { list: true })
  useEffect(() => { if (focusId) document.getElementById(`row-${focusId}`)?.scrollIntoView({ block: 'center' }) }, [focusId, data.length])
  const totals = useMemo(() => data.reduce((a, r) => ({ due: a.due + r.total_due, paid: a.paid + r.paid, costs: a.costs + r.costs, profit: a.profit + r.profit }), { due: 0, paid: 0, costs: 0, profit: 0 }), [data])
  const FILTERS = [['completed', 'Completed tours'], ['open', 'Open balances'], ['settled', 'Settled'], ['all', 'All tours']]
  const cols = 'grid-cols-[1.6fr_repeat(4,1fr)] lg:grid-cols-[2fr_1fr_repeat(5,1fr)_1fr]'
  return (
    <div>
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex flex-wrap gap-2">{FILTERS.map(([k, l]) => <button key={k} onClick={() => setFilter(k)} className={`h-10 rounded-full border px-4 text-[14px] ${filter === k ? 'border-navy bg-navy text-ivory' : 'border-navy/10 bg-white hover:bg-sand-soft'}`}>{t(l)}</button>)}</div>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder={t('Search tour, customer or reference')} className="h-10 w-full max-w-sm rounded-sm border border-navy/10 bg-white px-3 text-[14px] outline-none focus:border-navy" />
      </div>
      <div className="mt-4 overflow-x-auto rounded-sm border border-navy/10 bg-white">
        <div className="min-w-[760px]">
          <div className={`grid ${cols} gap-3 border-b border-navy/10 px-4 py-3 font-mono text-[10px] uppercase tracking-[0.14em] text-ink`}>
            <span>{t('Tour')}</span><span className="hidden lg:block">{t('Date')}</span><span className="text-right">{t('Total due')}</span><span className="text-right">{t('Paid')}</span><span className="text-right">{t('Balance')}</span><span className="hidden text-right lg:block">{t('Costs')}</span><span className="hidden text-right lg:block">{t('Profit')}</span><span className="text-right">{t('Status')}</span>
          </div>
          {loading ? <div className="p-6"><Spinner /></div> : data.map((r) => (
            <div key={r.id} id={`row-${r.id}`} className="border-b border-navy/10 last:border-0">
              <button onClick={() => setOpen(open === r.id ? null : r.id)} className={`grid w-full ${cols} items-center gap-3 px-4 py-3 text-left text-[14px] hover:bg-sand-soft/50`}>
                <span className="min-w-0"><span className="block truncate font-medium">{r.service_title}</span><span className="block truncate text-[12px] text-ink">{r.reference} · {r.full_name} · {r.guests}</span></span>
                <span className="hidden font-mono text-[12.5px] lg:block">{r.service_date}</span>
                <span className="text-right font-mono">{usd(r.total_due)}</span>
                <span className="text-right font-mono">{usd(r.paid)}</span>
                <span className={`text-right font-mono ${r.balance > 0 ? 'text-amber-700' : ''}`}>{usd(r.balance)}</span>
                <span className="hidden text-right font-mono lg:block">{usd(r.costs)}</span>
                <span className={`hidden text-right font-mono lg:block ${r.profit < 0 ? 'text-destructive' : 'text-emerald-700'}`}>{usd(r.profit)}</span>
                <span className="text-right"><StateChip state={r.state} /></span>
              </button>
              {open === r.id && <Panel row={r} reload={reload} onInvoice={setInvoice} />}
            </div>
          ))}
          {!loading && !data.length && <p className="p-8 text-center text-ink">{t('No tours here yet. Mark a booking as completed to see it in the ledger.')}</p>}
          {data.length > 0 && (
            <div className={`grid ${cols} gap-3 border-t border-navy/20 bg-sand-soft/50 px-4 py-3 text-[14px] font-medium`}>
              <span>{t('Totals')} · {data.length}</span><span className="hidden lg:block" /><span className="text-right font-mono">{usd(totals.due)}</span><span className="text-right font-mono">{usd(totals.paid)}</span><span className="text-right font-mono">{usd(totals.due - totals.paid)}</span>
              <span className="hidden text-right font-mono lg:block">{usd(totals.costs)}</span><span className="hidden text-right font-mono lg:block">{usd(totals.profit)}</span><span />
            </div>
          )}
        </div>
      </div>
      {invoice && <Invoice id={invoice} onClose={() => setInvoice(null)} />}
    </div>
  )
}

/* ---------- general expenses ---------- */
function GeneralExpenses({ range }) {
  const t = useT()
  const { data, reload } = useFetch('/expenses/?general=1', { list: true })
  const shown = data.filter((e) => (!range.from || e.spent_on >= range.from) && (!range.to || e.spent_on <= range.to))
  const total = shown.reduce((sum, e) => sum + e.amount_usd, 0)
  return (
    <div className="max-w-4xl">
      <h2 className="font-heading text-[26px]">{t('General expenses (not linked to a tour)')}</h2>
      <p className="mt-1 text-[14px] text-ink">{t('Rent, advertising, salaries and other costs of running the business.')}</p>
      <ExpenseForm booking={null} onSaved={reload} />
      <MoneyList rows={shown} kind="expenses" onChanged={reload} />
      <p className="mt-3 text-right text-[15px] font-medium">{t('Total')}: <span className="font-mono">{usd(total)}</span></p>
    </div>
  )
}

export default function Accounting() {
  const t = useT()
  const [tab, setTab] = useState('summary')
  const [period, setPeriod] = useState('year')
  const [focusId, setFocusId] = useState(null)
  const range = useMemo(() => periodRange(period), [period])
  const tabs = [['summary', 'Summary'], ['ledger', 'Tour ledger'], ['expenses', 'General expenses']]
  const periods = [['month', 'This month'], ['last', 'Last month'], ['year', 'This year'], ['all', 'All time']]
  const download = (kind) => api.download(`/accounting/export/?kind=${kind}&${query(range)}`, `ali-travel-${kind}.csv`)
  const openBooking = (id) => { setFocusId(id); setTab('ledger') }
  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2" role="tablist">{tabs.map(([k, l]) => <button key={k} role="tab" aria-selected={tab === k} onClick={() => { setTab(k); if (k !== 'ledger') setFocusId(null) }} className={`h-10 rounded-full border px-5 text-[14px] ${tab === k ? 'border-navy bg-navy text-ivory' : 'border-navy/10 bg-white hover:bg-sand-soft'}`}>{t(l)}</button>)}</div>
        <div className="flex flex-wrap items-center gap-2">
          <select aria-label={t('Period')} value={period} onChange={(e) => setPeriod(e.target.value)} className="h-10 rounded-full border border-navy/15 bg-white px-4 text-[14px]">{periods.map(([k, l]) => <option key={k} value={k}>{t(l)}</option>)}</select>
          <button onClick={() => download('bookings')} className="inline-flex h-10 items-center gap-1.5 rounded-full border border-navy/15 bg-white px-4 text-[13px] hover:bg-sand-soft"><Download className="h-3.5 w-3.5" />{t('Tours (CSV)')}</button>
          <button onClick={() => download('expenses')} className="inline-flex h-10 items-center gap-1.5 rounded-full border border-navy/15 bg-white px-4 text-[13px] hover:bg-sand-soft"><Download className="h-3.5 w-3.5" />{t('Expenses (CSV)')}</button>
        </div>
      </div>
      <p className="mt-3 text-[13px] text-ink">{t('Revenue and profit count tours marked as completed, by the day the tour took place. Amounts are in US dollars.')}</p>
      <div className="mt-5">
        {tab === 'summary' && <Summary range={range} openBooking={openBooking} />}
        {tab === 'ledger' && <Ledger key={focusId || 'all'} range={range} focusId={focusId} />}
        {tab === 'expenses' && <GeneralExpenses range={range} />}
      </div>
    </div>
  )
}
