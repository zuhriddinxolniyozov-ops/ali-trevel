import { useEffect, useState } from 'react'
import { biggestGroup, useGroupTiers } from '../groupPricing'
import { ArrowDown, ArrowUp, Gift, Languages, Loader2, Plus, Trash2, Upload } from 'lucide-react'
import { api } from '../api'
import { useFetch, useUploads } from '../hooks'
import { LANGS, useT } from '../i18n'
import { cap } from '../pages/Auth'
import { CostsField, ItineraryField } from './PlanFields'
import GalleryField from './GalleryField'

/** Photo field: preview, upload from the computer, or paste a link. */
function ImageField({ label, help, value, onChange }) {
  const t = useT()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function pick(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setBusy(true); setError('')
    try { onChange((await api.upload(file)).url) } catch (ex) { setError(ex.message) } finally { setBusy(false); e.target.value = '' }
  }
  return (
    <div className="label sm:col-span-2">{label}
      <div className="mt-1.5 flex flex-wrap items-start gap-4">
        <div className="grid h-28 w-44 shrink-0 place-items-center overflow-hidden rounded-sm border border-navy/15 bg-sand-soft/60">
          {value ? <img src={value} alt="" className="h-full w-full object-cover" /> : <span className="px-2 text-center text-[11px] text-ink">{t('No photo yet')}</span>}
        </div>
        <div className="min-w-[240px] flex-1">
          <label className="btn-outline !h-10 cursor-pointer !text-[13px]">
            {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}{busy ? t('Uploading…') : value ? t('Replace photo') : t('Upload photo')}
            <input type="file" accept="image/*" className="sr-only" onChange={pick} disabled={busy} />
          </label>
          <input className="input" placeholder={t('Or paste an image link')} value={value ?? ''} onChange={(e) => onChange(e.target.value)} />
          {busy && <UploadBar />}
          {error && <span role="alert" className="mt-1 block text-[12px] text-destructive">{t(error)}</span>}
          {help && <span className="mt-1 block text-[12px] font-normal text-ink/80">{help}</span>}
        </div>
      </div>
    </div>
  )
}

/** "Uploading the photo… 45%" with a bar: shown while a photo travels to the server. */
export function UploadBar() {
  const t = useT()
  const { percent } = useUploads()
  return (
    <span role="status" className="mt-2 block font-normal">
      <span className="text-[12.5px] text-turquoise-deep">{t('Uploading the photo… {n}%', { n: percent })} · {t('Please wait, do not leave the page.')}</span>
      <span className="mt-1 block h-1.5 w-full overflow-hidden rounded-full bg-navy/10"><span className="block h-full rounded-full bg-turquoise-deep transition-all" style={{ width: `${Math.max(4, percent)}%` }} /></span>
    </span>
  )
}


const BONUS_TAGS = [['bonus', 'Bonus'], ['exclusive', 'Exclusive'], ['gift', 'Gift']]
const BONUS_LANGS = LANGS.slice(1)

