import { ImagePlus, Pencil, Plus } from 'lucide-react'
import { useT } from '../i18n'
import { useEdit } from './context'

/** A blank card shown in the empty slot of a grid while editing: click it, fill in the form, upload a photo. */
export function AddCard({ resource, preset, label }) {
  const { editing, openRecord } = useEdit()
  const t = useT()
  if (!editing) return null
  return (
    <button type="button" data-edit-ignore onClick={() => openRecord(resource, null, preset)}
      className="group flex h-full min-h-[360px] w-full flex-col overflow-hidden rounded-[4px] border-2 border-dashed border-turquoise-deep/50 bg-sand-soft/30 text-left transition-colors hover:border-navy hover:bg-sand-soft/70">
      <span className="grid aspect-[4/3] w-full place-items-center bg-white/70 text-turquoise-deep"><ImagePlus className="h-10 w-10" strokeWidth={1.4} /></span>
      <span className="flex flex-1 flex-col gap-3 p-5">
        <span className="inline-flex items-center gap-2 font-heading text-[23px] leading-tight text-navy">
          <span className="grid h-8 w-8 place-items-center rounded-full bg-navy text-ivory transition-transform group-hover:rotate-90"><Plus className="h-4 w-4" /></span>{t(label)}
        </span>
        <span className="text-[14px] leading-relaxed text-ink">{t('Fill in a blank template, upload a photo and publish.')}</span>
        <span className="mt-auto space-y-2" aria-hidden="true"><span className="block h-2.5 w-3/4 rounded bg-navy/10" /><span className="block h-2.5 w-1/2 rounded bg-navy/10" /></span>
      </span>
    </button>
  )
}

/** Small "Edit" pill in the corner of a record card (the card must be `relative`). */
export function EditButton({ resource, record }) {
  const { editing, openRecord } = useEdit()
  const t = useT()
  if (!editing || !record) return null
  return (
    <button type="button" data-edit-ignore onClick={() => openRecord(resource, record.slug)}
      className="absolute right-3 top-3 z-20 inline-flex items-center gap-1.5 rounded-full bg-navy px-3 py-1.5 text-[12px] font-medium text-ivory shadow-lg hover:bg-navy-deep">
      <Pencil className="h-3.5 w-3.5" />{t('Edit')}
    </button>
  )
}

/** Full-width "edit this page's record" bar for detail pages. */
export function EditRecordBar({ resource, record, label }) {
  const { editing, openRecord } = useEdit()
  const t = useT()
  if (!editing || !record) return null
  return (
    <div className="shell pt-6" data-edit-ignore>
      <button type="button" onClick={() => openRecord(resource, record.slug)}
        className="inline-flex items-center gap-2 rounded-full border border-turquoise-deep/50 bg-sand-soft px-4 py-2 text-[13px] font-medium text-navy hover:border-navy">
        <Pencil className="h-4 w-4" />{t(label)}
      </button>
    </div>
  )
}
