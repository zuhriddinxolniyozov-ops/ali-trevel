import { Link, useParams } from 'react-router-dom'
import { useFetch } from '../hooks'
import { useI18n } from '../i18n'
import { EmptyState, Skeleton } from '../components/ui'
import LegalText, { headingId, parseLegal } from '../components/LegalText'

const PAGES = [['privacy', 'Privacy Policy'], ['terms', 'Terms and Conditions'], ['cancellation', 'Cancellation Policy']]

/** Privacy policy, terms or cancellation policy, loaded from the admin-editable legal pages. */
import Seo from '../components/Seo'

export default function Legal() {
  const { t, lang } = useI18n()
  const { page } = useParams()
  const { data, loading, error } = useFetch(PAGES.some(([k]) => k === page) ? `/legal/${page}/` : null)
  if (!PAGES.some(([k]) => k === page) || error) return <div className="shell py-24"><EmptyState title="Page not found" /></div>
  if (loading || !data) return <div className="shell py-24"><Skeleton count={3} /></div>

  const headings = parseLegal(data.body).filter((b) => b.type === 'h2')
  const updated = new Date(`${data.updated}T12:00:00`).toLocaleDateString(lang === 'uz' ? 'uz-UZ' : lang, { year: 'numeric', month: 'long', day: 'numeric' })
  return (
    <div className="shell py-14 lg:py-20">
      <Seo title={data.title} />
      <header className="max-w-3xl animate-rise-in">
        <p className="eyebrow">{t('Legal')}</p>
        <h1 className="display-lg mt-3 text-navy">{data.title}</h1>
        <p className="mt-3 font-mono text-[11px] uppercase tracking-[0.14em] text-ink">{t('Last updated')}: {updated}</p>
      </header>

      <div className="mt-10 grid gap-10 lg:grid-cols-[250px_1fr] lg:gap-16">
        <nav aria-label={t('On this page')} className="lg:sticky lg:top-28 lg:self-start">
          <details className="rounded-sm border border-navy/10 bg-white p-4 lg:border-0 lg:bg-transparent lg:p-0" open>
            <summary className="cursor-pointer font-mono text-[10px] uppercase tracking-[0.2em] text-ink lg:cursor-default">{t('On this page')}</summary>
            <ol className="mt-3 space-y-2 text-[14px]">
              {headings.map((h, i) => <li key={i}><a href={`#${headingId(i)}`} className="text-navy/80 hover:text-turquoise-deep">{h.text}</a></li>)}
            </ol>
          </details>
          <ul className="mt-6 hidden space-y-2 border-t border-navy/10 pt-5 text-[13px] lg:block">
            {PAGES.filter(([k]) => k !== page).map(([k, label]) => <li key={k}><Link to={`/legal/${k}`} className="text-ink hover:text-navy">{t(label)}</Link></li>)}
          </ul>
        </nav>
        <article className="max-w-3xl"><LegalText body={data.body} />
          <p className="mt-12 rounded-sm border border-gold/40 bg-sand-soft/60 p-4 text-[14px] text-ink">{t('Questions about this page? Write to us at the address in the footer and we will gladly help.')}</p>
          <ul className="mt-6 flex flex-wrap gap-x-6 gap-y-2 text-[14px] lg:hidden">{PAGES.filter(([k]) => k !== page).map(([k, label]) => <li key={k}><Link to={`/legal/${k}`} className="text-turquoise-deep">{t(label)}</Link></li>)}</ul>
        </article>
      </div>
    </div>
  )
}