/** The special bonuses of a tour: each with a title, a story, a duration, a tag, photos and its own translations. */
function BonusesField({ label, help, value, onChange }) {
  const t = useT()
  const [open, setOpen] = useState({})   // bonus index -> language whose translation is open
  const list = Array.isArray(value) ? value : []
  const put = (i, patch) => onChange(list.map((b, j) => (j === i ? { ...b, ...patch } : b)))
  const putLang = (i, code, patch) => put(i, { i18n: { ...(list[i].i18n || {}), [code]: { ...(list[i].i18n?.[code] || {}), ...patch } } })
  const move = (i, by) => { const next = [...list]; [next[i], next[i + by]] = [next[i + by], next[i]]; onChange(next) }
  const small = 'grid h-9 w-9 shrink-0 place-items-center rounded-full border border-navy/15 text-navy hover:bg-sand-soft disabled:opacity-30'
  return (
    <div className="label sm:col-span-2">{label}
      {help && <span className="mt-1 block text-[12px] font-normal text-ink/80">{help}</span>}
      <div className="mt-3 space-y-5 font-normal">
        {list.map((b, i) => (
          <div key={i} className="rounded-[12px] border border-[#e8c36a]/60 bg-[#fffbf0] p-4">
            <div className="flex items-center justify-between gap-2">
              <p className="inline-flex items-center gap-2 text-[14px] font-semibold text-[#9a6b00]"><Gift className="h-4 w-4" />{t('Bonus')} {i + 1}</p>
              <div className="flex gap-1.5">
                <button type="button" className={small} aria-label={t('Move up')} disabled={i === 0} onClick={() => move(i, -1)}><ArrowUp className="h-4 w-4" /></button>
                <button type="button" className={small} aria-label={t('Move down')} disabled={i === list.length - 1} onClick={() => move(i, 1)}><ArrowDown className="h-4 w-4" /></button>
                <button type="button" className={`${small} border-red-200 text-destructive hover:bg-red-50`} aria-label={t('Delete')} onClick={() => { if (window.confirm(t('Delete this bonus?'))) onChange(list.filter((_, j) => j !== i)) }}><Trash2 className="h-4 w-4" /></button>
              </div>
            </div>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <label className="label sm:col-span-2">{t('Bonus title')} <span className="text-destructive">*</span><input className="input" maxLength={120} placeholder={t('For example: Visit to the house-museum of Islam Karimov')} value={b.title || ''} onChange={(e) => put(i, { title: e.target.value })} /></label>
              <label className="label">{t('Duration')}<input className="input" maxLength={60} placeholder={t('About 1 hour')} value={b.duration || ''} onChange={(e) => put(i, { duration: e.target.value })} /></label>
              <label className="label">{t('Label on the photo')}<select className="input" value={b.tag || 'bonus'} onChange={(e) => put(i, { tag: e.target.value })}>{BONUS_TAGS.map(([k, l]) => <option key={k} value={k}>{t(l)}</option>)}</select></label>
              <label className="label sm:col-span-2">{t('What the traveller sees and does')}<textarea rows={4} maxLength={2000} className="input" value={b.text || ''} onChange={(e) => put(i, { text: e.target.value })} /></label>
              <ImageField label={t('Main photo')} value={b.image || ''} onChange={(v) => put(i, { image: v })} />
              <GalleryField label={t('More photos')} value={b.gallery || []} onChange={(v) => put(i, { gallery: v })} />
            </div>
            <div className="mt-3">
              <p className="flex flex-wrap items-center gap-1.5 text-[12.5px] text-ink"><Languages className="h-4 w-4" />{t('Translations')}:
                {BONUS_LANGS.map((l) => {
                  const done = b.i18n?.[l.code]?.title
                  return <button key={l.code} type="button" onClick={() => setOpen((o) => ({ ...o, [i]: o[i] === l.code ? null : l.code }))}
                    className={`rounded-full border px-2.5 py-1 text-[11px] uppercase tracking-[0.08em] ${open[i] === l.code ? 'border-navy bg-navy text-ivory' : 'border-navy/15 text-navy/75'}`}>{l.code}{done && <span className="ml-1 inline-block h-1.5 w-1.5 rounded-full bg-turquoise align-middle" />}</button>
                })}</p>
              {open[i] && (
                <div className="mt-3 grid gap-3 rounded-sm bg-white p-3 sm:grid-cols-2">
                  <label className="label sm:col-span-2">{t('Bonus title')} ({open[i].toUpperCase()})<input className="input" maxLength={120} placeholder={b.title || ''} value={b.i18n?.[open[i]]?.title || ''} onChange={(e) => putLang(i, open[i], { title: e.target.value })} /></label>
                  <label className="label">{t('Duration')} ({open[i].toUpperCase()})<input className="input" maxLength={60} placeholder={b.duration || ''} value={b.i18n?.[open[i]]?.duration || ''} onChange={(e) => putLang(i, open[i], { duration: e.target.value })} /></label>
                  <label className="label sm:col-span-2">{t('What the traveller sees and does')} ({open[i].toUpperCase()})<textarea rows={4} maxLength={2000} className="input" placeholder={b.text || ''} value={b.i18n?.[open[i]]?.text || ''} onChange={(e) => putLang(i, open[i], { text: e.target.value })} /></label>
                  <p className="text-[12px] text-ink/80 sm:col-span-2">{t('Leave a field empty to show the English text.')}</p>
                </div>
              )}
            </div>
          </div>
        ))}
        <button type="button" className="btn-outline !h-10" onClick={() => onChange([...list, { title: '', text: '', duration: '', tag: 'bonus', image: '', gallery: [], i18n: {} }])}><Plus className="h-4 w-4" />{t('Add a bonus')}</button>
      </div>
    </div>
  )
}

