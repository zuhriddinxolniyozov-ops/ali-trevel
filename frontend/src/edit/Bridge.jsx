import { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Loader2, Upload } from 'lucide-react'
import { api } from '../api'
import { useI18n } from '../i18n'
import { STRINGS } from '../strings'
import RecordEditor, { FORMS } from '../admin/Editor'
import { useEdit } from './context'
import { findImageRecord, findSetting, findText, norm } from './registry'

const RECORD_LABEL = { tours: 'tour', destinations: 'destination', hotels: 'hotel', food: 'experience', transport: 'transport option' }
const escapeRe = (s) => s.replace(/[.*+?^$|()[\]\\]/g, '\\$&')

/** Which interface string renders as this text? Placeholders such as {name} match any text. */
function findUiKey(text, t) {
  const keys = Object.keys(STRINGS)
  const exact = keys.find((k) => norm(t(k)) === text)
  if (exact) return exact
  return keys.find((k) => {
    const value = t(k)
    return value.includes('{') && new RegExp(`^${value.split(/\{\w+\}/).map(escapeRe).join('(.+?)')}$`).test(text)
  })
}

function resolveText(text, ctx, t) {
  const matches = findText(text, ctx)
  if (matches.length) return { type: 'db', matches }
  const key = findUiKey(text, t)
  if (key) return { type: 'ui', key }
  const setting = findSetting(text)
  if (setting) return { type: 'setting', ...setting }
  const global = ctx ? [] : findText(text, null)
  return global.length === 1 ? { type: 'db', matches: global } : { type: 'none' }
}

function textNodeAt(x, y) {
  const pos = document.caretPositionFromPoint?.(x, y)
  const node = pos?.offsetNode || document.caretRangeFromPoint?.(x, y)?.startContainer
  if (node?.nodeType !== 3 || !node.textContent.trim()) return null
  const range = document.createRange()
  range.selectNodeContents(node)
  const hit = [...range.getClientRects()].some((r) => x >= r.left - 4 && x <= r.right + 4 && y >= r.top - 4 && y <= r.bottom + 4)
  return hit ? node : null
}

const hasOwnText = (el) => [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())
const fieldLabel = (resource, field) => FORMS[resource].sections.flatMap((s) => s.fields).find((f) => f.k === field)?.label || field

function place(rect, width = 400, height = 300) {
  return {
    top: Math.max(8, Math.min(rect.bottom + 10, window.innerHeight - height)),
    left: Math.max(12, Math.min(rect.left, window.innerWidth - width - 12)),
    width,
  }
}

async function saveRecordText(match, lang, value) {
  const raw = await api.get(`/${match.resource}/${match.slug}/?all=1&raw=1`)
  const isList = match.index !== undefined
  const replaceItem = (list) => {
    const next = [...list]
    const fee = match.field === 'route' ? String(next[match.index] ?? '').split('|')[1]?.trim() : ''
    next[match.index] = fee ? `${value} | ${fee}` : value
    return next
  }
  const body = {}
  if (lang === 'en') {
    body[match.field] = isList ? replaceItem(raw[match.field] || []) : value
  } else {
    const i18n = JSON.parse(JSON.stringify(raw.i18n || {}))
    const entry = (i18n[lang] ||= {})
    entry[match.field] = isList ? replaceItem(entry[match.field]?.length ? entry[match.field] : raw[match.field] || []) : value
    body.i18n = i18n
  }
  await api.patch(`/${match.resource}/${match.slug}/`, body)
}

function Popup({ rect, width, height = 340, children, onClose }) {
  return (
    <div data-edit-ignore style={{ position: 'fixed', zIndex: 90, maxHeight: 'calc(100vh - 16px)', overflowY: 'auto', ...place(rect, width, height) }} className="rounded-md border border-navy/15 bg-white p-4 text-[14px] text-navy shadow-2xl">
      {children}
      <button type="button" onClick={onClose} aria-label="Close" className="absolute right-2 top-2 grid h-7 w-7 place-items-center rounded-full text-ink hover:bg-sand-soft">×</button>
    </div>
  )
}

