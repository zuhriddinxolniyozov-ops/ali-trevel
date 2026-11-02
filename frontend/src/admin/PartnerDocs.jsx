import { useEffect, useMemo, useRef, useState } from 'react'
import { Copy, Download, Mail, Printer, RotateCcw } from 'lucide-react'
import { useFetch, useSettings } from '../hooks'
import { useT } from '../i18n'
import LegalText from '../components/LegalText'
import { printSection } from '../components/DayPlan'
import { DOCS, DOC_LANGS, PARTNER_TYPES, buildDocument, subjectOf } from './partnerTemplates'

const TYPE_LABEL = { hotel: 'Hotel / guesthouse', guide: 'Guide', transport: 'Driver / transfers' }
const DOC_LABEL = { proposal: 'Cooperation proposal', email: 'Official email', inquiry: 'Price request letter', agreement: 'Cooperation agreement' }
const DEFAULT_CITY = { en: 'Samarkand', uz: 'Samarqand', ru: 'Самарканд' }
const PARTNER_TO_TYPE = { 'Hotel / guesthouse': 'hotel', Guide: 'guide', 'Driver / transfers': 'transport' }
const inDays = (n) => { const d = new Date(); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10) }
const field = 'h-10 w-full rounded-sm border border-navy/15 bg-white px-3 text-[14px] text-navy outline-none focus:border-navy'

function Choice({ value, onChange, options, label }) {
  return (
    <div className="flex flex-wrap gap-2" role="radiogroup" aria-label={label}>
      {options.map(([k, text]) => (
        <button key={k} type="button" role="radio" aria-checked={value === k} onClick={() => onChange(k)}
          className={`h-10 rounded-full border px-4 text-[13px] ${value === k ? 'border-navy bg-navy text-ivory' : 'border-navy/15 bg-white hover:bg-sand-soft'}`}>{text}</button>
      ))}
    </div>
  )
}

function Input({ label, ...props }) {
  return <label className="label">{label}<input className={`${field} mt-1`} {...props} /></label>
}

