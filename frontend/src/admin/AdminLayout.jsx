import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { BadgePercent, Bell, MapPinned, Building2, CalendarDays, Calculator, Coins, Handshake, Scale, ChevronDown, Compass, ExternalLink, FileText, Globe, KeyRound, Layers, LayoutGrid, Mail, PencilRuler, Search, Settings, Star, Users } from 'lucide-react'
import { api } from '../api'
import { useAuth } from '../hooks'
import { LANGS, useI18n } from '../i18n'
import LogoMark from '../components/LogoMark'
import MarketSwitch from '../components/MarketSwitch'
import { isLocal } from '../market'
import { adminLang } from '../lang'

const NAV = [
  { to: '/admin', end: true, label: 'Overview', icon: LayoutGrid },
  { to: '/admin/site', label: 'Site editor', icon: PencilRuler },
  { to: '/admin/map', label: 'Map', icon: MapPinned },
  { to: '/admin/tours', label: 'Tours & packages', icon: Compass },
  { to: '/admin/listings', label: 'Other listings', icon: Layers },
  { to: '/admin/promotions', label: 'Promotions', icon: BadgePercent },
  { to: '/admin/reviews', label: 'Reviews', icon: Star },
  { to: '/admin/group-pricing', label: 'Group pricing', icon: Coins },
  { to: '/admin/bookings', label: 'Bookings', icon: CalendarDays, badge: 'pending' },
  { to: '/admin/accounting', label: 'Accounting', icon: Calculator },
  { to: '/admin/customers', label: 'Customers', icon: Users },
  { to: '/admin/partners', label: 'Partners', icon: Building2 },
  { to: '/admin/partner-letters', label: 'Partner letters', icon: Handshake },
  { to: '/admin/enquiries', label: 'Enquiries', icon: Mail },
  { to: '/admin/content', label: 'Homepage content', icon: FileText },
  { to: '/admin/legal', label: 'Legal pages', icon: Scale },
  { to: '/admin/settings', label: 'Contact & settings', icon: Settings },
  { to: '/admin/account', label: 'Login and password', icon: KeyRound },
]

function SectionSearch() {
  const { t } = useI18n()
  const [q, setQ] = useState('')
  const nav = useNavigate()
  const needle = q.trim().toLowerCase()
  const matches = needle ? NAV.filter((n) => t(n.label).toLowerCase().includes(needle) || n.label.toLowerCase().includes(needle)) : []
  const go = (to) => { setQ(''); nav(to) }
  return (
    <div className="relative hidden sm:block">
      <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink" />
      <input value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && matches[0] && go(matches[0].to)}
        placeholder={t('Search sections')} aria-label={t('Search sections')}
        className="h-11 w-48 rounded-full border border-navy/10 bg-white pl-10 pr-4 text-[14px] outline-none focus:border-navy lg:w-60" />
      {matches.length > 0 && (
        <ul className="absolute left-0 right-0 z-30 mt-1 rounded-md border border-navy/10 bg-white p-1 shadow-lg">
          {matches.map((m) => <li key={m.to}><button onClick={() => go(m.to)} className="block w-full rounded px-3 py-2 text-left text-[14px] hover:bg-sand-soft">{t(m.label)}</button></li>)}
        </ul>
      )}
    </div>
  )
}

function AdminLanguage() {
  const { lang, setLang, t } = useI18n()
  return (
    // the button shows only the short code (UZ, RU…); the invisible select on top opens the full list, so it fits a phone header
    <label className="relative flex h-11 cursor-pointer items-center gap-1.5 rounded-full border border-navy/10 bg-white px-3 text-[13px] font-medium hover:bg-sand-soft">
      <Globe className="h-4 w-4 text-ink" aria-hidden="true" />
      <span aria-hidden="true">{lang.toUpperCase()}</span>
      <ChevronDown className="h-3.5 w-3.5 text-ink" aria-hidden="true" />
      <select value={lang} onChange={(e) => setLang(e.target.value)} className="absolute inset-0 h-full w-full cursor-pointer opacity-0" aria-label={t('Select language')}>
        {LANGS.map((l) => <option key={l.code} value={l.code}>{l.code.toUpperCase()} — {l.label}</option>)}
      </select>
    </label>
  )
}