function TextPopup({ popup, onClose }) {
  const { t, lang, refresh } = useI18n()
  const { bump, openRecord } = useEdit()
  const { text, target, ctx } = popup
  const [choice, setChoice] = useState(0)
  const [value, setValue] = useState(target.type === 'ui' ? t(target.key) : text)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const langName = lang.toUpperCase()

  async function run(job) {
    setBusy(true); setError('')
    try { await job(); onClose() } catch (ex) { setError(ex.message); setBusy(false) }
  }
  const save = () => run(async () => {
    if (target.type === 'ui') { await api.put('/texts/', { lang, key: target.key, value }); refresh() }
    else if (target.type === 'db') { await saveRecordText(target.matches[choice], lang, value.trim()); bump() }
    else if (target.type === 'setting') { const cur = await api.get('/site-content/'); await api.put('/site-content/', { ...cur, [target.field]: value.trim() }); bump() }
  })
  const reset = () => run(async () => { await api.put('/texts/', { lang, key: target.key, value: '' }); refresh() })

  if (target.type === 'none') {
    const [resource, slug] = (ctx || '').split(':')
    return (
      <Popup rect={popup.rect} onClose={onClose}>
        <p className="pr-6 text-[13px] leading-relaxed text-ink">{t('This text is generated automatically and cannot be edited directly.')}</p>
        {ctx && <button type="button" className="btn-outline mt-3 !h-9 !px-4 text-[12px]" onClick={() => { onClose(); openRecord(resource, slug) }}>{t(`Edit ${RECORD_LABEL[resource]}`)}</button>}
      </Popup>
    )
  }
  const match = target.type === 'db' ? target.matches[choice] : null
  const source = target.type === 'ui' ? t('Interface text') : target.type === 'setting' ? t('Contact details') : `${t(RECORD_LABEL[match.resource].replace(/^./, (c) => c.toUpperCase()))}`
  return (
    <Popup rect={popup.rect} onClose={onClose}>
      <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink">{source} · {langName}</p>
      {target.type === 'db' && target.matches.length > 1 && (
        <select className="input !mt-2 !py-1.5 text-[13px]" value={choice} onChange={(e) => setChoice(Number(e.target.value))}>
          {target.matches.map((m, i) => <option key={i} value={i}>{t(fieldLabel(m.resource, m.field))}</option>)}
        </select>
      )}
      {target.type === 'db' && target.matches.length === 1 && <p className="mt-1 text-[12px] text-ink">{t(fieldLabel(match.resource, match.field))}</p>}
      <textarea autoFocus rows={Math.min(8, Math.max(2, Math.ceil(value.length / 48)))} value={value} onChange={(e) => setValue(e.target.value)} className="input !mt-2" />
      {target.type === 'ui' && /\{\w+\}/.test(value) && <p className="mt-1 text-[12px] text-ink">{t('Keep placeholders such as {name} unchanged.')}</p>}
      {error && <p role="alert" className="mt-2 text-[12px] text-destructive">{error}</p>}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <button type="button" disabled={busy || !value.trim()} onClick={save} className="btn-primary !h-9 !px-5 text-[12px]">{busy && <Loader2 className="h-3.5 w-3.5 animate-spin" />}{t('Save')}</button>
        <button type="button" onClick={onClose} className="btn-outline !h-9 !px-4 text-[12px]">{t('Cancel')}</button>
        {target.type === 'ui' && <button type="button" disabled={busy} onClick={reset} className="ml-auto text-[12px] text-ink underline">{t('Reset to default')}</button>}
      </div>
    </Popup>
  )
}

function ImagePopup({ popup, onClose }) {
  const { t, refresh } = useI18n()
  const { bump } = useEdit()
  const record = findImageRecord(popup.src, popup.ctx)
  const mode = record ? 'record' : popup.orig ? 'static' : 'none'
  const [url, setUrl] = useState(popup.src)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function upload(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setBusy(true); setError('')
    try { setUrl((await api.upload(file)).url) } catch (ex) { setError(ex.message) } finally { setBusy(false); e.target.value = '' }
  }
  async function save(value = url) {
    setBusy(true); setError('')
    try {
      if (mode === 'record') { await api.patch(`/${record.resource}/${record.slug}/`, { image_url: value }); bump() }
      else { await api.put('/texts/', { lang: 'en', key: `image:${popup.orig}`, value: value === popup.orig ? '' : value }); refresh() }
      onClose()
    } catch (ex) { setError(ex.message); setBusy(false) }
  }

  return (
    <Popup rect={popup.rect} width={380} height={460} onClose={onClose}>
      {mode === 'none' ? <p className="pr-6 text-[13px] text-ink">{t('This image is part of a fixed element and cannot be changed here.')}</p> : (
        <>
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink">{t('Photo')}</p>
          <img src={url} alt="" className="mt-2 h-32 w-full rounded-sm bg-sand-soft object-cover" data-edit-ignore />
          <label className="btn-outline mt-3 !h-9 w-full cursor-pointer !text-[12px]">
            {busy ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Upload className="h-3.5 w-3.5" />}{busy ? t('Uploading…') : t('Upload photo')}
            <input type="file" accept="image/jpeg,image/png,image/gif,image/webp" className="sr-only" onChange={upload} disabled={busy} />
          </label>
          <label className="label mt-3">{t('Or paste an image link')}<input className="input !mt-1" value={url} onChange={(e) => setUrl(e.target.value)} /></label>
          {error && <p role="alert" className="mt-2 text-[12px] text-destructive">{error}</p>}
          <div className="mt-3 flex items-center gap-2">
            <button type="button" disabled={busy || !url.trim()} onClick={() => save()} className="btn-primary !h-9 !px-5 text-[12px]">{t('Save')}</button>
            <button type="button" onClick={onClose} className="btn-outline !h-9 !px-4 text-[12px]">{t('Cancel')}</button>
            {mode === 'static' && <button type="button" disabled={busy} onClick={() => save(popup.orig)} className="ml-auto text-[12px] text-ink underline">{t('Reset to default')}</button>}
          </div>
        </>
      )}
    </Popup>
  )
}