/** Drafts of the letters and the agreement we send to hotels, guides and drivers. Everything stays editable. */
export default function PartnerDocs() {
  const t = useT()
  const { settings } = useSettings()
  const partners = useFetch('/partners/', { list: true })
  const [type, setType] = useState('hotel')
  const [doc, setDoc] = useState('proposal')
  const [lang, setLang] = useState('en')
  const [tab, setTab] = useState('text')
  const [text, setText] = useState('')
  const [dirty, setDirty] = useState(false)
  const [notice, setNotice] = useState('')
  const preview = useRef(null)
  const [d, setD] = useState({
    partner: '', contact: '', city: DEFAULT_CITY.en, partnerAddress: '', partnerEmail: '', partnerPhone: '',
    ourName: '', ourRole: '', date: inDays(0), deadline: inDays(14), commission: '', paymentDays: 7, termMonths: 12, cancelHours: 48,
  })
  const set = (k) => (e) => setD((p) => ({ ...p, [k]: e.target.value }))
  const data = useMemo(() => ({
    ...d, ourEmail: settings.email, ourPhone: settings.phone_primary, ourAddress: settings.address,
    partnerContacts: [d.partnerPhone, d.partnerEmail].filter(Boolean).join(' · '),
    commission: d.commission === '' ? 0 : Number(d.commission), paymentDays: Number(d.paymentDays) || 7, termMonths: Number(d.termMonths) || 12, cancelHours: Number(d.cancelHours) || 48,
  }), [d, settings])

  // Rebuild the draft whenever a choice or a field changes, unless the text was edited by hand.
  useEffect(() => { if (!dirty) setText(buildDocument({ doc, type, lang, data })) }, [doc, type, lang, data, dirty])
  const chooseLang = (code) => {
    setLang(code)
    setD((p) => (Object.values(DEFAULT_CITY).includes(p.city) ? { ...p, city: DEFAULT_CITY[code] } : p))
  }
  const fromPartner = (id) => {
    const p = partners.data.find((x) => String(x.id) === id)
    if (!p) return
    setType(PARTNER_TO_TYPE[p.partner_type] || type)
    setD((prev) => ({ ...prev, partner: p.business_name, contact: p.contact_name, city: p.city || prev.city, partnerEmail: p.email, partnerPhone: p.phone }))
  }

  const flash = (msg) => { setNotice(msg); setTimeout(() => setNotice(''), 2200) }
  const copy = async () => { try { await navigator.clipboard.writeText(text.replace(/\*\*/g, '').replace(/^#{1,3}\s+/gm, '')); flash(t('Copied')) } catch { flash(t('Copy failed — select the text and copy it manually.')) } }
  const download = () => {
    const html = `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word"><head><meta charset="utf-8"><title>${DOC_LABEL[doc]}</title>
      <style>body{font-family:Calibri,Arial,sans-serif;font-size:11pt;line-height:1.45}h1{font-size:16pt;text-align:center}h2{font-size:13pt;margin-top:14pt}p,li{margin:4pt 0}</style></head><body>${preview.current?.innerHTML || ''}</body></html>`
    const link = document.createElement('a')
    link.href = URL.createObjectURL(new Blob(['﻿', html], { type: 'application/msword' }))
    link.download = `${doc}-${type}-${lang}-${(d.partner || 'partner').replace(/[^\w-]+/g, '_')}.doc`
    link.click()
    URL.revokeObjectURL(link.href)
  }
  const print = () => { setTab('preview'); setTimeout(() => printSection('partner-doc'), 150) }
  const plain = text.replace(/\*\*/g, '').replace(/^#{1,3}\s+/gm, '').replace(/^\s*(Subject|Mavzu|Тема):.*\n+/i, '')
  const mailto = `mailto:${d.partnerEmail}?subject=${encodeURIComponent(subjectOf(text))}&body=${encodeURIComponent(plain)}`

  return (
    <div className="grid gap-6 xl:grid-cols-[400px_1fr]">
      <aside className="space-y-5 rounded-sm border border-navy/10 bg-white p-5 xl:self-start">
        <p className="text-[13px] leading-relaxed text-ink">{t('Drafts for hotels, guides and transport providers in Samarkand. Choose what you need, fill in the details, then edit the text, copy it, print it or download it as a Word file. Have a lawyer read the agreement before it is signed.')}</p>
        <div><p className="eyebrow mb-2">{t('Who is it for?')}</p><Choice label={t('Partner type')} value={type} onChange={setType} options={PARTNER_TYPES.map((k) => [k, t(TYPE_LABEL[k])])} /></div>
        <div><p className="eyebrow mb-2">{t('Document')}</p><Choice label={t('Document')} value={doc} onChange={setDoc} options={DOCS.map((k) => [k, t(DOC_LABEL[k])])} /></div>
        <div><p className="eyebrow mb-2">{t('Language')}</p><Choice label={t('Language')} value={lang} onChange={chooseLang} options={DOC_LANGS} /></div>

        <div className="space-y-3 border-t border-navy/10 pt-5">
          {partners.data.length > 0 && (
            <label className="label">{t('Fill from a registered partner')}
              <select className={`${field} mt-1`} defaultValue="" onChange={(e) => fromPartner(e.target.value)}>
                <option value="">{t('— choose —')}</option>{partners.data.map((p) => <option key={p.id} value={p.id}>{p.business_name} · {p.partner_type}</option>)}</select></label>)}
          <Input label={t('Partner name')} value={d.partner} onChange={set('partner')} placeholder="Registan Plaza Hotel" />
          <Input label={t('Contact person')} value={d.contact} onChange={set('contact')} />
          <div className="grid grid-cols-2 gap-3"><Input label={t('City')} value={d.city} onChange={set('city')} /><Input label={t('Partner phone')} value={d.partnerPhone} onChange={set('partnerPhone')} /></div>
          <Input label={t('Partner email')} type="email" value={d.partnerEmail} onChange={set('partnerEmail')} />
          <Input label={t('Partner address')} value={d.partnerAddress} onChange={set('partnerAddress')} />
        </div>
        <div className="space-y-3 border-t border-navy/10 pt-5">
          <p className="eyebrow">{t('Signed by')}</p>
          <div className="grid grid-cols-2 gap-3"><Input label={t('Your name')} value={d.ourName} onChange={set('ourName')} /><Input label={t('Position')} value={d.ourRole} onChange={set('ourRole')} /></div>
          <p className="text-[12px] text-ink">{t('Our phone, email and address come from Contact & settings.')}</p>
        </div>
        <div className="space-y-3 border-t border-navy/10 pt-5">
          <p className="eyebrow">{t('Dates and terms')}</p>
          <div className="grid grid-cols-2 gap-3"><Input label={t('Document date')} type="date" value={d.date} onChange={set('date')} /><Input label={t('Reply by')} type="date" value={d.deadline} onChange={set('deadline')} /></div>
          <div className="grid grid-cols-2 gap-3">
            <Input label={t('Payment within (days)')} type="number" min="1" value={d.paymentDays} onChange={set('paymentDays')} />
            <Input label={t('Commission / discount (%)')} type="number" min="0" max="50" value={d.commission} onChange={set('commission')} />
            <Input label={t('Agreement term (months)')} type="number" min="1" value={d.termMonths} onChange={set('termMonths')} />
            <Input label={t('Free cancellation (hours before)')} type="number" min="0" value={d.cancelHours} onChange={set('cancelHours')} />
          </div>
        </div>
      </aside>

      <section className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex rounded-full border border-navy/15 p-0.5" role="tablist">
            {[['text', 'Edit text'], ['preview', 'Preview']].map(([k, l]) => <button key={k} role="tab" aria-selected={tab === k} onClick={() => setTab(k)} className={`h-9 rounded-full px-4 text-[13px] ${tab === k ? 'bg-navy text-ivory' : 'hover:bg-sand-soft'}`}>{t(l)}</button>)}
          </div>
          <div className="ml-auto flex flex-wrap items-center gap-2">
            {dirty && <button onClick={() => setDirty(false)} className="inline-flex h-9 items-center gap-1.5 rounded-full border border-navy/15 px-3.5 text-[13px] hover:bg-sand-soft"><RotateCcw className="h-3.5 w-3.5" />{t('Rebuild from the form')}</button>}
            <button onClick={copy} className="inline-flex h-9 items-center gap-1.5 rounded-full border border-navy/15 px-3.5 text-[13px] hover:bg-sand-soft"><Copy className="h-3.5 w-3.5" />{t('Copy')}</button>
            <button onClick={download} className="inline-flex h-9 items-center gap-1.5 rounded-full border border-navy/15 px-3.5 text-[13px] hover:bg-sand-soft"><Download className="h-3.5 w-3.5" />{t('Download (.doc)')}</button>
            <button onClick={print} className="inline-flex h-9 items-center gap-1.5 rounded-full border border-navy/15 px-3.5 text-[13px] hover:bg-sand-soft"><Printer className="h-3.5 w-3.5" />{t('Print')}</button>
            {doc === 'email' && <a href={mailto} className="inline-flex h-9 items-center gap-1.5 rounded-full bg-navy px-4 text-[13px] text-ivory hover:bg-navy-deep"><Mail className="h-3.5 w-3.5" />{t('Open in email')}</a>}
          </div>
        </div>
        {notice && <p role="status" className="mt-2 text-[13px] text-turquoise-deep">{notice}</p>}
        <p className="mt-2 text-[12px] text-ink">{t('Fields in the draft shown as ____ are for you to fill in by hand.')}{doc !== 'email' && ` ${t('Long letters: download the document and attach it to your email.')}`}</p>

        <textarea value={text} onChange={(e) => { setText(e.target.value); setDirty(true) }} spellCheck rows={30} aria-label={t('Document text')}
          className={`mt-3 w-full rounded-sm border border-navy/15 bg-white p-4 font-mono text-[13px] leading-relaxed text-navy outline-none focus:border-navy ${tab === 'text' ? '' : 'hidden'}`} />
        <div className={tab === 'preview' ? '' : 'hidden'}>
          <div id="partner-doc" ref={preview} className="mx-auto mt-3 max-w-3xl rounded-sm border border-navy/10 bg-white p-8 text-navy"><LegalText body={text} /></div>
        </div>
      </section>
    </div>
  )
}
