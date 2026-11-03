import { useState } from 'react'
import { api } from '../api'
import { useSettings } from '../hooks'
import { useT } from '../i18n'
import { EMAIL_RE, Field, Honeypot, PageHero, Spinner, Success } from '../components/ui'
import Seo from '../components/Seo'
import { ExtraContacts, Phones, Socials } from '../components/Layout'
import { IMAGES } from '../data'

const ABOUT_POINTS = ['Licensed local guides', 'Family-run guesthouses we know personally', 'Written confirmation before you pay anything', 'English-speaking coordinator on WhatsApp']

export function About() {
  const t = useT()
  return (
    <>
      <PageHero eyebrow="About Us" title="A local team, a shared table" description="ALI TRAVEL designs private tours, cultural experiences, hotels and airport transfers across Uzbekistan." image={IMAGES.khiva} />
      <div className="shell grid gap-12 py-16 lg:grid-cols-2 lg:py-24">
        <div className="space-y-5 text-[17px] leading-relaxed text-ink">
          <p>{t('We are guides, drivers and hosts from Samarkand, Bukhara, Khiva and Tashkent. Every route we sell is one we have walked or driven ourselves.')}</p>
          <p>{t('Our approach is simple: clear prices, honest advice about the seasons, and a person you can message on WhatsApp from your first question to your last day.')}</p>
        </div>
        <ul className="space-y-4">{ABOUT_POINTS.map((x) => (
          <li key={x} className="rounded-sm border border-navy/10 bg-card p-5 font-heading text-[22px]">{t(x)}</li>))}</ul>
      </div>
    </>
  )
}

export function Contact() {
  const t = useT()
  const { settings } = useSettings()
  const [f, setF] = useState({ full_name: '', email: '', phone: '', subject: '', message: '', website: '' })
  const [errors, setErrors] = useState({})
  const [state, setState] = useState('idle')
  const set = (k) => (e) => setF((p) => ({ ...p, [k]: e.target.value }))
  async function submit(e) {
    e.preventDefault()
    const err = {}
    if (f.full_name.trim().length < 2) err.full_name = 'Please tell us your name.'
    if (!EMAIL_RE.test(f.email.trim())) err.email = 'A valid email is required.'
    if (f.message.trim().length < 10) err.message = 'Tell us a little more (at least 10 characters).'
    setErrors(err)
    if (Object.keys(err).length) return
    setState('saving')
    try { await api.post('/contact/', f); setState('done') } catch { setState('error') }
  }
  return (
    <>
      <Seo title={t('Contact')} />
      <PageHero eyebrow="Contact" title="Talk to a person" description="Questions, ideas, or a trip half-planned — write to us and we will reply by email." image={IMAGES.tashkent} />
      <div className="shell grid gap-12 py-16 lg:grid-cols-[1fr_1.3fr] lg:py-24">
        <div><Phones settings={settings} />{settings.email && <p className="mt-4"><a href={`mailto:${settings.email}`} className="break-all text-turquoise-deep">{settings.email}</a></p>}
          {settings.address && <p className="mt-4 text-ink">{settings.address}</p>}{settings.hours && <p className="mt-1 text-[14px] text-ink">{settings.hours}</p>}
          <ExtraContacts settings={settings} className="mt-4" />
          <Socials settings={settings} className="mt-6" /></div>
        {state === 'done' ? <Success title="Message received">{t('Thank you — we will reply by email soon.')}</Success> : (
          <form onSubmit={submit} noValidate className="space-y-4 rounded-sm border border-navy/12 bg-sand-soft/40 p-6">
            <Honeypot value={f.website} onChange={set('website')} />
            <Field label="Full name" error={errors.full_name}><input className="input" value={f.full_name} onChange={set('full_name')} /></Field>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Email" error={errors.email}><input type="email" className="input" value={f.email} onChange={set('email')} /></Field>
              <Field label="Phone"><input type="tel" className="input" value={f.phone} onChange={set('phone')} /></Field></div>
            <Field label="Subject"><input className="input" value={f.subject} onChange={set('subject')} /></Field>
            <Field label="Message" error={errors.message}><textarea rows={5} className="input" value={f.message} onChange={set('message')} /></Field>
            {state === 'error' && <p role="alert" className="text-[12px] text-destructive">{t('We could not send your message. Please try again.')}</p>}
            <button className="btn-primary" disabled={state === 'saving'}>{state === 'saving' && <Spinner />}{t('Send message')}</button>
          </form>)}
      </div>
    </>
  )
}
