import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Heart } from 'lucide-react'
import { api, getToken } from '../api'
import { useT } from '../i18n'

// One request for the whole page: every card asks the same list of saved tours.
let saved = null       // Map slug -> saved row id
let loading = null
const listeners = new Set()
const notify = () => listeners.forEach((fn) => fn())

function loadSaved() {
  if (!getToken()) return Promise.resolve(new Map())
  loading ||= api.list('/saved/?item_type=tour').then((rows) => { saved = new Map(rows.map((r) => [r.item_slug, r.id])); return saved })
    .catch(() => { saved = new Map(); return saved })
  return loading
}

/** The ♡ on a tour card: saves the tour to the traveller's list (signing in first when needed). */
export default function CardHeart({ tour, className = '' }) {
  const t = useT()
  const nav = useNavigate()
  const [, redraw] = useState(0)
  useEffect(() => {
    const fn = () => redraw((x) => x + 1)
    listeners.add(fn)
    loadSaved().then(fn)
    return () => { listeners.delete(fn) }
  }, [])
  const id = saved?.get(tour.slug)
  async function toggle(e) {
    e.preventDefault(); e.stopPropagation()
    if (!getToken()) { nav('/login'); return }
    await loadSaved()
    if (id) { await api.del(`/saved/${id}/`); saved.delete(tour.slug) }
    else {
      const row = await api.post('/saved/', { item_type: 'tour', item_slug: tour.slug, item_title: tour.title, item_image: tour.image_url || '', item_meta: tour.duration_label || '' })
      saved.set(tour.slug, row.id)
    }
    notify()
  }
  return (
    <button type="button" data-edit-ignore onClick={toggle} aria-pressed={!!id} aria-label={t(id ? 'Saved' : 'Save')}
      className={`absolute right-3 top-3 z-10 grid h-9 w-9 place-items-center rounded-full bg-white/95 text-navy shadow-md transition hover:scale-105 ${className}`}>
      <Heart className={`h-[18px] w-[18px] ${id ? 'fill-red-500 text-red-500' : ''}`} strokeWidth={2} />
    </button>
  )
}
