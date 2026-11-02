import { useEffect, useState } from 'react'
import { api } from '../api'
import { useFetch } from '../hooks'
import { LANGS, useT } from '../i18n'
import { Spinner } from '../components/ui'
import LegalText from '../components/LegalText'

const PAGES = [['privacy', 'Privacy Policy'], ['terms', 'Terms and Conditions'], ['cancellation', 'Cancellation Policy']]
const HELP = '## Heading\n### Smaller heading\n- Bullet point\n1. Numbered step\n**bold text**   [link text](https://example.com)\n(Every new line is a new paragraph.)'

function Editor({ slug }) {
  const t = useT()
  const { data: page, reload } = useFetch(`/legal/${slug}/?raw=1`)
  const [lang, setLang] = useState('en')
  const [draft, setDraft] = useState({})
  const [preview, setPreview] = useState(false)
  const [saved, setSaved] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!page) return
    const read = (code) => (code === 'en' ? { title: page.title, body: page.body } : { title: page.i18n?.[code]?.title || '', body: page.i18n?.[code]?.body || '' })
    setDraft(Object.fromEntries(LANGS.map((l) => [l.code, read(l.code)])))
  }, [page])
  if (!page || !draft[lang]) return <Spinner />

  const cur = draft[lang]
  const set = (k, v) => { setSaved(''); setDraft((p) => ({ ...p, [lang]: { ...p[lang], [k]: v } })) }
  const filled = (code) => draft[code]?.body?.trim()
  async function save() {
    setError('')
    const i18n = Object.fromEntries(LANGS.slice(1).map((l) => [l.code, draft[l.code]]).filter(([, v]) => v.title?.trim() || v.body?.trim()))
    try {
      await api.patch(`/legal/${slug}/`, { title: draft.en.title, body: draft.en.body, i18n, updated: new Date().toISOString().slice(0, 10) })
      setSaved(t('Saved — the page now shows today’s date as “last updated”.')); reload()
    } catch (ex) { setError(ex.message) }
  }

  return (
    <div className="mt-5">
      <div className="flex flex-wrap items-center gap-2" role="tablist" aria-label={t('Language')}>
        {LANGS.map((l) => (
          <button key={l.code} role="tab" aria-selected={lang === l.code} onClick={() => setLang(l.code)} className={`h-10 rounded-full border px-4 text-[14px] ${lang === l.code ? 'border-navy bg-navy text-ivory' : 'border-navy/10 bg-white hover:bg-sand-soft'}`}>
            {l.label}{l.code !== 'en' && filled(l.code) && <span className="ml-1.5 inline-block h-1.5 w-1.5 rounded-full bg-turquoise align-middle" />}</button>))}
        <span className="ml-auto text-[13px] text-ink">{t('Last updated')}: {page.updated}</span>
      </div>
      {lang !== 'en' && !filled(lang) && (
        <p className="mt-3 rounded-sm bg-sand-soft/70 p-3 text-[13px] text-ink">{t('This language is empty, so visitors see the English text. Write a translation below, or start from the English text.')}{' '}
          <button className="text-turquoise-deep underline" onClick={() => setDraft((p) => ({ ...p, [lang]: { ...p.en } }))}>{t('Copy the English text here')}</button></p>)}

      <div className="mt-4 grid gap-5 xl:grid-cols-2">
        <div>
          <label className="label">{t('Title')}<input className="mt-1 h-10 w-full rounded-sm border border-navy/15 bg-white px-3 text-[14px] outline-none focus:border-navy" value={cur.title} onChange={(e) => set('title', e.target.value)} /></label>
          <label className="label mt-3">{t('Text')}
            <textarea rows={28} spellCheck className="mt-1 w-full rounded-sm border border-navy/15 bg-white p-3 font-mono text-[13px] leading-relaxed outline-none focus:border-navy" value={cur.body} onChange={(e) => set('body', e.target.value)} /></label>
          <details className="mt-2 text-[13px] text-ink"><summary className="cursor-pointer">{t('How to format the text')}</summary><pre className="mt-2 whitespace-pre-wrap rounded-sm bg-sand-soft/60 p-3 text-[12.5px]">{HELP}</pre></details>
        </div>
        <div className="min-w-0">
          <button className="mb-3 text-[13px] text-turquoise-deep underline xl:hidden" onClick={() => setPreview((v) => !v)}>{preview ? t('Hide preview') : t('Show preview')}</button>
          <div className={`rounded-sm border border-navy/10 bg-white p-6 ${preview ? '' : 'hidden xl:block'}`}>
            <p className="eyebrow">{t('Preview')}</p>
            <h2 className="display-lg mt-2 !text-[32px]">{cur.title}</h2>
            <div className="mt-4"><LegalText body={cur.body} /></div>
          </div>
        </div>
      </div>
      {error && <p role="alert" className="mt-3 text-[13px] text-destructive">{error}</p>}
      <div className="mt-5 flex items-center gap-3"><button className="btn-primary" onClick={save}>{t('Save changes')}</button>{saved && <span role="status" className="text-[13px] text-turquoise-deep">{saved}</span>}</div>
    </div>
  )
}

/** Edit the privacy policy, terms and cancellation policy in every language. */
export default function LegalAdmin() {
  const t = useT()
  const [slug, setSlug] = useState('privacy')
  return (
    <div>
      <p className="max-w-3xl text-[14px] text-ink">{t('These three pages are shown to visitors under Privacy Policy, Terms and Conditions and Cancellation Policy in the footer. Replace the details in [square brackets] with your company’s details, and have a lawyer review the texts before you rely on them.')}</p>
      <div className="mt-4 flex flex-wrap gap-2">{PAGES.map(([k, l]) => <button key={k} onClick={() => setSlug(k)} className={`h-10 rounded-full border px-5 text-[14px] ${slug === k ? 'border-navy bg-navy text-ivory' : 'border-navy/10 bg-white hover:bg-sand-soft'}`}>{t(l)}</button>)}</div>
      <Editor key={slug} slug={slug} />
    </div>
  )
}
