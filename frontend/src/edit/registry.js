import { setResponseHook } from '../api'
import { EDIT_SESSION } from './context'

/**
 * Remembers every catalogue record the page has loaded, so a click on rendered text can be traced back to the
 * record and field that produced it.
 */
const records = new Map() // "tours:slug" -> { resource, slug, data }
let settings = null

export const TEXT_FIELDS = {
  tours: { text: ['title', 'summary', 'description', 'category', 'duration_label', 'group_type', 'destination_name', 'guide', 'meeting_point'], list: ['highlights', 'included', 'excluded', 'route'] },
  destinations: { text: ['name', 'region', 'summary', 'description', 'suggested_duration'], list: ['activities', 'highlights'] },
  hotels: { text: ['name', 'summary', 'description', 'destination_name'], list: ['amenities'] },
  food: { text: ['name', 'summary', 'kind', 'destination_name'], list: [] },
  transport: { text: ['name', 'vehicle', 'summary'], list: [] },
}
export const SETTING_FIELDS = ['email', 'phone_primary', 'phone_secondary', 'address', 'hours']

export const norm = (s) => String(s ?? '').replace(/\s+/g, ' ').trim()
const absolute = (u) => { try { return new URL(u, window.location.href).href } catch { return String(u) } }

function index(path, data) {
  if (path.includes('raw=1')) return // raw responses are untranslated; they would mislabel rendered text
  const m = path.match(/^\/(tours|destinations|hotels|food|transport)\//)
  if (m) {
    const rows = Array.isArray(data) ? data : data?.results ?? (data?.slug ? [data] : [])
    rows.forEach((r) => r?.slug && records.set(`${m[1]}:${r.slug}`, { resource: m[1], slug: r.slug, data: r }))
  } else if (path.startsWith('/site-content/') && data) settings = data
}
if (EDIT_SESSION) setResponseHook(index)

export const getRecord = (ctx) => records.get(ctx)

/** Where did this text come from? Looks in the record around the click first, then across everything loaded. */
export function findText(text, ctx) {
  const found = []
  const scan = ({ resource, slug, data }) => {
    const spec = TEXT_FIELDS[resource]
    spec.text.forEach((field) => { if (norm(data[field]) === text) found.push({ resource, slug, field }) })
    spec.list.forEach((field) => (data[field] || []).forEach((item, index) => {
      const shown = field === 'route' ? String(item).split('|')[0] : item
      if (norm(shown) === text) found.push({ resource, slug, field, index })
    }))
  }
  if (ctx && records.has(ctx)) scan(records.get(ctx))
  if (!found.length && !ctx) records.forEach(scan)
  return found
}

export function findSetting(text) {
  const field = settings && SETTING_FIELDS.find((f) => norm(settings[f]) === text)
  return field ? { field } : null
}

/** The record an <img> belongs to, matched by its photo URL. */
export function findImageRecord(src, ctx) {
  const same = (rec) => rec.data.image_url && absolute(rec.data.image_url) === src
  if (ctx && records.has(ctx) && same(records.get(ctx))) return records.get(ctx)
  for (const rec of records.values()) if (same(rec)) return rec
  return null
}
