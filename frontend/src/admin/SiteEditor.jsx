import { useCallback, useEffect, useRef, useState } from 'react'
import { ExternalLink, Globe, Monitor, RefreshCw, Smartphone, Tablet } from 'lucide-react'
import { useFetch } from '../hooks'
import { LANGS, useI18n } from '../i18n'

const DEVICES = [['desktop', Monitor, 'Desktop', '100%'], ['tablet', Tablet, 'Tablet', '820px'], ['phone', Smartphone, 'Phone', '390px']]
const PAGES = [
  ['/', 'Home page'], ['/destinations', 'Destinations'], ['/tours', 'Tours & Experiences'], ['/hotels', 'Hotels'], ['/food', 'Local Food'],
  ['/transport', 'Transport'], ['/plan', 'Plan My Trip'], ['/about', 'About Us'], ['/contact', 'Contact'], ['/partners', 'Partners'],
]

/**
 * The public website, shown exactly as visitors see it, with editing switched on.
 * It is the real site in a frame (`/?edit=1`); this page only sends it commands (mode, language, page).
 */
export default function SiteEditor() {
  const { t, lang, setLang } = useI18n()
  const frame = useRef(null)
  const [path, setPath] = useState('/')
  const [mode, setMode] = useState('edit')
  const [device, setDevice] = useState('desktop')
  const destinations = useFetch('/destinations/?all=1&raw=1', { list: true })
  const tours = useFetch('/tours/?all=1&raw=1', { list: true })

  const send = useCallback((message) => frame.current?.contentWindow?.postMessage({ ali: 'edit', ...message }, window.location.origin), [])

  useEffect(() => {
    const onMessage = (e) => {
      if (e.origin !== window.location.origin || e.source !== frame.current?.contentWindow || e.data?.ali !== 'edit') return
      if (e.data.type === 'path') setPath(e.data.path)
      if (e.data.type === 'ready') { send({ type: 'mode', mode }); send({ type: 'lang', lang }) }
    }
    window.addEventListener('message', onMessage)
    return () => window.removeEventListener('message', onMessage)
  }, [send, mode, lang])

  useEffect(() => { send({ type: 'mode', mode }) }, [mode, send])
  useEffect(() => { send({ type: 'lang', lang }) }, [lang, send])

  const known = PAGES.some(([p]) => p === path) || destinations.data.some((d) => path === `/destinations/${d.slug}`) || tours.data.some((x) => path === `/tours/${x.slug}`)
  const width = DEVICES.find(([k]) => k === device)[3]
  const segment = (on) => `h-9 rounded-full px-4 text-[13px] font-medium transition-colors ${on ? 'bg-navy text-ivory' : 'text-navy hover:bg-sand-soft'}`

  return (
    <div className="flex h-full flex-col">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 border-b border-navy/10 bg-white px-4 py-2.5">
        <div className="flex rounded-full border border-navy/15 p-0.5" role="tablist" aria-label={t('Site editor')}>
          <button role="tab" aria-selected={mode === 'edit'} className={segment(mode === 'edit')} onClick={() => setMode('edit')}>{t('Edit')}</button>
          <button role="tab" aria-selected={mode === 'browse'} className={segment(mode === 'browse')} onClick={() => setMode('browse')}>{t('Browse')}</button>
        </div>
        <label className="flex items-center gap-2 text-[13px] text-ink">{t('Page')}
          <select value={known ? path : '__other'} onChange={(e) => send({ type: 'goto', path: e.target.value })} className="h-9 max-w-[220px] rounded-full border border-navy/15 bg-white px-3 text-[13px] text-navy">
            {!known && <option value="__other" disabled>{path}</option>}
            {PAGES.map(([p, label]) => <option key={p} value={p}>{t(label)}</option>)}
            {destinations.data.length > 0 && <optgroup label={t('Destinations')}>{destinations.data.map((d) => <option key={d.slug} value={`/destinations/${d.slug}`}>{d.name}</option>)}</optgroup>}
            {tours.data.length > 0 && <optgroup label={t('Tours & Experiences')}>{tours.data.map((x) => <option key={x.slug} value={`/tours/${x.slug}`}>{x.title}</option>)}</optgroup>}
          </select>
        </label>
        <label className="flex items-center gap-1.5 text-[13px] text-ink"><Globe className="h-4 w-4" aria-hidden="true" /><span className="sr-only">{t('Select language')}</span>
          <select value={lang} onChange={(e) => setLang(e.target.value)} className="h-9 rounded-full border border-navy/15 bg-white px-3 text-[13px] text-navy">
            {LANGS.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}</select></label>
        <div className="flex rounded-full border border-navy/15 p-0.5">
          {DEVICES.map(([k, Icon, label]) => (
            <button key={k} title={t(label)} aria-label={t(label)} aria-pressed={device === k} onClick={() => setDevice(k)} className={`grid h-9 w-10 place-items-center rounded-full ${device === k ? 'bg-navy text-ivory' : 'text-navy hover:bg-sand-soft'}`}><Icon className="h-4 w-4" /></button>
          ))}
        </div>
        <div className="ml-auto flex items-center gap-2">
          <button onClick={() => send({ type: 'reload' })} className="inline-flex h-9 items-center gap-1.5 rounded-full border border-navy/15 px-3.5 text-[13px] hover:bg-sand-soft"><RefreshCw className="h-3.5 w-3.5" />{t('Reload')}</button>
          <a href={path} target="_blank" rel="noreferrer" className="inline-flex h-9 items-center gap-1.5 rounded-full border border-navy/15 px-3.5 text-[13px] hover:bg-sand-soft"><ExternalLink className="h-3.5 w-3.5" />{t('Open site in a new tab')}</a>
        </div>
        <p className="basis-full text-[12.5px] text-ink">{mode === 'edit'
          ? t('Click any text or photo to edit it. Use the dashed “+” cards to add new items. Switch to Browse to move around the site.')
          : t('Browse mode: links work as on the live site. Switch to Edit to change things.')}</p>
      </div>
      <div className="flex min-h-0 flex-1 justify-center overflow-auto bg-sand-soft/60 p-0 sm:p-4">
        <iframe ref={frame} title={t('Site editor')} src="/?edit=1" style={{ width }} className={`h-full min-h-[560px] max-w-full bg-white ${device === 'desktop' ? '' : 'rounded-md border border-navy/15 shadow-xl'}`} />
      </div>
    </div>
  )
}
