import { useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { api } from '../api'
import { useFetch } from '../hooks'
import { useT } from '../i18n'
import { Spinner } from '../components/ui'
import { CITIES, PLACES, PLACE_OF_DESTINATION } from '../mapCities'

const SIDES = [['above', 'above'], ['below', 'below'], ['left', 'to the left'], ['right', 'to the right']]
const dotKey = (slug) => `t-${slug}`.slice(0, 30)  // the key of a tour's dot on the map
const field = 'input !mt-0'

/**
 * The Silk Road map of the home page: which tours (and cities) are green dots, where they sit on the map and where a click leads.
 * A dot is drawn at the latitude and longitude given here; a tour's dot opens that tour.
 */
export default function AdminMap() {
  const t = useT()
  const { data, loading } = useFetch('/site-content/')
  const { data: allTours } = useFetch('/tours/?all=1', { list: true })
  const [form, setForm] = useState(null)
  const [message, setMessage] = useState('')
  const [saving, setSaving] = useState(false)
  if (loading || !data) return <Spinner />
  const cities = form || data.map_cities || {}
  const tours = allTours.filter((x) => !x.parent_slug && Number(x.price_from_usd) > 0)
  const set = (next) => { setMessage(''); setForm(next) }
  const patch = (key, change) => set({ ...cities, [key]: { ...cities[key], ...change } })
  const remove = (key) => { const rest = { ...cities }; delete rest[key]; set(rest) }
  const own = Object.entries(cities).filter(([key]) => key.startsWith('c-'))

  function addTour(tour) {
    const place = PLACES.find(([key]) => key === PLACE_OF_DESTINATION[tour.destination_slug])
    set({ ...cities, [dotKey(tour.slug)]: { name: (tour.destination_name || tour.title).slice(0, 40), lat: place ? place[2] : '', lon: place ? place[3] : '', side: 'above', green: true, target: `/tours/${tour.slug}` } })
  }

  async function save() {
    const unfinished = Object.entries(cities).find(([, c]) => c.name !== undefined && (c.lat === '' || c.lon === '' || c.lat == null || c.lon == null) && String(c.name).trim())
    if (unfinished) return setMessage(`${t('Choose a place or write the latitude and longitude for')}: ${unfinished[1].name}`)
    setSaving(true); setMessage('')
    try { await api.put('/site-content/', { map_cities: cities }); setForm(null); setMessage(t('Saved. The home page map is updated.')) } catch (ex) { setMessage(ex.message) }
    setSaving(false)
  }

  return (
    <div className="max-w-5xl space-y-8">
      <section className="rounded-sm border border-navy/10 bg-white p-5">
        <h2 className="font-heading text-[26px]">{t('Tours on the map')}</h2>
        <p className="mt-1 text-[14px] text-ink">{t('Switch a tour on to show it as a green pulsing dot on the home page map. Choose where it sits; a click on the dot opens that tour. A tour you add later appears in this list.')}</p>
        <div className="mt-4 divide-y divide-navy/10 rounded-sm border border-navy/10">
          {tours.map((tour) => {
            const key = dotKey(tour.slug)
            const dot = cities[key]
            return (
              <div key={tour.slug} className="px-3 py-3">
                <label className="flex flex-wrap items-center gap-3 text-[15px]">
                  <input type="checkbox" checked={!!dot} onChange={(e) => (e.target.checked ? addTour(tour) : remove(key))} />
                  <span className={`inline-block h-3 w-3 rounded-full ${dot ? 'bg-[#22c55e]' : 'bg-navy/25'}`} aria-hidden="true" />
                  <span className="font-medium text-navy">{tour.title}</span>
                  <span className="text-[13px] text-ink">{tour.destination_name} · {t(tour.duration_label)}</span>
                </label>
                {dot && (
                  <div className="mt-3 grid gap-2 rounded-sm bg-sand-soft/50 p-3 sm:grid-cols-[1.2fr_1.4fr_0.8fr_0.8fr_1fr]">
                    <label className="label">{t('Name on the map')}<input className={field} maxLength={40} value={dot.name || ''} onChange={(e) => patch(key, { name: e.target.value })} /></label>
                    <label className="label">{t('Place')}
                      <select className={field} value={(PLACES.find(([, , lat, lon]) => Number(lat) === Number(dot.lat) && Number(lon) === Number(dot.lon)) || [''])[0]}
                        onChange={(e) => { const place = PLACES.find(([k]) => k === e.target.value); if (place) patch(key, { lat: place[2], lon: place[3] }) }}>
                        <option value="">{t('Own coordinates')}</option>
                        {PLACES.map(([k, name]) => <option key={k} value={k}>{t(name)}</option>)}
                      </select></label>
                    <label className="label">{t('Latitude')}<input type="number" step="any" className={field} value={dot.lat ?? ''} onChange={(e) => patch(key, { lat: e.target.value })} /></label>
                    <label className="label">{t('Longitude')}<input type="number" step="any" className={field} value={dot.lon ?? ''} onChange={(e) => patch(key, { lon: e.target.value })} /></label>
                    <label className="label">{t('Name placed')}<select className={field} value={dot.side || 'above'} onChange={(e) => patch(key, { side: e.target.value })}>{SIDES.map(([v, l]) => <option key={v} value={v}>{t(l)}</option>)}</select></label>
                  </div>
                )}
              </div>
            )
          })}
          {!tours.length && <p className="p-5 text-[14px] text-ink">{t('No tours yet.')}</p>}
        </div>
      </section>

      <section className="rounded-sm border border-navy/10 bg-white p-5">
        <h2 className="font-heading text-[26px]">{t('Cities')}</h2>
        <p className="mt-1 text-[14px] text-ink">{t('Tick a city to mark it with a green pulsing dot. A click on it opens the tours of that city, or the tour you choose. A city that is not on the map yet appears once ticked.')}</p>
        <div className="mt-4 divide-y divide-navy/10 rounded-sm border border-navy/10">
          {CITIES.map(([key, name]) => {
            const chosen = cities[key] || { green: false, target: '' }
            const change = (change2) => set({ ...cities, [key]: { ...chosen, ...change2 } })
            return (
              <div key={key} className="grid items-center gap-2 px-3 py-2.5 sm:grid-cols-[170px_1fr]">
                <label className="flex items-center gap-2 text-[14px]"><input type="checkbox" checked={!!chosen.green} onChange={(e) => change({ green: e.target.checked })} />
                  <span className={`inline-block h-3 w-3 rounded-full ${chosen.green ? 'bg-[#22c55e]' : 'bg-navy/25'}`} aria-hidden="true" />{t(name)}</label>
                <select aria-label={t('A click opens')} disabled={!chosen.green} className={`${field} disabled:opacity-50`} value={chosen.target || ''} onChange={(e) => change({ target: e.target.value })}>
                  <option value="">{t('The tours of this city')}</option>
                  {tours.map((x) => <option key={x.slug} value={`/tours/${x.slug}`}>{x.title}</option>)}
                </select>
              </div>
            )
          })}
        </div>

        <h3 className="mt-6 font-medium text-navy">{t('Cities you added')}</h3>
        <p className="text-[12.5px] text-ink">{t('Add any other place of Uzbekistan: write its name and its latitude and longitude (in Google Maps right-click the place and click the numbers to copy them).')}</p>
        <div className="mt-2 space-y-2">
          {own.map(([key, c]) => (
            <div key={key} className="grid gap-2 rounded-sm bg-sand-soft/50 p-3 sm:grid-cols-[1.2fr_0.8fr_0.8fr_1.1fr_1.6fr_auto]">
              <label className="label">{t('Name')}<input className={field} maxLength={40} value={c.name || ''} onChange={(e) => patch(key, { name: e.target.value })} /></label>
              <label className="label">{t('Latitude')}<input type="number" step="any" className={field} value={c.lat ?? ''} onChange={(e) => patch(key, { lat: e.target.value })} /></label>
              <label className="label">{t('Longitude')}<input type="number" step="any" className={field} value={c.lon ?? ''} onChange={(e) => patch(key, { lon: e.target.value })} /></label>
              <label className="label">{t('Name placed')}<select className={field} value={c.side || 'above'} onChange={(e) => patch(key, { side: e.target.value })}>{SIDES.map(([v, l]) => <option key={v} value={v}>{t(l)}</option>)}</select></label>
              <label className="label">{t('A click opens')}<select className={field} value={c.target || ''} onChange={(e) => patch(key, { target: e.target.value })}><option value="">{t('Nothing')}</option>{tours.map((x) => <option key={x.slug} value={`/tours/${x.slug}`}>{x.title}</option>)}</select></label>
              <div className="mt-6 flex items-center gap-2"><label className="flex items-center gap-1 text-[13px]"><input type="checkbox" checked={!!c.green} onChange={(e) => patch(key, { green: e.target.checked })} />{t('Green')}</label>
                <button type="button" aria-label={t('Remove this line')} className="h-10 rounded-full border border-red-200 px-3 text-destructive hover:bg-red-50" onClick={() => remove(key)}><Trash2 className="mx-auto h-4 w-4" /></button></div>
            </div>
          ))}
        </div>
        <button type="button" className="btn-outline mt-3 !h-9" onClick={() => set({ ...cities, [`c-${Math.random().toString(36).slice(2, 8)}`]: { name: '', lat: '', lon: '', side: 'above', green: true, target: '' } })}><Plus className="h-4 w-4" />{t('Add a city')}</button>
      </section>

      <div className="flex flex-wrap items-center gap-3">
        <button type="button" className="btn-primary" disabled={saving} onClick={save}>{saving && <Spinner />}{t('Save the map')}</button>
        {message && <span role="status" className="text-[14px] text-turquoise-deep">{message}</span>}
      </div>
    </div>
  )
}
