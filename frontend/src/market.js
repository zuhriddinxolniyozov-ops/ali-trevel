import { readLang } from './lang'

// Two versions of the site: "global" (US dollars, the default) and "local" (for Uzbekistan, prices in so'm).
// The site always opens in the global version. A choice of the local one is kept only while that browser tab stays open
// (sessionStorage), so a new visit starts global again; a link with ?market=local or ?market=global also sets it. Every request
// tells the server which one it is for (see api.js), and switching reloads the page so everything is read again from that version.

export const MARKET_KEY = 'ali-travel-market'
export const MARKETS = ['global', 'local']

function readMarket() {
  try {
    localStorage.removeItem(MARKET_KEY)   // an older version remembered the choice for good: forget it
    const fromLink = new URLSearchParams(window.location.search).get('market')
    if (MARKETS.includes(fromLink)) { sessionStorage.setItem(MARKET_KEY, fromLink); return fromLink }
    const saved = sessionStorage.getItem(MARKET_KEY)
    return MARKETS.includes(saved) ? saved : 'global'
  } catch { return 'global' }
}

/** The version this page shows; fixed while the page is open. */
export const MARKET = readMarket()
export const isLocal = MARKET === 'local'

export function setMarket(next) {
  if (!MARKETS.includes(next) || next === MARKET) return
  try { sessionStorage.setItem(MARKET_KEY, next) } catch { /* storage unavailable: the link below still carries it */ }
  const url = new URL(window.location.href)
  url.searchParams.delete('market')
  if (next === 'local') url.searchParams.set('market', 'local')   // works even where the browser cannot remember it
  window.location.assign(url.toString())
}

/** So'm prices in whole ten thousands from 100 000 (thousands from 10 000, hundreds below), as on the server; dollars to the cent. */
export function roundPrice(value) {
  const n = Number(value) || 0
  if (!isLocal) return Math.round(n * 100) / 100
  const step = n >= 100000 ? 10000 : n >= 10000 ? 1000 : 100
  return Math.round(n / step) * step
}

const SOM = { ru: 'сум' }
const currentLang = () => readLang()

/** 1 746 000 so'm */
export function som(value) {
  const n = Math.round(Number(value) || 0)
  return `${String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')} ${SOM[currentLang()] || "so'm"}`
}

// On the local site the interface speaks of so'm instead of dollars (labels like "Price (USD)" or "Amounts are in US dollars").
const PHRASES = {
  en: [[/in US dollars/g, "in Uzbek so'm"], [/US dollars/g, "Uzbek so'm"], [/\bUSD\b/g, 'UZS']],
  uz: [[/AQSH dollarida/gi, "so'mda"], [/AQSH dollari/gi, "so'm"], [/\bUSD\b/g, "so'm"]],
  ru: [[/в долларах США/g, 'в сумах'], [/доллар(ах|ы|ов) США/g, 'сум'], [/\bUSD\b/g, 'сум']],
  fr: [[/en dollars américains/g, 'en sums ouzbeks'], [/\bUSD\b/g, 'UZS']],
  de: [[/in US-Dollar/g, 'in usbekischen Sum'], [/\bUSD\b/g, 'UZS']],
  es: [[/en dólares estadounidenses/g, 'en sumos uzbekos'], [/\bUSD\b/g, 'UZS']],
}
export function localCurrencyText(text, lang) {
  if (!isLocal || typeof text !== 'string') return text
  return (PHRASES[lang] || PHRASES.en).reduce((s, [pattern, value]) => s.replace(pattern, value), text)
}
