import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { Check, Globe, Mail, Menu, Phone, Send, Tag, X } from 'lucide-react'
import { useAuth, useFetch, useSettings } from '../hooks'
import { LANGS, useI18n } from '../i18n'
import { WhatsAppButton } from './Trust'
import { SelectionProvider } from './Selection'
import Analytics from './Analytics'
import { Socials } from './Socials'

export { Socials }

const NAV = [
  ['Destinations', '/destinations'], ['Tours & Experiences', '/tours'], ['Hotels', '/hotels'],
  ['Transport', '/transport'], ['Local Food', '/food'], ['About Us', '/about'], ['Contact', '/contact'],
]
export function Logo({ light = false }) {
  return (
    <Link to="/" className="group flex shrink-0 items-center gap-3 whitespace-nowrap" aria-label="ALI TRAVEL">
      <span className={`grid h-10 w-10 place-items-center rounded-[10px] transition-transform duration-500 group-hover:rotate-[8deg] ${light ? 'bg-ivory/10 ring-1 ring-ivory/25' : 'bg-navy'}`}>
        <svg viewBox="0 0 32 32" className="h-5 w-5" aria-hidden="true"><path d="M16 3l3.6 7.4L28 11.6l-5.8 5.6 1.4 8L16 21.5l-7.6 3.7 1.4-8L4 11.6l8.4-1.2z" fill="#c5a059" /></svg>
      </span>
      <span className="flex flex-col leading-none">
        <span className={`font-heading text-[22px] tracking-[0.01em] ${light ? 'text-ivory' : 'text-navy'}`}>ALI TRAVEL</span>
        <span className={`mt-1 font-mono text-[9px] uppercase tracking-[0.28em] ${light ? 'text-ivory/70' : 'text-ink'}`}>Uzbekistan</span>
      </span>
    </Link>
  )
}

/** Extra contact lines the owner added in Settings: a label, a value and an optional link. */
export function ExtraContacts({ settings, light, className = '' }) {
  const rows = (settings.extra_contacts || []).filter((r) => r && (r.label || r.value))
  if (!rows.length) return null
  const link = light ? 'text-ivory hover:text-turquoise' : 'text-turquoise-deep hover:text-navy'
  return (
    <ul className={`space-y-1.5 text-[14px] ${light ? 'text-ivory/80' : 'text-ink'} ${className}`}>
      {rows.map((r, i) => (
        <li key={i}>{r.label && <span className={`mr-1.5 ${light ? 'text-ivory/55' : 'text-ink/70'}`}>{r.label}:</span>}
          {r.url ? <a href={r.url} target={r.url.startsWith('http') ? '_blank' : undefined} rel="noopener noreferrer" className={`break-words underline-offset-2 hover:underline ${link}`}>{r.value || r.url}</a> : <span className="break-words">{r.value}</span>}</li>
      ))}
    </ul>
  )
}

export function Phones({ settings, light }) {
  const cls = light ? 'text-ivory hover:text-turquoise' : 'text-navy hover:text-turquoise-deep'
  return (
    <ul className="space-y-2">
      {[settings.phone_primary, settings.phone_secondary].filter(Boolean).map((p) => (
        <li key={p}><a href={`tel:${p}`} className={`inline-flex items-center gap-2 ${cls}`}>
          <Phone className="h-4 w-4 shrink-0 opacity-70" /><span className="font-mono text-[13.5px] tracking-tight">{p}</span></a></li>
      ))}
    </ul>
  )
}


