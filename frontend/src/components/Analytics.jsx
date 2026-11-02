import { useEffect, useState } from 'react'
import { useSettings } from '../hooks'
import { useT } from '../i18n'

const KEY = 'ali.analytics'
const read = () => { try { return localStorage.getItem(KEY) } catch { return null } }
const write = (v) => { try { localStorage.setItem(KEY, v) } catch { /* private window: asked again next time */ } }

function loadGoogleAnalytics(id) {
  if (document.getElementById('ga-script')) return
  const script = document.createElement('script')
  script.id = 'ga-script'; script.async = true; script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`
  document.head.appendChild(script)
  window.dataLayer = window.dataLayer || []
  window.gtag = function gtag() { window.dataLayer.push(arguments) }
  window.gtag('js', new Date())
  window.gtag('config', id, { anonymize_ip: true })
}

/**
 * Google Analytics, only when an admin has entered a measurement ID (Contact & settings) and the visitor has said yes.
 * Nothing is loaded and nothing is stored about the visitor until then.
 */
export default function Analytics() {
  const t = useT()
  const { settings } = useSettings()
  const id = (settings.analytics_id || '').trim()
  const [choice, setChoice] = useState(read)
  useEffect(() => { if (id && choice === 'yes') loadGoogleAnalytics(id) }, [id, choice])
  if (!id || choice) return null
  const answer = (v) => { write(v); setChoice(v) }
  return (
    <div role="dialog" aria-label={t('Cookies')} className="fixed inset-x-3 bottom-3 z-50 mx-auto max-w-2xl rounded-md border border-navy/15 bg-white p-4 shadow-2xl print:hidden">
      <p className="text-[13.5px] leading-relaxed text-ink">{t('We would like to use analytics cookies to understand how the website is used and to improve it. Nothing is collected unless you accept.')}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        <button onClick={() => answer('yes')} className="btn-primary !h-10 text-[13px]">{t('Accept')}</button>
        <button onClick={() => answer('no')} className="btn-outline !h-10 text-[13px]">{t('Decline')}</button>
      </div>
    </div>
  )
}
