import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useT } from '../i18n'
import Seo from '../components/Seo'

/** Any address the site does not know: a clear heading, one line and the way back home (search engines are told not to list it). */
export default function NotFound() {
  const t = useT()
  return (
    <div className="shell py-24 text-center">
      <Seo title={t('Page not found')} noindex />
      <p className="font-mono text-[11px] uppercase tracking-[0.24em] text-ink">404</p>
      <h1 className="display-lg mt-3 text-navy">{t('Page not found')}</h1>
      <p className="mx-auto mt-4 max-w-md text-[16px] leading-relaxed text-ink">{t('The page you opened does not exist or has moved.')}</p>
      <Link to="/" className="btn-primary mt-8"><ArrowLeft className="h-4 w-4" />{t('Back to the home page')}</Link>
    </div>
  )
}
