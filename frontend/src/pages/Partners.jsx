import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth, useFetch } from '../hooks'
import { useT } from '../i18n'
import { EMAIL_RE, EmptyState, Field, PageHero, PHONE_RE, Spinner, Success } from '../components/ui'
import PhoneInput from '../components/PhoneInput'
import { IMAGES } from '../data'
import { StatusPill } from './Auth'

const TYPES = ['Guide', 'Driver / transfers', 'Hotel / guesthouse', 'Restaurant / cooking class', 'Craft workshop']

export function PartnersHome() {
  const t = useT()
  const { isAuthenticated } = useAuth()
  return (
    <>
      <PageHero eyebrow="Partners" title="Work with ALI TRAVEL" description="Guides, drivers, hosts and makers: join our network and receive vetted requests from travellers." image={IMAGES.craft} />
      <div className="shell flex flex-wrap gap-3 py-16">
        <Link to="/partners/register" className="btn-primary">{t('Register as a partner')}</Link>
        <Link to={isAuthenticated ? '/partners/dashboard' : '/login'} className="btn-outline">{isAuthenticated ? t('Partner dashboard') : t('Partner Sign In')}</Link>
      </div>
    </>
  )
}

export function PartnerRegister() {
  const t = useT()
  const [f, setF] = useState({ business_name: '', contact_name: '', email: '', phone: '', partner_type: TYPES[0], city: '', description: '' })
  const [errors, setErrors] = useState({})
  const [state, setState] = useState('idle')
  const set = (k) => (e) => setF((p) => ({ ...p, [k]: e.target.value }))
  async function submit(e) {
    e.preventDefault()
    const err = {}
    if (f.business_name.trim().length < 2) err.business_name = 'Business name is required.'
    if (f.contact_name.trim().length < 2) err.contact_name = 'Contact name is required.'
    if (!EMAIL_RE.test(f.email)) err.email = 'A valid email is required.'
    if (!PHONE_RE.test(f.phone)) err.phone = 'Please enter your phone number.'
    setErrors(err)
    if (Object.keys(err).length) return
    setState('saving')
    try { await api.post('/partners/', f); setState('done') } catch { setState('error') }
  }
  return (
    <div className="shell max-w-2xl py-16 lg:py-24">
      <h1 className="display-lg">{t('Partner registration')}</h1>
      {state === 'done' ? <div className="mt-8"><Success title="Application received">{t('Our team reviews every application and will reply by email.')}</Success></div> : (
        <form onSubmit={submit} noValidate className="mt-8 space-y-4">
          <Field label="Business name" error={errors.business_name}><input className="input" value={f.business_name} onChange={set('business_name')} /></Field>
          <Field label="Contact name" error={errors.contact_name}><input className="input" value={f.contact_name} onChange={set('contact_name')} /></Field>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Email" error={errors.email}><input type="email" className="input" value={f.email} onChange={set('email')} /></Field>
            <Field label="Phone" error={errors.phone}><PhoneInput value={f.phone} onChange={(v) => setF((p) => ({ ...p, phone: v }))} invalid={!!errors.phone} /></Field></div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Type"><select className="input" value={f.partner_type} onChange={set('partner_type')}>{TYPES.map((x) => <option key={x} value={x}>{t(x)}</option>)}</select></Field>
            <Field label="City"><input className="input" value={f.city} onChange={set('city')} /></Field></div>
          <Field label="About your business"><textarea rows={4} className="input" value={f.description} onChange={set('description')} /></Field>
          {state === 'error' && <p role="alert" className="text-[12px] text-destructive">{t('We could not send your application. Please try again.')}</p>}
          <button className="btn-primary" disabled={state === 'saving'}>{state === 'saving' && <Spinner />}{t('Submit application')}</button>
        </form>)}
    </div>
  )
}

export function PartnerDashboard() {
  const t = useT()
  const { data, loading } = useFetch('/partners/', { list: true })
  const p = data[0]
  return (
    <div className="shell py-16 lg:py-24">
      <h1 className="display-lg">{t('Partner dashboard')}</h1>
      {loading ? <Spinner /> : !p ? (
        <div className="mt-8"><EmptyState title="No partner profile on this account" body="Register your business to start receiving requests." /><Link to="/partners/register" className="btn-primary mt-4">{t('Register as a partner')}</Link></div>
      ) : (
        <div className="mt-8 max-w-xl rounded-sm border border-navy/10 bg-card p-6">
          <div className="flex items-center justify-between"><h2 className="font-heading text-[26px]">{p.business_name}</h2><StatusPill status={p.status} /></div>
          <p className="mt-2 text-[14px] text-ink">{t(p.partner_type)} · {p.city}</p><p className="mt-3 text-[14px] text-ink">{p.description}</p>
          {p.status !== 'approved' && <p className="mt-4 text-[13px] text-ink">{t('Your application is being reviewed. We will email you when it is done.')}</p>}
        </div>)}
    </div>
  )
}
