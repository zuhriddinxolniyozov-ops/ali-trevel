import { Link, useLocation } from 'react-router-dom'
import { LockKeyhole } from 'lucide-react'
import { useAuth } from '../hooks'
import { useT } from '../i18n'
import { Spinner } from './ui'

/**
 * Shown instead of a booking form to visitors who are not signed in. Bookings come only from accounts whose e-mail address was
 * confirmed with a code, so fake requests and made-up addresses cannot reach the team. After signing in the visitor comes back here.
 */
export default function SignInToBook({ className = '', id = 'book' }) {
  const t = useT()
  const { ready } = useAuth()
  const { pathname, search } = useLocation()
  const from = `${pathname}${search}`
  return (
    <div id={id} className={`scroll-mt-24 rounded-sm border border-navy/12 bg-sand-soft/40 p-5 ${className}`}>
      <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink">{t('Send a booking request')}</p>
      {!ready ? <div className="py-6"><Spinner /></div> : (
        <>
          <p className="mt-3 flex items-center gap-2 text-[17px] font-semibold text-navy"><LockKeyhole className="h-5 w-5 text-turquoise-deep" aria-hidden="true" />{t('Sign in to book')}</p>
          <p className="mt-2 text-[13.5px] leading-relaxed text-ink">{t('To protect you and us from fake requests, bookings are made from an account. Creating one takes a minute: we send a code to your e-mail to confirm it.')}</p>
          <Link to="/login" state={{ from }} className="btn-primary mt-4 w-full">{t('Sign in')}</Link>
          <Link to="/register" state={{ from }} className="btn-outline mt-2 w-full">{t('Create an account')}</Link>
        </>
      )}
    </div>
  )
}