function LanguageMenu() {
  const { lang, setLang, t } = useI18n()
  const [open, setOpen] = useState(false)
  return (
    <div className="relative hidden sm:block">
      <button type="button" onClick={() => setOpen((o) => !o)} aria-label={t('Select language')} aria-expanded={open}
        className="flex items-center gap-1.5 rounded-full px-2.5 py-2 text-[12px] uppercase tracking-[0.08em] text-ink transition-colors hover:text-navy">
        <Globe className="h-4 w-4" />{lang}
      </button>
      {open && (
        <div className="absolute right-0 z-50 mt-2 w-48 rounded-md border border-navy/10 bg-ivory p-1 shadow-lg" onMouseLeave={() => setOpen(false)}>
          {LANGS.map((l) => (
            <button key={l.code} onClick={() => { setLang(l.code); setOpen(false) }}
              className="flex w-full items-center justify-between rounded px-3 py-2 text-left text-[14px] text-navy hover:bg-sand-soft">
              {l.label}{lang === l.code && <Check className="h-4 w-4 text-turquoise-deep" />}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

/** Running promotions ("20% off all tours"), shown above the header until dismissed for the session. */
function PromoBar() {
  const { t } = useI18n()
  const { data } = useFetch('/promotions-active/', { list: true })
  const [hidden, setHidden] = useState(() => { try { return sessionStorage.getItem('ali-promo-hidden') === '1' } catch { return false } })
  const promo = data[0]
  if (!promo || hidden) return null
  const ends = promo.ends_on && new Date(`${promo.ends_on}T12:00:00`).toLocaleDateString(undefined, { day: 'numeric', month: 'long' })
  return (
    <div className="bg-destructive text-white" role="region" aria-label={promo.title}>
      <div className="shell flex items-center justify-center gap-3 py-2 text-center text-[13px]">
        <Tag className="hidden h-4 w-4 shrink-0 sm:block" aria-hidden="true" />
        <p><strong className="font-semibold">{promo.title}</strong>{promo.message && <> — {promo.message}</>}{ends && <span className="opacity-90"> · {t('Until {date}', { date: ends })}</span>}</p>
        <Link to="/tours" className="hidden whitespace-nowrap font-medium underline underline-offset-2 sm:inline">{t('See offers')}</Link>
        <button type="button" aria-label={t('Close')} onClick={() => { setHidden(true); try { sessionStorage.setItem('ali-promo-hidden', '1') } catch { /* private mode */ } }} className="ml-1 shrink-0 rounded-full p-1 hover:bg-white/15"><X className="h-4 w-4" /></button>
      </div>
    </div>
  )
}

function Header() {
  const { t, lang, setLang } = useI18n()
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)
  const [menu, setMenu] = useState(false)
  const { pathname } = useLocation()
  const { user, isAuthenticated, logout } = useAuth()
  const { settings } = useSettings()
  useEffect(() => { setOpen(false) }, [pathname])
  useEffect(() => {
    const on = () => setScrolled(window.scrollY > 12)
    on(); window.addEventListener('scroll', on, { passive: true })
    return () => window.removeEventListener('scroll', on)
  }, [])

  return (
    <header className={`sticky top-0 z-50 border-b border-navy/10 bg-ivory/95 backdrop-blur-md transition-shadow duration-500 ${scrolled ? 'shadow-[0_18px_40px_-32px_rgba(0,35,102,0.55)]' : ''}`}>
      <div className="shell flex h-[74px] items-center justify-between gap-6">
        <Logo />
        <nav aria-label={t('Main navigation')} className="hidden items-center gap-3 xl:flex">
          {NAV.map(([label, to]) => (
            <NavLink key={to} to={to} className={({ isActive }) => `link-underline whitespace-nowrap text-[11px] uppercase tracking-[0.04em] transition-colors ${isActive ? 'text-navy' : 'text-ink hover:text-navy'}`}>{t(label)}</NavLink>
          ))}
        </nav>
        <div className="flex items-center gap-2 sm:gap-3">
          <LanguageMenu />
          {isAuthenticated ? (
            <div className="relative hidden lg:block">
              <button type="button" onClick={() => setMenu((m) => !m)} className="inline-flex items-center gap-2 rounded-full px-3 py-2 text-[13px] font-medium text-navy hover:bg-navy/5">
                <span className="grid h-7 w-7 place-items-center rounded-full bg-navy text-[11px] text-ivory">{(user?.full_name || user?.email || 'A').slice(0, 1).toUpperCase()}</span>
                {user?.full_name ? user.full_name.split(' ')[0] : t('Account')}
              </button>
              {menu && (
                <div onClick={() => setMenu(false)} className="absolute right-0 mt-2 w-56 rounded-md border border-navy/10 bg-ivory p-1 text-sm shadow-lg">
                  <Link className="block rounded px-3 py-2 hover:bg-sand-soft" to="/account">{t('My account')}</Link>
                  <Link className="block rounded px-3 py-2 hover:bg-sand-soft" to="/partners/dashboard">{t('Partner dashboard')}</Link>
                  {user?.role === 'admin' && <Link className="block rounded px-3 py-2 hover:bg-sand-soft" to="/admin">{t('Admin dashboard')}</Link>}
                  <button className="block w-full rounded px-3 py-2 text-left hover:bg-sand-soft" onClick={logout}>{t('Sign out')}</button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login" className="hidden rounded-full px-3 py-2 text-[13px] font-medium text-navy hover:bg-navy/5 lg:inline-flex">{t('Sign In')}</Link>
          )}
          <Link to="/plan" className="btn-liquid hidden h-11 shrink-0 items-center whitespace-nowrap rounded-full bg-navy px-5 text-[13px] font-medium tracking-[0.02em] text-ivory hover:text-navy sm:inline-flex">{t('Plan My Trip')}</Link>
          <button className="rounded-full p-2 text-navy xl:hidden" aria-label={t('Open menu')} onClick={() => setOpen(true)}><Menu className="h-5 w-5" /></button>
        </div>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 bg-navy/40" onClick={() => setOpen(false)}>
          <aside className="ml-auto flex h-full w-[88%] max-w-sm flex-col bg-ivory" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between border-b border-navy/10 px-6 py-6"><Logo /><button aria-label={t('Close menu')} onClick={() => setOpen(false)}><X className="h-5 w-5" /></button></div>
            <nav className="flex-1 overflow-y-auto px-6 py-6" aria-label={t('Mobile navigation')}>
              <ul className="space-y-1">
                {NAV.map(([label, to]) => (
                  <li key={to}><NavLink to={to} className={({ isActive }) => `block rounded-md px-3 py-3 font-heading text-[22px] ${isActive ? 'bg-sand-soft text-navy' : 'text-navy/80 hover:bg-sand-soft'}`}>{t(label)}</NavLink></li>
                ))}
              </ul>
              <div className="mt-6 border-t border-navy/10 pt-5">
                <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink">{t('Language')}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {LANGS.map((l) => (
                    <button key={l.code} onClick={() => setLang(l.code)} className={`rounded-full border px-3 py-1.5 text-[12px] ${lang === l.code ? 'border-navy bg-navy text-ivory' : 'border-navy/15 text-navy/70'}`}>{l.label}</button>
                  ))}
                </div>
              </div>
              <div className="mt-6 border-t border-navy/10 pt-5">
                <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink">{t('Call us')}</p>
                <div className="mt-3"><Phones settings={settings} /></div>
                <Socials settings={settings} className="mt-4" />
              </div>
            </nav>
            <div className="space-y-2 border-t border-navy/10 px-6 py-6">
              <Link to="/plan" className="btn-primary w-full">{t('Plan My Trip')}</Link>
              {isAuthenticated ? (
                <><Link to="/account" className="btn-outline w-full">{t('My account')}</Link><button className="h-12 w-full text-[13px] text-ink" onClick={logout}>{t('Sign out')}</button></>
              ) : <Link to="/login" className="btn-outline w-full">{t('Sign In')}</Link>}
            </div>
          </aside>
        </div>
      )}
    </header>
  )
}

const EXPLORE = [['Destinations', '/destinations'], ['Tours & Experiences', '/tours'], ['Hotels', '/hotels'], ['Airport Transfers', '/transport'], ['Local Food', '/food']]
const COMPANY = [['About Us', '/about'], ['Contact', '/contact'], ['Plan My Trip', '/plan'], ['Partner Registration', '/partners/register'], ['Partner Sign In', '/partners']]
const LEGAL = [['Privacy Policy', '/legal/privacy'], ['Terms and Conditions', '/legal/terms'], ['Cancellation Policy', '/legal/cancellation'], ['Photo credits', '/credits']]

function FooterLinks({ title, items }) {
  const { t } = useI18n()
  return (
    <nav aria-label={title}>
      <h2 className="font-mono text-[10px] uppercase tracking-[0.24em] text-ivory/50">{t(title)}</h2>
      <ul className="mt-5 space-y-3">{items.map(([l, to]) => <li key={to}><Link to={to} className="link-underline text-[14px] text-ivory/80 hover:text-ivory">{t(l)}</Link></li>)}</ul>
    </nav>
  )
}

function Footer() {
  const { t } = useI18n()
  const { settings } = useSettings()
  return (
    <footer className="relative overflow-hidden bg-navy text-ivory">
      <div className="girih pointer-events-none absolute inset-0 opacity-[0.18]" aria-hidden="true" />
      <div className="shell relative py-14 lg:py-20">
        <div className="grid gap-12 lg:grid-cols-[1.4fr_1fr_1fr_1.2fr]">
          <div>
            <Logo light />
            <p className="mt-4 font-heading text-[19px] text-gold">{t('Discover the Beauty of Uzbekistan!')}</p>
            <p className="mt-4 max-w-xs text-[15px] leading-relaxed text-ivory/70">{t('A local team crafting private journeys, cultural experiences and seamless travel across the Silk Road cities of Uzbekistan.')}</p>
            <Socials settings={settings} light className="mt-6" />
          </div>
          <FooterLinks title="Explore" items={EXPLORE} />
          <FooterLinks title="Company" items={COMPANY} />
          <div>
            <h2 className="font-mono text-[10px] uppercase tracking-[0.24em] text-ivory/50">{t('Contact')}</h2>
            <div className="mt-5"><Phones settings={settings} light /></div>
            {settings.email && <p className="mt-4 flex items-start gap-2 text-[14px] text-ivory/80"><Mail className="mt-0.5 h-4 w-4 shrink-0 text-turquoise" /><a href={`mailto:${settings.email}`} className="break-all hover:text-ivory">{settings.email}</a></p>}
            {settings.address && <p className="mt-3 text-[14px] text-ivory/80">{settings.address}</p>}
            {settings.hours && <p className="mt-1 text-[13px] text-ivory/60">{settings.hours}</p>}
            <ExtraContacts settings={settings} light className="mt-3" />
            <ul className="mt-6 space-y-2">{LEGAL.map(([l, to]) => <li key={to}><Link to={to} className="text-[13px] text-ivory/55 hover:text-ivory">{t(l)}</Link></li>)}</ul>
          </div>
        </div>
        <div className="hairline-gold mt-14" />
        <div className="mt-6 flex flex-col gap-3 text-[12px] text-ivory/50 sm:flex-row sm:items-center sm:justify-between">
          <p>© {new Date().getFullYear()} ALI TRAVEL. {t('All rights reserved.')}</p>
          <p>{t('Listings marked as sample are demonstration content and are not yet confirmed by our partners.')}</p>
        </div>
      </div>
    </footer>
  )
}

export default function Layout() {
  const { pathname } = useLocation()
  useEffect(() => { window.scrollTo(0, 0) }, [pathname])
  return (
    <SelectionProvider>
    <div className="flex min-h-screen flex-col bg-background">
      <PromoBar />
      <Header />
      <main id="main-content" className="flex-1"><Outlet /></main>
      <Footer />
      <WhatsAppButton />
      <Analytics />
    </div>
    </SelectionProvider>
  )
}
