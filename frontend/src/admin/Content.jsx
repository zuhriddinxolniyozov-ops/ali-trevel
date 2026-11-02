import { useMemo, useState } from 'react'
import { RotateCcw, Search } from 'lucide-react'
import { api } from '../api'
import { LANGS, useI18n } from '../i18n'
import { SECTIONS } from '../strings'

const COLUMN = { uz: 0, ru: 1, fr: 2, de: 3, es: 4 }

function TextRow({ source, lang, builtIn, override, onSave }) {
  const { t } = useI18n()
  const [value, setValue] = useState(override ?? builtIn ?? '')
  const [busy, setBusy] = useState(false)
  const long = source.length > 70
  const initial = override ?? builtIn ?? ''
  const commit = async () => {
    if (value.trim() === initial.trim()) return
    setBusy(true); await onSave(source, value); setBusy(false)
  }
  const reset = async () => { setBusy(true); await onSave(source, ''); setValue(builtIn ?? ''); setBusy(false) }
  const Tag = long ? 'textarea' : 'input'
  return (
    <div className="grid gap-3 border-b border-navy/10 px-5 py-4 last:border-0 lg:grid-cols-2">
      <p className="text-[14px] leading-relaxed text-ink">{source}</p>
      <div className="flex items-start gap-2">
        <Tag className="input !mt-0" rows={long ? 3 : undefined} value={value} placeholder={lang === 'en' ? source : t('Not translated yet — English is shown')}
          onChange={(e) => setValue(e.target.value)} onBlur={commit} disabled={busy} />
        {override !== undefined && <button type="button" title={t('Reset to the built-in text')} aria-label={t('Reset')} onClick={reset} className="grid h-10 w-10 shrink-0 place-items-center rounded-full border border-navy/15 hover:bg-sand-soft"><RotateCcw className="h-3.5 w-3.5" /></button>}
      </div>
    </div>
  )
}

/** Every piece of interface copy on the public site, editable per language. */
export default function Content() {
  const { overrides, refresh, t } = useI18n()
  const [lang, setLang] = useState('en')
  const [section, setSection] = useState('all')
  const [q, setQ] = useState('')
  const [notice, setNotice] = useState('')

  const rows = useMemo(() => SECTIONS.filter((s) => section === 'all' || s.name === section)
    .flatMap((s) => Object.entries(s.rows).map(([key, tr]) => ({ key, section: s.name, builtIn: lang === 'en' ? undefined : tr[COLUMN[lang]] })))
    .filter((r, i, all) => all.findIndex((x) => x.key === r.key) === i) // one row per distinct text
    .filter((r) => !q || r.key.toLowerCase().includes(q.toLowerCase()) || (overrides[lang]?.[r.key] || r.builtIn || '').toLowerCase().includes(q.toLowerCase())), [section, q, lang, overrides])

  const save = async (key, value) => {
    await api.put('/texts/', { lang, key, value })
    refresh()
    setNotice(value.trim() ? t('Saved') : t('Reset to default'))
    setTimeout(() => setNotice(''), 1800)
  }
  const edited = Object.keys(overrides[lang] || {}).length

  return (
    <div>
      <p className="max-w-3xl text-[14px] text-ink">{t('Every fixed piece of text on the public site — menus, headings, buttons, form messages and page copy — is listed here. Choose a language, edit a field and click outside it to save. Texts for tours, hotels, destinations and other listings are translated inside their own editors.')}</p>
      <div className="mt-5 flex flex-wrap items-center gap-2" role="tablist" aria-label="Language">
        {LANGS.map((l) => (
          <button key={l.code} role="tab" aria-selected={lang === l.code} onClick={() => setLang(l.code)} className={`h-10 rounded-full border px-4 text-[14px] ${lang === l.code ? 'border-navy bg-navy text-ivory' : 'border-navy/10 bg-white hover:bg-sand-soft'}`}>{l.label}</button>))}
        <span className="ml-2 font-mono text-[11px] uppercase tracking-[0.12em] text-ink">{t('{a} customised · {b} shown', { a: edited, b: rows.length })}</span>
        {notice && <span className="text-[14px] text-turquoise-deep" role="status">{notice}</span>}
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <div className="relative w-full max-w-sm"><Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder={t('Search texts')} className="h-11 w-full rounded-sm border border-navy/10 bg-white pl-10 pr-3 text-[14px] outline-none focus:border-navy" /></div>
        <select value={section} onChange={(e) => setSection(e.target.value)} className="h-11 rounded-sm border border-navy/10 bg-white px-3 text-[14px]">
          <option value="all">{t('All sections')}</option>{SECTIONS.map((s) => <option key={s.name} value={s.name}>{t(s.name)}</option>)}</select>
      </div>
      <div className="mt-5 overflow-hidden rounded-sm border border-navy/10 bg-white">
        <div className="hidden grid-cols-2 gap-3 border-b border-navy/10 px-5 py-3 font-mono text-[10px] uppercase tracking-[0.18em] text-ink lg:grid"><span>{t('English original')}</span><span>{LANGS.find((l) => l.code === lang).label}</span></div>
        {rows.map((r) => <TextRow key={`${lang}:${r.key}`} source={r.key} lang={lang} builtIn={r.builtIn} override={overrides[lang]?.[r.key]} onSave={save} />)}
        {!rows.length && <p className="p-8 text-center text-ink">{t('No texts match.')}</p>}
      </div>
    </div>
  )
}