/**
 * A form is a list of sections, each a list of field specs:
 *   { k, label, kind?, tr?, help?, placeholder?, required? }
 * kinds: text | number | area | list | bool | select:a,b | multi:A,B | destination | parent
 * `tr` fields can be translated: the English tab edits the base column, every other tab edits `i18n[lang][field]`.
 */
const STATUS = 'select:published,draft,review,archived'
const LANGUAGE_CHOICES = 'multi:English,Russian,Uzbek,French,German,Spanish'

export const FORMS = {
  tours: {
    defaults: { status: 'draft', gallery: [], bonuses: [], multi_city: false, discount_percent: 0, group_pricing: true, price_from_usd: 0, rating: 4.8, review_count: 0, tour_type: 'car', languages: ['English'], group_type: 'Small group', category: 'Culture' },
    sections: [
      { title: 'Basics', hint: 'What travellers see first on the tour card and tour page.', fields: [
        { k: 'destination', kind: 'destination', label: 'Destination', required: true, help: 'The tour is listed on this destination’s page.' },
        { k: 'title', label: 'Title', tr: true, required: true, placeholder: 'Samarkand City Tour' },
        { k: 'category', label: 'Category', tr: true, placeholder: 'Culture', help: 'Used for the filter buttons on the Tours page.' },
        { k: 'multi_city', label: 'Show under “Multi-city”', kind: 'bool', help: 'Tick it for a tour that visits several cities: it also appears when visitors press “Multi-city” on the Tours page.' },
        { k: 'summary', label: 'Summary', kind: 'area', tr: true, required: true, help: 'One or two sentences shown on the tour card.' },
        { k: 'description', label: 'Description', kind: 'area', tr: true, help: 'The full text on the tour page.' },
        { k: 'story', label: 'Keepsake text', kind: 'area', tr: true, help: 'A short, beautifully written text shown at the end of the page.' },
        { k: 'image_url', label: 'Photo', kind: 'image', help: 'Upload a photo or paste a link to a wide (landscape) image.' },
        { k: 'gallery', label: 'More photos', kind: 'gallery', help: 'Upload several photos at once. Visitors slide through them on the tour page.' },
      ] },
      { title: 'Tour details', hint: 'Shown in the “Tour details” panel on the tour page.', fields: [
        { k: 'tour_type', label: 'Tour type', kind: 'select:car,walking,mixed,train,workshop' },
        { k: 'duration_label', label: 'Duration', tr: true, placeholder: 'Half day · 3 hours · Flexible hours' },
        { k: 'group_type', label: 'Group type', tr: true, placeholder: 'Small group' },
        { k: 'max_travelers', label: 'Maximum travelers', kind: 'number', placeholder: '21' },
        { k: 'group_pricing', label: 'Price depends on group size', kind: 'bool', help: 'On: the price above is for {n} or more travelers and smaller groups pay more per person (set in Group pricing). Off: one price per person for every group.' },
        { k: 'languages', label: 'Tour languages', kind: LANGUAGE_CHOICES, help: 'Languages the guide speaks.' },
        { k: 'guide', label: 'Guide', tr: true, placeholder: 'ALI TRAVEL team' },
        { k: 'meeting_point', label: 'Meeting point', tr: true, placeholder: 'Samarkand airport' },
      ] },
      { title: 'Price', hint: 'All prices are per person, in US dollars.', fields: [
        { k: 'price_from_usd', label: 'Price from (USD per person)', kind: 'number', required: true, help: 'Use 0 for a single historical place that only shows its entrance ticket.' },
        { k: 'discount_percent', label: 'Discount (%)', kind: 'number', help: 'Shows the old price crossed out with the new price beside it. Leave 0 for no discount.' },
        { k: 'entrance_fee_usd', label: 'Entrance ticket (USD)', kind: 'number', help: 'Only for a single place. Leave empty for normal tours.' },
        { k: 'parent_slug', label: 'Part of tour', kind: 'parent', help: 'Choose the bigger tour this place belongs to (for example “Samarkand City Tour”).' },
      ] },
      { title: 'Exact location', hint: 'For a single place: shown on a map with links to Google Maps. In Google Maps right-click the place and click the numbers to copy them.', fields: [
        { k: 'latitude', label: 'Latitude', kind: 'number', placeholder: '39.654722', help: 'Number of degrees north, for example 39.654722.' },
        { k: 'longitude', label: 'Longitude', kind: 'number', placeholder: '66.975556', help: 'Number of degrees east, for example 66.975556.' },
        { k: 'location_note', label: 'Address or how to find it', tr: true, placeholder: 'Registan Street, next to the ticket office' },
      ] },
      { title: 'What is included', hint: 'Tick what the price covers, then list the details.', fields: [
        { k: 'transport_included', label: 'Transport included', kind: 'bool' },
        { k: 'tickets_included', label: 'Entrance tickets included', kind: 'bool' },
        { k: 'pickup_included', label: 'Pickup included', kind: 'bool' },
        { k: 'included', label: 'Included', kind: 'list', tr: true, placeholder: 'Local guide service\nTaxi service' },
        { k: 'excluded', label: 'Not included', kind: 'list', tr: true, placeholder: 'Lunch\nDinner' },
      ] },
      { title: 'Special bonuses', hint: 'Something extra the traveller gets in this tour, for example a visit to a special place. Shown as its own golden block on the tour page and as a line on the tour card.', fields: [
        { k: 'bonuses', label: 'Bonuses', kind: 'bonuses' },
      ] },
      { title: 'Route', hint: 'The places visited, in order.', fields: [
        { k: 'route', label: 'Route stops', kind: 'list', tr: true, placeholder: 'Registan Square | 16\nGur-e-Amir Mausoleum | 13', help: 'One stop per line as: Name | entrance ticket in USD. The ticket price is optional.' },
        { k: 'highlights', label: 'Highlights', kind: 'list', tr: true, help: 'Optional short bullet points.' },
      ] },
      { title: 'Day-by-day plan', hint: 'The approximate schedule shown on the tour page and after a booking request. Choose places from the route above.', fields: [
        { k: 'itinerary', label: 'Plan', kind: 'itinerary' },
      ] },
      { title: 'Costs for accounting', hint: 'What the tour is expected to cost us. Accounting uses this to pre-fill the expenses of a finished tour.', fields: [
        { k: 'cost_items', label: 'Costs', kind: 'costs' },
      ] },
      { title: 'Publishing', fields: [
        { k: 'status', label: 'Status', kind: STATUS, help: 'Only “Published” tours are visible on the website.' },
        { k: 'featured', label: 'Show on the homepage', kind: 'bool' },
        { k: 'rating', label: 'Rating', kind: 'number' },
        { k: 'review_count', label: 'Review count', kind: 'number', help: 'Use 0 to hide the rating on the card.' },
        { k: 'destination_name', label: 'Destination name', tr: true, translateOnly: true },
      ] },
    ],
  },
  destinations: {
    defaults: { status: 'draft', order: 0, gallery: [] },
    sections: [
      { title: 'Basics', fields: [
        { k: 'name', label: 'Name', tr: true, required: true, placeholder: 'Samarkand' },
        { k: 'region', label: 'Region', tr: true, placeholder: 'Silk Road crossroads' },
        { k: 'suggested_duration', label: 'Suggested duration', tr: true, placeholder: '3 days' },
        { k: 'summary', label: 'Summary', kind: 'area', tr: true, required: true },
        { k: 'description', label: 'Description', kind: 'area', tr: true },
        { k: 'image_url', label: 'Photo', kind: 'image', help: 'Upload a photo or paste a link to a wide (landscape) image.' },
        { k: 'gallery', label: 'More photos', kind: 'gallery', help: 'Upload several photos at once. Visitors slide through them on the destination page.' },
      ] },
      { title: 'Trip builder', hint: 'Used by the “Plan my trip” page to draft day-by-day itineraries.', fields: [
        { k: 'activities', label: 'Activities', kind: 'list', tr: true, help: 'One activity per line.' },
      ] },
      { title: 'Publishing', fields: [
        { k: 'status', label: 'Status', kind: STATUS },
        { k: 'featured', label: 'Show on the homepage', kind: 'bool' },
        { k: 'order', label: 'Sort order', kind: 'number', help: 'Smaller numbers come first.' },
      ] },
    ],
  },
  hotels: {
    defaults: { status: 'draft', discount_percent: 0, stars: 3, rating: 4.6, price_from_usd: 0, property_type: 'hotel', price_basis: 'room', gallery: [], photos_illustrative: false },
    sections: [
      { title: 'Basics', fields: [
        { k: 'destination', kind: 'destination', label: 'Destination', required: true },
        { k: 'name', label: 'Name', tr: true, required: true },
        { k: 'summary', label: 'Summary', kind: 'area', tr: true, required: true },
        { k: 'description', label: 'Description', kind: 'area', tr: true },
        { k: 'image_url', label: 'Photo', kind: 'image', help: 'Upload a photo or paste a link to a wide (landscape) image.' },
        { k: 'gallery', label: 'More photos', kind: 'gallery', help: 'Upload several photos at once. Visitors slide through them on the hotel card and page.' },
        { k: 'photos_illustrative', label: 'Photos show similar places, not this property itself', kind: 'bool', help: 'Shows a note under the photos. Untick it once you have uploaded the property’s own photos.' },
      ] },
      { title: 'Details', fields: [
        { k: 'property_type', label: 'Type', kind: 'select:hotel,boutique,guesthouse,hostel' },
        { k: 'stars', label: 'Stars', kind: 'number', help: 'Use 0 for guesthouses and hostels.' },
        { k: 'price_from_usd', label: 'Price from (USD)', kind: 'number', required: true, help: 'The lowest usual nightly price. Visitors see it as an indicative “from” price.' },
        { k: 'price_basis', label: 'Price is', kind: 'select:room,bed', help: 'Hostels and dorm rooms are priced per bed.' },
        { k: 'discount_percent', label: 'Discount (%)', kind: 'number', help: 'Shows the old price crossed out with the new price beside it. Leave 0 for no discount.' },
        { k: 'rating', label: 'Rating', kind: 'number' },
        { k: 'amenities', label: 'Amenities', kind: 'list', tr: true, help: 'One per line.' },
      ] },
      { title: 'Publishing', fields: [
        { k: 'status', label: 'Status', kind: STATUS },
        { k: 'destination_name', label: 'Destination name', tr: true, translateOnly: true },
      ] },
    ],
  },
  food: {
    defaults: { status: 'draft', kind: 'Dish' },
    sections: [
      { title: 'Basics', fields: [
        { k: 'name', label: 'Name', tr: true, required: true },
        { k: 'kind', label: 'Kind (dish, experience…)', tr: true, placeholder: 'Dish' },
        { k: 'destination_name', label: 'Destination', tr: true },
        { k: 'summary', label: 'Summary', kind: 'area', tr: true, required: true },
        { k: 'image_url', label: 'Photo', kind: 'image', help: 'Upload a photo or paste a link to a wide (landscape) image.' },
        { k: 'price_from_usd', label: 'Price from (USD, optional)', kind: 'number' },
      ] },
      { title: 'Publishing', fields: [{ k: 'status', label: 'Status', kind: STATUS }] },
    ],
  },
  transport: {
    defaults: { status: 'draft', discount_percent: 0, capacity: 3, included_passengers: 3, base_price_usd: 0, extra_passenger_usd: 0 },
    sections: [
      { title: 'Basics', fields: [
        { k: 'name', label: 'Name', tr: true, required: true },
        { k: 'vehicle', label: 'Vehicle', tr: true },
        { k: 'summary', label: 'Summary', kind: 'area', tr: true },
        { k: 'image_url', label: 'Photo', kind: 'image', help: 'Upload a photo or paste a link to a wide (landscape) image.' },
      ] },
      { title: 'Price and capacity', fields: [
        { k: 'capacity', label: 'Capacity', kind: 'number' },
        { k: 'included_passengers', label: 'Included passengers', kind: 'number' },
        { k: 'base_price_usd', label: 'Base price (USD)', kind: 'number', required: true },
        { k: 'discount_percent', label: 'Discount (%)', kind: 'number', help: 'Shows the old price crossed out with the new price beside it. Leave 0 for no discount.' },
        { k: 'extra_passenger_usd', label: 'Extra passenger (USD)', kind: 'number' },
      ] },
      { title: 'Publishing', fields: [{ k: 'status', label: 'Status', kind: STATUS }] },
    ],
  },
}

