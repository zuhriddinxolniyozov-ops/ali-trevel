import { useState } from 'react'
import { ArrowLeft, ArrowRight, Loader2, Trash2, Upload } from 'lucide-react'
import { api } from '../api'
import { useT } from '../i18n'

/** Several photos for one listing: upload many at once, paste links, reorder with the arrows, remove with the bin. */
export default function GalleryField({ label, help, value = [], onChange }) {
  const t = useT()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [link, setLink] = useState('')
  const photos = Array.isArray(value) ? value : []

  async function pick(e) {
    const files = [...(e.target.files || [])]
    e.target.value = ''
    if (!files.length) return
    setBusy(true); setError('')
    const added = []
    for (const file of files) {
      try { added.push((await api.upload(file)).url) } catch (ex) { setError(`${file.name}: ${ex.message}`) }
    }
    if (added.length) onChange([...photos, ...added])
    setBusy(false)
  }
  const move = (i, step) => {
    const next = [...photos]
    const j = i + step
    if (j < 0 || j >= next.length) return
    ;[next[i], next[j]] = [next[j], next[i]]
    onChange(next)
  }
  const addLink = () => {
    const url = link.trim()
    if (!url) return
    onChange([...photos, url]); setLink('')
  }

  return (
    <div className="label sm:col-span-2">{label}
      <p className="mt-1 text-[12.5px] font-normal text-ink/80">{t('The first photo of the listing is the cover (above). These photos follow it in the slider, in this order.')}</p>
      {photos.length > 0 && (
        <ul className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {photos.map((src, i) => (
            <li key={`${src}-${i}`} className="overflow-hidden rounded-sm border border-navy/15 bg-white">
              <div className="relative aspect-[4/3] bg-sand-soft/60">
                <img src={src} alt="" className="h-full w-full object-cover" />
                <span className="absolute left-1.5 top-1.5 rounded-full bg-navy/70 px-2 py-0.5 font-mono text-[10px] text-ivory">{i + 2}</span>
              </div>
              <div className="flex items-center justify-between px-1.5 py-1">
                <button type="button" onClick={() => move(i, -1)} disabled={i === 0} aria-label={t('Move earlier')} className="grid h-8 w-8 place-items-center rounded-full hover:bg-sand-soft disabled:opacity-30"><ArrowLeft className="h-4 w-4" /></button>
                <button type="button" onClick={() => onChange(photos.filter((_, j) => j !== i))} aria-label={t('Remove photo')} className="grid h-8 w-8 place-items-center rounded-full text-destructive hover:bg-red-50"><Trash2 className="h-4 w-4" /></button>
                <button type="button" onClick={() => move(i, 1)} disabled={i === photos.length - 1} aria-label={t('Move later')} className="grid h-8 w-8 place-items-center rounded-full hover:bg-sand-soft disabled:opacity-30"><ArrowRight className="h-4 w-4" /></button>
              </div>
            </li>
          ))}
        </ul>
      )}
      <div className="mt-3 flex flex-wrap items-start gap-3">
        <label className="btn-outline !h-10 cursor-pointer !text-[13px]">
          {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}{busy ? t('Uploading…') : t('Upload photos')}
          <input type="file" multiple accept="image/jpeg,image/png,image/gif,image/webp" className="sr-only" onChange={pick} disabled={busy} />
        </label>
        <div className="flex min-w-[240px] flex-1 gap-2">
          <input className="input !mt-0" placeholder={t('Or paste an image link')} value={link} onChange={(e) => setLink(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addLink() } }} />
          <button type="button" onClick={addLink} className="btn-outline !h-10 !text-[13px]">{t('Add')}</button>
        </div>
      </div>
      {error && <span role="alert" className="mt-1 block text-[12px] text-destructive">{error}</span>}
      {help && <span className="mt-1 block text-[12px] font-normal text-ink/80">{help}</span>}
    </div>
  )
}