function RecordModal() {
  const { modal, closeModal, bump } = useEdit()
  const [record, setRecord] = useState(undefined) // undefined = loading, null = new
  useEffect(() => {
    if (!modal) return
    if (!modal.slug) { setRecord(null); return }
    setRecord(undefined)
    api.get(`/${modal.resource}/${modal.slug}/?all=1&raw=1`).then(setRecord).catch(closeModal)
  }, [modal, closeModal])
  if (!modal) return null
  return (
    <div data-edit-ignore className="fixed inset-0 z-[100] overflow-y-auto bg-navy/60 p-4 sm:p-8">
      <div className="mx-auto max-w-4xl">
        {record === undefined
          ? <div className="grid place-items-center rounded-md bg-white p-16"><Loader2 className="h-6 w-6 animate-spin text-navy" /></div>
          : <RecordEditor key={`${modal.resource}:${modal.slug}`} resource={modal.resource} label={RECORD_LABEL[modal.resource]} record={record} preset={modal.preset}
              onDone={(saved) => { closeModal(); if (saved) bump() }} />}
      </div>
    </div>
  )
}

/** Click, hover and message plumbing for the site editor frame. */
export default function Bridge() {
  const edit = useEdit()
  const { t, setLang } = useI18n()
  const nav = useNavigate()
  const loc = useLocation()
  const [popup, setPopup] = useState(null)
  const live = useRef({})
  live.current = { edit, t, setLang, nav }

  useEffect(() => {
    let hovered = null
    const clearHover = () => { hovered?.classList.remove('ali-edit-hover'); hovered = null }
    const skip = (el) => !(el instanceof Element) || el.closest('[data-edit-ignore]')

    const onClick = (e) => {
      const { edit: ed, t: tr } = live.current
      if (!ed.editing || skip(e.target)) return
      e.preventDefault(); e.stopPropagation()
      clearHover()
      const at = { bottom: e.clientY + 8, left: e.clientX - 24 }
      const node = textNodeAt(e.clientX, e.clientY)
      const beneath = document.elementsFromPoint(e.clientX, e.clientY)
      const img = !node && (e.target.closest('img') || beneath.find((el) => el.tagName === 'IMG'))
      if (img) {
        setPopup({ kind: 'image', rect: at, src: img.currentSrc || img.src, orig: img.dataset.orig, ctx: img.closest('[data-edit-record]')?.dataset.editRecord })
        return
      }
      const ctx = (node?.parentElement || e.target).closest('[data-edit-record]')?.dataset.editRecord
      if (node) {
        const text = norm(node.textContent)
        setPopup({ kind: 'text', rect: at, text, ctx, target: resolveText(text, ctx, tr) })
      } else if (ctx) {
        const [resource, slug] = ctx.split(':')
        ed.openRecord(resource, slug)
      } else setPopup(null)
    }
    const onOver = (e) => {
      if (!live.current.edit.editing || skip(e.target)) { clearHover(); return }
      const el = e.target
      const next = el.closest('img') || (hasOwnText(el) ? el : null)
      if (next === hovered) return
      clearHover()
      if (next) { next.classList.add('ali-edit-hover'); hovered = next }
    }
    const onMessage = (e) => {
      if (e.origin !== window.location.origin || e.source !== window.parent || e.data?.ali !== 'edit') return
      const { edit: ed, setLang: setL, nav: go } = live.current
      const m = e.data
      if (m.type === 'mode') ed.setMode(m.mode)
      else if (m.type === 'lang') setL(m.lang)
      else if (m.type === 'goto') go(m.path)
      else if (m.type === 'reload') window.location.reload()
    }
    const onKey = (e) => { if (e.key === 'Escape') setPopup(null) }

    document.addEventListener('click', onClick, true)
    document.addEventListener('mouseover', onOver, true)
    window.addEventListener('message', onMessage)
    window.addEventListener('keydown', onKey)
    window.parent.postMessage({ ali: 'edit', type: 'ready' }, window.location.origin)
    return () => {
      document.removeEventListener('click', onClick, true)
      document.removeEventListener('mouseover', onOver, true)
      window.removeEventListener('message', onMessage)
      window.removeEventListener('keydown', onKey)
      clearHover()
    }
  }, [])

  useEffect(() => { window.parent.postMessage({ ali: 'edit', type: 'path', path: loc.pathname }, window.location.origin) }, [loc.pathname])
  useEffect(() => { if (!edit.editing) setPopup(null) }, [edit.editing])
  useEffect(() => { setPopup(null) }, [loc.pathname])

  return (
    <>
      {popup?.kind === 'text' && <TextPopup key={`${popup.text}:${popup.rect.bottom}`} popup={popup} onClose={() => setPopup(null)} />}
      {popup?.kind === 'image' && <ImagePopup key={popup.src} popup={popup} onClose={() => setPopup(null)} />}
      <RecordModal />
    </>
  )
}
