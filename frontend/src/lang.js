// Which language the page is shown in.
// The public site always opens in English: a language the visitor picks is kept only while that browser tab stays open.
// The admin panel remembers its own language for good (the team works in Uzbek).

export const LANG_CODES = ['en', 'uz', 'ru', 'fr', 'de', 'es']
const SITE_KEY = 'ali-travel-locale'          // this tab (sessionStorage)
const ADMIN_KEY = 'ali-travel-admin-locale'   // the admin panel (localStorage)
const inAdmin = () => typeof window !== 'undefined' && window.location.pathname.startsWith('/admin')

function moveOldChoice() {
  // an older version kept the site language for good: it becomes the admin panel's language and the site starts in English
  const old = localStorage.getItem(SITE_KEY)
  if (!old) return
  if (LANG_CODES.includes(old) && !localStorage.getItem(ADMIN_KEY)) localStorage.setItem(ADMIN_KEY, old)
  localStorage.removeItem(SITE_KEY)
}

export function adminLang() {
  try { const v = localStorage.getItem(ADMIN_KEY); return LANG_CODES.includes(v) ? v : null } catch { return null }
}

export function readLang() {
  try {
    moveOldChoice()
    if (inAdmin() && adminLang()) return adminLang()
    const v = sessionStorage.getItem(SITE_KEY)
    if (LANG_CODES.includes(v)) return v
  } catch { /* storage unavailable */ }
  return 'en'
}

export function saveLang(code) {
  try {
    sessionStorage.setItem(SITE_KEY, code)
    if (inAdmin()) localStorage.setItem(ADMIN_KEY, code)
  } catch { /* storage unavailable */ }
}
