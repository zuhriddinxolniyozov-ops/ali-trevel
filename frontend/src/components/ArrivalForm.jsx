import { useState } from 'react'
import { MapPin, Plane } from 'lucide-react'
import { api } from '../api'
import { useT } from '../i18n'
import { isLocal } from '../market'
import { Field, Spinner } from './ui'

/**
 * Shown after a tour request. On the global site: when and how the traveller reaches Samarkand airport, so the guide can meet them.
 * On the local site the traveller is already in Uzbekistan: the day, time and place where our team meets them.
 */
export default function ArrivalForm({ reference, email, date = '' }) {
  const t = useT()
  const [f, setF] = useState({ arrival_date: date, arrival_time: '', arrival_flight: '', meeting_place: '' })
  const [errors, setErrors] = useState({})
  const [state, setState] = useState('idle')
  const [message, setMessage] = useState('')
  const set = (k) => (e) => setF((p) => ({ ...p, [k]: e.target.value }))

  async function submit(e) {
    e.preventDefault()
    const err = {}
    if (!f.arrival_date) err.arrival_date = isLocal ? 'Choose the day.' : 'Choose the arrival date.'
    if (!f.arrival_time) err.arrival_time = isLocal ? 'Choose the time.' : 'Choose the arrival time.'
    if (isLocal && !f.meeting_place.trim()) err.meeting_place = 'Write where we should meet you.'
    setErrors(err)
    if (Object.keys(err).length) return
    setState('saving'); setMessage('')
    try {
      await api.post('/bookings-arrival/', { reference, email, ...f, arrival_flight: f.arrival_flight.trim(), meeting_place: isLocal ? f.meeting_place.trim() : '' })
      setState('done')
    } catch (ex) { setState('idle'); setMessage(ex.message) }
  }

  if (state === 'done') {
    return <p role="status" className="mt-4 rounded-sm border border-turquoise-deep/30 bg-white p-4 text-[13.5px] text-navy">
      {t(isLocal ? 'Thank you. We have the meeting details; our team will meet you there at the agreed time.' : 'Thank you. We have your arrival details; our guide will meet you at Samarkand airport.')}</p>
  }
  if (isLocal) {
    return (
      <form onSubmit={submit} noValidate className="mt-4 rounded-sm border border-navy/12 bg-white p-4">
        <p className="flex items-center gap-2 font-medium text-navy"><MapPin className="h-4 w-4 text-turquoise-deep" />{t('When and where shall we meet?')}</p>
        <p className="mt-1 text-[12.5px] leading-relaxed text-ink">{t('Choose the day, the time and the place where our team meets you, for example your hotel or home address. You can also send this later.')}</p>
        <div className="mt-3 grid grid-cols-2 gap-3">
          <Field label="Meeting day" error={errors.arrival_date}><input type="date" className="input" value={f.arrival_date} onChange={set('arrival_date')} /></Field>
          <Field label="Meeting time" error={errors.arrival_time}><input type="time" className="input" value={f.arrival_time} onChange={set('arrival_time')} /></Field>
        </div>
        <Field label="Meeting place" error={errors.meeting_place}><input className="input" maxLength={200} placeholder={t('For example: Registan Square, or your hotel and its address')} value={f.meeting_place} onChange={set('meeting_place')} /></Field>
        {message && <p role="alert" className="mt-2 text-[12px] text-destructive">{message}</p>}
        <button type="submit" disabled={state === 'saving'} className="btn-primary mt-3 w-full">{state === 'saving' && <Spinner />}{t('Send meeting details')}</button>
      </form>
    )
  }
  return (
    <form onSubmit={submit} noValidate className="mt-4 rounded-sm border border-navy/12 bg-white p-4">
      <p className="flex items-center gap-2 font-medium text-navy"><Plane className="h-4 w-4 text-turquoise-deep" />{t('When do you arrive at Samarkand airport?')}</p>
      <p className="mt-1 text-[12.5px] leading-relaxed text-ink">{t('Tell us the date and time you land so our guide can meet you. You can also send this later.')}</p>
      <div className="mt-3 grid grid-cols-2 gap-3">
        <Field label="Arrival date" error={errors.arrival_date}><input type="date" className="input" value={f.arrival_date} onChange={set('arrival_date')} /></Field>
        <Field label="Arrival time" error={errors.arrival_time}><input type="time" className="input" value={f.arrival_time} onChange={set('arrival_time')} /></Field>
      </div>
      <Field label="Flight or train number (optional)"><input className="input" maxLength={60} placeholder="HY 123" value={f.arrival_flight} onChange={set('arrival_flight')} /></Field>
      {message && <p role="alert" className="mt-2 text-[12px] text-destructive">{message}</p>}
      <button type="submit" disabled={state === 'saving'} className="btn-primary mt-3 w-full">{state === 'saving' && <Spinner />}{t('Send arrival details')}</button>
    </form>
  )
}
