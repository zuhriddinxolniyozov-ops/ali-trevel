import { useState } from 'react'
import { Copy, Plus, Trash2 } from 'lucide-react'
import { api } from '../api'
import { useFetch } from '../hooks'
import { useT } from '../i18n'
import { Spinner } from '../components/ui'

const field = 'h-10 w-full rounded-sm border border-navy/15 bg-white px-3 text-[14px] text-navy outline-none focus:border-navy'

/** Promo codes the team hands to travellers: the code and its percentage, typed by the traveller in the booking form. */
export default function PromoCodes() {
  const t = useT()
  const { data, loading, reload } = useFetch('/promo-codes/', { list: true })
  const [f, setF] = useState({ code: '', percent: 10, note: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [copied, setCopied] = useState('')

  async function create(e) {
    e.preventDefault()
    setBusy(true); setError('')
    try {
      await api.post('/promo-codes/', { code: f.code, percent: Number(f.percent), note: f.note.trim() })
      setF({ code: '', percent: f.percent, note: '' }); reload()
    } catch (ex) { setError(ex.message) } finally { setBusy(false) }
  }
  const toggle = async (p) => { await api.patch(`/promo-codes/${p.id}/`, { active: !p.active }); reload() }
  const remove = async (p) => { if (window.confirm(t('Delete “{name}”? This cannot be undone.', { name: p.code }))) { await api.del(`/promo-codes/${p.id}/`); reload() } }
  const copy = (code) => { navigator.clipboard?.writeText(code).then(() => { setCopied(code); setTimeout(() => setCopied(''), 1500) }).catch(() => {}) }

  return (
    <div>
      <p className="max-w-3xl text-[14px] text-ink">{t('Give a traveller a code for their next trip or for a friend. They type it in the booking form and its percentage comes off the estimated price. A code works on the global and the local site.')}</p>
      <form onSubmit={create} className="mt-5 grid max-w-3xl gap-3 rounded-sm border border-navy/10 bg-white p-5 sm:grid-cols-[1.3fr_0.7fr_1.6fr_auto] sm:items-end">
        <label className="block text-[12.5px] text-ink">{t('Promo code')}
          <input className={`${field} mt-1 font-mono uppercase`} required maxLength={30} placeholder="ALI10" value={f.code} onChange={(e) => setF({ ...f, code: e.target.value })} /></label>
        <label className="block text-[12.5px] text-ink">{t('Discount, %')}
          <input type="number" min="1" max="90" required className={`${field} mt-1`} value={f.percent} onChange={(e) => setF({ ...f, percent: e.target.value })} /></label>
        <label className="block text-[12.5px] text-ink">{t('Note (optional)')}
          <input className={`${field} mt-1`} maxLength={200} placeholder={t('For example: given to the Smith family')} value={f.note} onChange={(e) => setF({ ...f, note: e.target.value })} /></label>
        <button disabled={busy} className="inline-flex h-10 items-center justify-center gap-2 rounded-full bg-navy px-5 text-[14px] font-medium text-ivory hover:bg-navy-deep">{busy ? <Spinner /> : <Plus className="h-4 w-4" />}{t('Add code')}</button>
        {error && <p role="alert" className="text-[12.5px] text-destructive sm:col-span-4">{t(error)}</p>}
      </form>

      <div className="mt-6 space-y-3">
        {loading && !data.length ? <Spinner /> : data.map((p) => (
          <article key={p.id} className={`flex flex-wrap items-center justify-between gap-4 rounded-sm border border-navy/10 bg-white p-4 ${p.active ? '' : 'opacity-70'}`}>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2.5">
                <button type="button" onClick={() => copy(p.code)} title={t('Copy')} className="inline-flex items-center gap-1.5 rounded-sm bg-sand-soft px-2.5 py-1 font-mono text-[17px] font-semibold tracking-wide text-navy hover:bg-sand">
                  {p.code}<Copy className="h-3.5 w-3.5 text-ink" aria-hidden="true" /></button>
                <span className="rounded-full bg-destructive px-2.5 py-0.5 font-mono text-[11px] text-white">−{p.percent}%</span>
                <span className={`rounded-full px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-[0.1em] ${p.active ? 'bg-emerald-100 text-emerald-900' : 'bg-sand text-navy'}`}>{t(p.active ? 'Active' : 'Paused')}</span>
                {copied === p.code && <span role="status" className="text-[12px] text-turquoise-deep">{t('Copied')}</span>}
              </div>
              <p className="mt-1 text-[13px] text-ink">{t('Used in {n} booking requests', { n: p.uses })}{p.note ? ` · ${p.note}` : ''}</p>
            </div>
            <div className="flex flex-wrap gap-2 text-[13px]">
              <button onClick={() => toggle(p)} className="h-9 rounded-full border border-navy/15 px-3.5 hover:bg-sand-soft">{p.active ? t('Pause') : t('Activate')}</button>
              <button onClick={() => remove(p)} aria-label={t('Delete')} className="grid h-9 w-9 place-items-center rounded-full border border-red-200 text-destructive hover:bg-red-50"><Trash2 className="h-3.5 w-3.5" /></button>
            </div>
          </article>
        ))}
        {!loading && !data.length && <p className="rounded-sm border border-dashed border-navy/20 p-8 text-center text-ink">{t('No promo codes yet.')}</p>}
      </div>
    </div>
  )
}
