import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { Check, Plus, Trash2, X } from 'lucide-react'
import { discounted, exactMoney, useBackClose } from '../hooks'
import { groupPercent } from '../groupPricing'
import { isLocal, roundPrice } from '../market'
import { useT } from '../i18n'
import BookingForm from './BookingForm'
import { Photo } from './ui'

/**
 * Tours the visitor ticked on any page ("Select" on a tour card). They are kept in this browser, so a few tours from different
 * pages can be requested together in one booking.
 */
const KEY = 'ali.selectedTours'
const Ctx = createContext({ items: [], has: () => false, toggle: () => {}, remove: () => {}, clear: () => {}, open: () => {} })
export const useSelection = () => useContext(Ctx)

const slim = (t) => ({
  slug: t.slug, title: t.title, image_url: t.image_url, price_from_usd: Number(t.price_from_usd) || 0,
  effective_discount: t.effective_discount || 0, group_pricing: t.group_pricing !== false, duration_label: t.duration_label,
})

function load() {
  try { const v = JSON.parse(localStorage.getItem(KEY) || '[]'); return Array.isArray(v) ? v : [] } catch { return [] }
}

export function SelectionProvider({ children }) {
  const [items, setItems] = useState(load)
  const [dialog, setDialog] = useState(false)
  useEffect(() => { try { localStorage.setItem(KEY, JSON.stringify(items)) } catch { /* private window: the selection just lives on this page */ } }, [items])
  const toggle = useCallback((tour) => setItems((list) => (list.some((x) => x.slug === tour.slug) ? list.filter((x) => x.slug !== tour.slug) : [...list, slim(tour)])), [])
  const remove = useCallback((slug) => setItems((list) => list.filter((x) => x.slug !== slug)), [])
  const clear = useCallback(() => setItems([]), [])
  const value = useMemo(() => ({ items, has: (slug) => items.some((x) => x.slug === slug), toggle, remove, clear, open: () => setDialog(true) }), [items, toggle, remove, clear])
  return (
    <Ctx.Provider value={value}>
      {children}
      <SelectionBar />
      {dialog && <SelectionDialog onClose={() => setDialog(false)} />}
    </Ctx.Provider>
  )
}

/** The "Select" button shown on a tour card; tours without a price (single places) cannot be selected. */
export function SelectToggle({ tour }) {
  const t = useT()
  const { has, toggle } = useSelection()
  if (!(Number(tour.price_from_usd) > 0)) return null
  const on = has(tour.slug)
  return (
    <button type="button" aria-pressed={on} data-edit-ignore onClick={(e) => { e.preventDefault(); e.stopPropagation(); toggle(tour) }}
      className={`absolute bottom-3 right-3 z-10 inline-flex items-center gap-1.5 rounded-full px-3.5 py-2 text-[12px] font-medium shadow-md transition-colors ${on ? 'bg-turquoise-deep text-white' : 'bg-ivory/95 text-navy hover:bg-white'}`}>
      {on ? <Check className="h-3.5 w-3.5" /> : <Plus className="h-3.5 w-3.5" />}{t(on ? 'Selected' : 'Select')}
    </button>
  )
}

function SelectionBar() {
  const t = useT()
  const { items, clear, open } = useSelection()
  if (!items.length) return null
  return (
    <div className="fixed inset-x-3 bottom-4 z-40 mx-auto flex max-w-xl items-center justify-between gap-3 rounded-full bg-navy py-2 pl-5 pr-2 text-ivory shadow-xl print:hidden sm:inset-x-0">
      <span className="text-[13px]">{t('{n} tours selected', { n: items.length })}</span>
      <span className="flex items-center gap-2">
        <button onClick={clear} className="rounded-full px-3 py-2 text-[12px] text-ivory/75 hover:text-ivory">{t('Clear')}</button>
        <button onClick={open} className="rounded-full bg-ivory px-4 py-2 text-[13px] font-medium text-navy hover:bg-white">{t('Request booking')}</button>
      </span>
    </div>
  )
}

function SelectionDialog({ onClose }) {
  const t = useT()
  const { items, remove, clear } = useSelection()
  const [sent, setSent] = useState(false)
  const grouped = items.some((x) => x.group_pricing)
  const close = () => { if (sent) clear(); onClose() }
  useBackClose(true, close)   // the dialog is shown only while open: Back closes it
  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') close() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  })
  const one = (x, g, tiers) => roundPrice(discounted(x.price_from_usd, x.effective_discount) * (x.group_pricing ? groupPercent(tiers, g) / 100 : 1))
  const priceFor = (g, tiers) => items.reduce((sum, x) => sum + one(x, g, tiers), 0)
  const title = `${t('{n} tours', { n: items.length })}: ${items.map((x) => x.title).join(' + ')}`.slice(0, 250)
  const summary = items.map((x, i) => `${i + 1}. ${x.title} — ${t('from')} ${exactMoney(discounted(x.price_from_usd, x.effective_discount))} / ${t('person')}`).join('\n')
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 p-3 sm:p-8" role="dialog" aria-modal="true" aria-label={t('Your selected tours')} onClick={(e) => { if (e.target === e.currentTarget) close() }}>
      <div className="mx-auto max-w-2xl rounded-md bg-ivory p-5 shadow-2xl sm:p-7">
        <div className="flex items-start justify-between gap-4">
          <h2 className="font-heading text-[28px] leading-tight">{t('Your selected tours')}</h2>
          <button onClick={close} aria-label={t('Close')} className="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-navy/15 hover:bg-sand-soft"><X className="h-4 w-4" /></button>
        </div>
        {!sent && (
          <ul className="mt-5 divide-y divide-navy/10 rounded-sm border border-navy/10 bg-white">
            {items.map((x) => (
              <li key={x.slug} className="flex items-center gap-3 p-3">
                <Photo src={x.image_url} sizes="80px" alt="" className="h-14 w-20 shrink-0 rounded object-cover" />
                <div className="min-w-0 flex-1"><p className="truncate text-[14px] font-medium text-navy">{x.title}</p>
                  <p className="text-[12.5px] text-ink">{t(x.duration_label)} · {t('from')} <span className="font-mono">{exactMoney(discounted(x.price_from_usd, x.effective_discount))}</span> / {t('person')}</p></div>
                <button onClick={() => remove(x.slug)} aria-label={t('Remove')} className="grid h-8 w-8 place-items-center rounded-full text-destructive hover:bg-red-50"><Trash2 className="h-4 w-4" /></button>
              </li>
            ))}
          </ul>
        )}
        {items.length > 0 || sent ? (
          <div className="mt-5">
            <BookingForm guideOptional={isLocal} serviceType="tour" serviceTitle={title} estimatedTotal={items.reduce((s, x) => s + discounted(x.price_from_usd, x.effective_discount), 0)}
              priceFor={grouped ? priceFor : null} extra={{ details_summary: summary }} onSubmitted={() => setSent(true)}
              intro="Tell us when you would like to start. Our team will arrange the tours one after another and confirm the schedule in writing." />
          </div>
        ) : <p className="mt-5 text-[14px] text-ink">{t('No tours selected.')}</p>}
      </div>
    </div>
  )
}
