import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { api } from './api'
import { STRINGS } from './strings'
import { localCurrencyText } from './market'

export const LANGS = [
  { code: 'en', label: 'English' },
  { code: 'uz', label: "O'zbekcha" },
  { code: 'ru', label: 'Русский' },
  { code: 'fr', label: 'Français' },
  { code: 'de', label: 'Deutsch' },
  { code: 'es', label: 'Español' },
]
const COLUMN = { uz: 0, ru: 1, fr: 2, de: 3, es: 4 }
export const LANG_KEY = 'ali-travel-locale'

export const getLang = () => {
  try {
    const v = localStorage.getItem(LANG_KEY)
    return LANGS.some((l) => l.code === v) ? v : 'en'
  } catch { return 'en' }
}

const I18nContext = createContext(null)
export const useI18n = () => useContext(I18nContext)
export const useT = () => useContext(I18nContext).t

/**
 * Interface copy is keyed by its English text. Lookup order for a language:
 * admin override (SiteText) -> built-in translation -> English (with an English admin override applied).
 */
export function I18nProvider({ children }) {
  const [lang, setLangState] = useState(getLang)
  const [overrides, setOverrides] = useState({})

  const refresh = useCallback(() => {
    api.get('/texts/').then(setOverrides).catch(() => setOverrides({}))
  }, [])
  useEffect(() => { refresh() }, [refresh])
  useEffect(() => { document.documentElement.lang = lang }, [lang])

  const setLang = (code) => {
    try { localStorage.setItem(LANG_KEY, code) } catch { /* storage unavailable */ }
    setLangState(code)
  }

  const value = useMemo(() => {
    // Placeholders like {city} are filled from `params` after the lookup, so word order can differ per language.
    const fill = (text, params) => (params ? text.replace(/\{(\w+)\}/g, (m, k) => (k in params ? params[k] : m)) : text)
    const lookup = (key, params) => {
      if (lang !== 'en') {
        const own = overrides[lang]?.[key] || STRINGS[key]?.[COLUMN[lang]]
        if (own) return fill(own, params)
        if (import.meta.env.DEV && typeof key === 'string' && !STRINGS[key]) (window.__untranslated ||= new Set()).add(key)
      }
      return fill(overrides.en?.[key] || key, params)
    }
    const t = (key, params) => localCurrencyText(lookup(key, params), lang)
    // Photos that admins replaced in the site editor are stored as overrides keyed by the original URL.
    const img = (url) => overrides.en?.[`image:${url}`] || url
    return { t, lang, setLang, overrides, refresh, img }
  }, [lang, overrides, refresh])

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}