const toText = (v, kind) => (kind === 'list' ? (v || []).join('\n') : v ?? '')
const fromText = (v, kind) => (kind === 'list' ? v.split('\n').map((x) => x.trim()).filter(Boolean) : v)
const flat = (form) => form.sections.flatMap((s) => s.fields)

function Help({ children }) {
  return children ? <span className="mt-1 block text-[12px] font-normal leading-snug text-ink/80">{children}</span> : null
}

export default function RecordEditor({ resource, record, onDone, label, preset }) {
  const t = useT()
  const top = biggestGroup(useGroupTiers())
  const form = FORMS[resource]
  const all = flat(form)
  const needsDestination = all.some((f) => f.kind === 'destination')
  const destinations = useFetch(needsDestination ? '/destinations/?all=1&raw=1' : null, { list: true })
  const tours = useFetch(resource === 'tours' ? '/tours/?all=1&raw=1' : null, { list: true })

  const [lang, setLang] = useState('en')
  const [base, setBase] = useState(() => {
    const out = {}
    all.forEach(({ k, kind = 'text' }) => {
      if (kind === 'destination') return
      const stored = record ? record[k] : preset?.[k] ?? form.defaults[k]
      out[k] = kind === 'list' ? toText(stored, 'list') : kind.startsWith('multi:') || kind === 'itinerary' || kind === 'costs' || kind === 'gallery' || kind === 'bonuses' ? stored || [] : stored ?? (kind === 'bool' ? false : '')
    })
    out.destination_slug = record?.destination_slug ?? preset?.destination_slug ?? ''
    out.destination_name = record?.destination_name ?? preset?.destination_name ?? out.destination_name ?? ''
    return out
  })
  const [tr, setTr] = useState(() => {
    const out = {}
    LANGS.slice(1).forEach(({ code }) => {
      out[code] = {}
      all.filter((f) => f.tr).forEach(({ k, kind }) => { out[code][k] = toText(record?.i18n?.[code]?.[k], kind) })
    })
    return out
  })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const uploading = useUploads()   // a photo still on its way: saving now would leave it out

  // Picking a destination also copies its name (and its translated names) so the tour reads correctly in every language.
  function pickDestination(slug) {
    const d = destinations.data.find((x) => x.slug === slug)
    setBase((p) => ({ ...p, destination_slug: slug, destination_name: d?.name || '' }))
    if (d) setTr((p) => Object.fromEntries(Object.entries(p).map(([code, v]) => [code, { ...v, destination_name: d.i18n?.[code]?.name || v.destination_name }])))
  }

  // A blank template opened from a destination page: copy that destination's translated names as soon as they load.
  useEffect(() => { if (!record && preset?.destination_slug && destinations.data.length) pickDestination(preset.destination_slug) }, [destinations.data.length]) // eslint-disable-line react-hooks/exhaustive-deps

  async function remove() {
    if (!window.confirm(t('Delete this item? This cannot be undone.'))) return
    try { await api.del(`/${resource}/${record.slug}/`); onDone(true) } catch (ex) { setError(ex.message) }
  }

  async function save(e) {
    e.preventDefault()
    if (uploading.count > 0) return setError('Wait until the photo has uploaded, then save.')
    setError(''); setBusy(true)
    const body = {}
    all.forEach(({ k, kind = 'text' }) => {
      if (kind === 'destination' || k === 'destination_name') return
      if (kind === 'number') body[k] = k === 'discount_percent' ? Number(base[k] || 0) : base[k] === '' || base[k] === null ? null : Number(base[k])
      else body[k] = fromText(base[k], kind)
    })
    if (needsDestination) { body.destination_slug = base.destination_slug; body.destination_name = base.destination_name }
    else if ('destination_name' in base && all.some((f) => f.k === 'destination_name' && !f.translateOnly)) body.destination_name = base.destination_name
    body.i18n = {}
    LANGS.slice(1).forEach(({ code }) => {
      const entries = all.filter((f) => f.tr).map(({ k, kind }) => [k, fromText(tr[code][k], kind)]).filter(([, v]) => (Array.isArray(v) ? v.length : v))
      if (entries.length) body.i18n[code] = Object.fromEntries(entries)
    })
    try {
      if (record) await api.patch(`/${resource}/${record.slug}/`, body)
      else await api.post(`/${resource}/`, body)
      onDone(true)
    } catch (ex) { setError(ex.message); setBusy(false) }
  }

  const filled = (code) => Object.values(tr[code]).some((v) => v && String(v).trim())

  function renderField(f) {
    const { k, label: fl, kind = 'text', placeholder, help, required } = f
    const wide = kind === 'area' || kind === 'list' || kind.startsWith('multi:')
    const isEnglish = lang === 'en'
    const value = isEnglish ? base[k] : tr[lang]?.[k]
    const set = (v) => (isEnglish ? setBase((p) => ({ ...p, [k]: v })) : setTr((p) => ({ ...p, [lang]: { ...p[lang], [k]: v } })))
    const ph = isEnglish ? placeholder || '' : String(base[k] ?? '')
    const caption = <>{t(fl)}{required && isEnglish && <span className="text-destructive"> *</span>}{kind === 'list' && <span className="font-normal"> ({t('one per line')})</span>}</>

    if (kind === 'itinerary') return <ItineraryField key={k} label={t(fl)} help={help && t(help)} value={base.itinerary} onChange={set} route={base.route} />
    if (kind === 'costs') return <CostsField key={k} label={t(fl)} help={help && t(help)} value={base.cost_items} onChange={set} />

    if (kind === 'gallery') return <GalleryField key={k} label={t(fl)} help={help && t(help)} value={base[k]} onChange={set} />
    if (kind === 'bonuses') return <BonusesField key={k} label={t(fl)} help={help && t(help)} value={base[k]} onChange={(v) => setBase((p) => ({ ...p, bonuses: v }))} />
    if (kind === 'image') return <ImageField key={k} label={t(fl)} help={help && t(help)} value={value} onChange={set} />

    if (kind === 'bool') {
      return (
        <label key={k} className="flex cursor-pointer items-start gap-3 rounded-sm border border-navy/10 bg-white px-4 py-3 text-[14px]">
          <input type="checkbox" className="mt-1 h-4 w-4" checked={!!value} onChange={(e) => set(e.target.checked)} />
          <span><span className="font-medium text-navy">{t(fl)}</span><Help>{help && t(help, { n: top })}</Help></span>
        </label>
      )
    }
    return (
      <label key={k} className={`label ${wide ? 'sm:col-span-2' : ''}`}>{caption}
        {kind === 'area' || kind === 'list' ? <textarea rows={kind === 'area' ? 3 : 4} className="input" placeholder={ph} value={value ?? ''} onChange={(e) => set(e.target.value)} />
          : kind === 'destination' ? (
            <select className="input" required={required} value={base.destination_slug} onChange={(e) => pickDestination(e.target.value)}>
              <option value="">{t('— choose —')}</option>{destinations.data.map((d) => <option key={d.slug} value={d.slug}>{d.name}</option>)}</select>)
          : kind === 'parent' ? (
            <select className="input" value={value ?? ''} onChange={(e) => set(e.target.value)}>
              <option value="">{t('— none (a normal tour) —')}</option>
              {tours.data.filter((x) => !x.parent_slug && x.slug !== record?.slug).map((x) => <option key={x.slug} value={x.slug}>{x.title}</option>)}</select>)
          : kind.startsWith('multi:') ? (
            <span className="mt-2 flex flex-wrap gap-2">{kind.slice(6).split(',').map((o) => {
              const on = (value || []).includes(o)
              return <button key={o} type="button" aria-pressed={on} onClick={() => set(on ? value.filter((x) => x !== o) : [...(value || []), o])}
                className={`rounded-full border px-3.5 py-1.5 text-[13px] ${on ? 'border-navy bg-navy text-ivory' : 'border-navy/20 text-navy/75 hover:border-navy/50'}`}>{t(o)}</button>
            })}</span>)
          : kind.startsWith('select:') ? (
            <select className="input" value={value ?? ''} onChange={(e) => set(e.target.value)}>
              {kind.slice(7).split(',').map((o) => <option key={o} value={o}>{t(o === 'hotel' ? 'Hotel' : o === 'boutique' ? 'Boutique hotel' : o === 'guesthouse' ? 'Guesthouse' : o === 'hostel' ? 'Hostel' : o === 'room' ? 'per room per night' : o === 'bed' ? 'per bed per night' : o === 'review' ? 'Awaiting review' : o === 'mixed' ? 'Car + walking' : o === 'car' ? 'Car tour' : o === 'walking' ? 'Walking tour' : o === 'train' ? 'Train tour' : cap(o))}</option>)}</select>)
          : <input type={kind === 'number' ? 'number' : 'text'} step="any" min={kind === 'number' ? 0 : undefined} required={required && isEnglish} className="input" placeholder={ph} value={value ?? ''} onChange={(e) => set(e.target.value)} />}
        {isEnglish && <Help>{help && t(help)}</Help>}
      </label>
    )
  }

  const titleKey = `${record ? 'Edit' : 'New'} ${label}`
  return (
    <form onSubmit={save} className="mx-auto w-full max-w-4xl rounded-md border border-navy/10 bg-white p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-heading text-[28px]">{t(titleKey)}</h2>
        <div className="flex flex-wrap gap-1.5" role="tablist" aria-label="Language">
          {LANGS.map((l) => (
            <button key={l.code} type="button" role="tab" aria-selected={lang === l.code} onClick={() => setLang(l.code)} title={l.label}
              className={`rounded-full border px-3.5 py-1.5 text-[12px] uppercase tracking-[0.08em] ${lang === l.code ? 'border-navy bg-navy text-ivory' : 'border-navy/15 text-navy/70 hover:border-navy'}`}>
              {l.code}{l.code !== 'en' && filled(l.code) && <span className="ml-1.5 inline-block h-1.5 w-1.5 rounded-full bg-turquoise align-middle" />}
            </button>
          ))}
        </div>
      </div>

      {lang === 'en' ? (
        <div className="mt-2 space-y-8">
          {form.sections.map((section) => {
            const fields = section.fields.filter((f) => !f.translateOnly)
            return (
              <fieldset key={section.title} className="border-t border-navy/10 pt-5">
                <legend className="px-0 font-heading text-[22px]">{t(section.title)}</legend>
                {section.hint && <p className="-mt-1 mb-3 text-[13px] text-ink">{t(section.hint)}</p>}
                <div className="grid gap-4 sm:grid-cols-2">{fields.map(renderField)}</div>
              </fieldset>
            )
          })}
        </div>
      ) : (
        <div className="mt-2">
          <p className="mb-4 mt-3 rounded-sm bg-sand-soft/70 px-4 py-3 text-[13px] text-navy/80">{t('Translating into {lang}. Leave a field empty to show the English text.', { lang: LANGS.find((l) => l.code === lang).label })}</p>
          <div className="grid gap-4 sm:grid-cols-2">{all.filter((f) => f.tr).map(renderField)}</div>
        </div>
      )}

      {error && <p role="alert" className="mt-4 text-[13px] text-destructive">{error}</p>}
      <div className="mt-6 flex flex-wrap items-center gap-3"><button className="btn-primary" disabled={busy || uploading.count > 0}>{uploading.count > 0 ? t('Uploading the photo… {n}%', { n: uploading.percent }) : record ? t('Save changes') : t('Create')}</button><button type="button" className="btn-outline" onClick={() => onDone(false)}>{t('Cancel')}</button>
        {record && <button type="button" onClick={remove} className="ml-auto h-11 rounded-full border border-red-200 px-5 text-[13px] text-destructive hover:bg-red-50">{t('Delete')}</button>}</div>
    </form>
  )
}