export default function AdminLayout() {
  const { t, lang, setLang } = useI18n()
  useEffect(() => { const own = adminLang(); if (own && own !== lang) setLang(own) }, [])   // eslint-disable-line react-hooks/exhaustive-deps
  const { user, logout } = useAuth()
  const { pathname } = useLocation()
  const [stats, setStats] = useState(null)
  const [menu, setMenu] = useState(false)
  const [mobileNav, setMobileNav] = useState(false)
  const menuRef = useRef(null)

  const refreshStats = () => api.get('/admin-stats/').then(setStats).catch(() => {})
  useEffect(() => { refreshStats() }, [pathname])
  useEffect(() => { setMobileNav(false) }, [pathname])
  useEffect(() => {
    const close = (e) => { if (menuRef.current && !menuRef.current.contains(e.target)) setMenu(false) }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [])

  const current = useMemo(() => NAV.find((n) => (n.end ? pathname === n.to : pathname.startsWith(n.to))) || NAV[0], [pathname])
  const alerts = (stats?.pending || 0) + (stats?.new_messages || 0) + (stats?.pending_partners || 0)
  const display = user?.full_name?.includes('@') ? user.full_name.split('@')[0] : user?.full_name || 'Admin'

  const sidebar = (
    <aside className="flex h-full w-[275px] shrink-0 flex-col bg-navy text-ivory">
      <div className="px-7 pb-6 pt-7">
        <Link to="/admin" className="flex items-center gap-3">
          <LogoMark className="h-11 w-11 shrink-0" />
          <span className="flex flex-col leading-none">
            <span className="font-heading text-[24px]">ALI TRAVEL</span>
            <span className="mt-1.5 font-mono text-[9px] uppercase tracking-[0.28em] text-ivory/70">Uzbekistan</span>
          </span>
        </Link>
        <p className="mt-6 font-mono text-[10px] uppercase tracking-[0.24em] text-ivory/60">{t('Operations console')}</p>
      </div>
      <nav className="flex-1 overflow-y-auto px-4" aria-label={t('Admin sections')}>
        <ul className="space-y-1">
          {NAV.map(({ to, end, label, icon: Icon, badge }) => {
            const count = badge ? stats?.[badge] : 0
            return (
              <li key={to}>
                <NavLink to={to} end={end} className={({ isActive }) => `flex items-center gap-3.5 rounded-md px-3 py-3 text-[15px] transition-colors ${isActive ? 'bg-ivory/12 text-ivory' : 'text-ivory/85 hover:bg-ivory/8'}`}>
                  <Icon className="h-[18px] w-[18px] shrink-0" strokeWidth={1.7} />
                  <span className="flex-1">{t(label)}</span>
                  {count > 0 && <span className="grid h-6 min-w-6 place-items-center rounded-full bg-turquoise px-1.5 text-[11px] font-medium text-navy">{count}</span>}
                </NavLink>
              </li>
            )
          })}
        </ul>
      </nav>
      <Link to="/" className="m-4 flex items-center gap-3 rounded-md px-3 py-3 text-[14px] text-ivory/85 hover:bg-ivory/8"><ExternalLink className="h-[18px] w-[18px]" strokeWidth={1.7} />{t('View public site')}</Link>
    </aside>
  )

  return (
    <div className="flex h-screen bg-background text-navy">
      <div className="hidden lg:block">{sidebar}</div>
      {mobileNav && <div className="fixed inset-0 z-40 flex bg-navy/40 lg:hidden" onClick={() => setMobileNav(false)}><div onClick={(e) => e.stopPropagation()}>{sidebar}</div></div>}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-[66px] shrink-0 items-center justify-between gap-2 border-b border-navy/10 bg-ivory px-3 sm:gap-4 sm:px-5 lg:px-8">
          <div className="flex min-w-0 items-center gap-2 sm:gap-3">
            <button className="rounded p-1 lg:hidden" aria-label={t('Open sections')} onClick={() => setMobileNav(true)}><LayoutGrid className="h-5 w-5" /></button>
            <div className="min-w-0"><p className="hidden truncate font-mono text-[10px] uppercase tracking-[0.24em] text-ink sm:block">{t('ALI TRAVEL Admin')}</p><h1 className="truncate font-heading text-[20px] leading-tight sm:text-[26px] sm:leading-none">{t(current.label)}</h1></div>
          </div>
          <div className="flex shrink-0 items-center gap-2 sm:gap-3">
            <SectionSearch />
            <MarketSwitch size="sm" />
            <AdminLanguage />
            <Link to="/admin/bookings" aria-label={`${alerts} ${t('items need attention')}`} className="relative grid h-11 w-11 place-items-center rounded-full border border-navy/10 bg-white hover:bg-sand-soft">
              <Bell className="h-[18px] w-[18px]" />{alerts > 0 && <span className="absolute -right-0.5 -top-0.5 grid h-5 min-w-5 place-items-center rounded-full bg-turquoise px-1 text-[10px] font-medium">{alerts}</span>}
            </Link>
            <div className="relative" ref={menuRef}>
              <button onClick={() => setMenu((m) => !m)} className="flex h-11 items-center gap-2.5 rounded-full border border-navy/10 bg-white pl-1.5 pr-2 text-[14px] hover:bg-sand-soft sm:pr-3.5">
                <span className="grid h-8 w-8 place-items-center rounded-full bg-navy text-[12px] text-ivory">{display.charAt(0)}</span>
                <span className="hidden sm:inline">{display}</span><ChevronDown className="hidden h-4 w-4 sm:block" />
              </button>
              {menu && (
                <div className="absolute right-0 z-30 mt-2 w-52 rounded-md border border-navy/10 bg-white p-1 text-[14px] shadow-lg">
                  <p className="px-3 py-2 text-[12px] text-ink">{user?.email}</p>
                  <Link to="/admin/account" className="block rounded px-3 py-2 hover:bg-sand-soft">{t('Login and password')}</Link>
                  <Link to="/" className="block rounded px-3 py-2 hover:bg-sand-soft">{t('View public site')}</Link>
                  <button onClick={logout} className="block w-full rounded px-3 py-2 text-left hover:bg-sand-soft">{t('Sign out')}</button>
                </div>
              )}
            </div>
          </div>
        </header>
        {isLocal && <p className="shrink-0 border-b border-[#16a34a]/30 bg-[#f0fdf4] px-5 py-2 text-[13px] text-[#15803d] lg:px-8">🇺🇿 {t('You are editing the local site: its own tours, bookings and settings, prices in so\'m. The global site is not changed.')}</p>}
        <main className={pathname.startsWith('/admin/site') ? 'min-h-0 flex-1 overflow-hidden' : 'min-h-0 flex-1 overflow-y-auto px-5 py-8 lg:px-8'}><Outlet context={{ stats, refreshStats }} /></main>
      </div>
    </div>
  )
}
