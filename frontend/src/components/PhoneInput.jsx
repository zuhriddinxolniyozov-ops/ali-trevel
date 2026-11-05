import { useMemo, useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { useI18n, useT } from '../i18n'

// Country (ISO code) and its calling code. Names come from the browser in the visitor's language.
const LIST = `AF93 AL355 DZ213 AD376 AO244 AG1268 AR54 AM374 AU61 AT43 AZ994 BS1242 BH973 BD880 BB1246 BY375 BE32 BZ501 BJ229 BT975
BO591 BA387 BW267 BR55 BN673 BG359 BF226 BI257 KH855 CM237 CA1 CV238 CF236 TD235 CL56 CN86 CO57 KM269 CG242 CD243 CR506 CI225 HR385
CU53 CY357 CZ420 DK45 DJ253 DM1767 DO1809 EC593 EG20 SV503 GQ240 ER291 EE372 SZ268 ET251 FJ679 FI358 FR33 GA241 GM220 GE995 DE49 GH233
GR30 GD1473 GT502 GN224 GW245 GY592 HT509 HN504 HK852 HU36 IS354 IN91 ID62 IR98 IQ964 IE353 IL972 IT39 JM1876 JP81 JO962 KZ7 KE254 KI686
KW965 KG996 LA856 LV371 LB961 LS266 LR231 LY218 LI423 LT370 LU352 MO853 MG261 MW265 MY60 MV960 ML223 MT356 MH692 MR222 MU230 MX52 FM691
MD373 MC377 MN976 ME382 MA212 MZ258 MM95 NA264 NR674 NP977 NL31 NZ64 NI505 NE227 NG234 KP850 MK389 NO47 OM968 PK92 PW680 PS970 PA507
PG675 PY595 PE51 PH63 PL48 PT351 QA974 RO40 RU7 RW250 KN1869 LC1758 VC1784 WS685 SM378 ST239 SA966 SN221 RS381 SC248 SL232 SG65 SK421
SI386 SB677 SO252 ZA27 KR82 SS211 ES34 LK94 SD249 SR597 SE46 CH41 SY963 TW886 TJ992 TZ255 TH66 TL670 TG228 TO676 TT1868 TN216 TR90 TM993
TV688 UG256 UA380 AE971 GB44 US1 UY598 UZ998 VU678 VA379 VE58 VN84 YE967 ZM260 ZW263`.split(/\s+/).map((x) => ({ iso: x.slice(0, 2), code: x.slice(2) }))
const CODE = Object.fromEntries(LIST.map((x) => [x.iso, x.code]))
// Shown first: Uzbekistan, its neighbours and the countries most of our travellers come from.
const TOP = ['UZ', 'KZ', 'KG', 'TJ', 'TM', 'RU', 'TR', 'US', 'GB', 'DE', 'FR']
const flag = (iso) => String.fromCodePoint(...[...iso].map((c) => 0x1f1a5 + c.charCodeAt(0)))

/** The country whose calling code starts the number (the longest match), or null. */
function countryOf(value) {
  const digits = String(value || '').replace(/[^\d+]/g, '')
  if (!digits.startsWith('+')) return null
  const hit = LIST.filter((x) => digits.slice(1).startsWith(x.code)).sort((a, b) => b.code.length - a.code.length || (TOP.indexOf(b.iso) >= 0) - (TOP.indexOf(a.iso) >= 0))
  return hit[0] || null
}

/**
 * A phone number: the visitor picks the country (Uzbekistan +998 by default) and types the rest.
 * value / onChange carry the whole number such as "+998 90 123 45 67", or "" while nothing is typed.
 */
export default function PhoneInput({ value = '', onChange, invalid = false, placeholder }) {
  const { lang } = useI18n()
  const t = useT()
  const [iso, setIso] = useState(() => countryOf(value)?.iso || 'UZ')
  const code = CODE[iso]
  const rest = value.startsWith(`+${code}`) ? value.slice(code.length + 1).trim() : value.replace(/^\+\d*\s*/, '')
  const names = useMemo(() => {
    let dn = null
    try { dn = new Intl.DisplayNames([lang, 'en'], { type: 'region' }) } catch { /* old browser: show the codes */ }
    const name = (x) => dn?.of(x) || x
    const all = LIST.map((x) => ({ ...x, name: name(x.iso) })).sort((a, b) => a.name.localeCompare(b.name, lang))
    return [...TOP.map((t) => all.find((x) => x.iso === t)), ...all.filter((x) => !TOP.includes(x.iso))]
  }, [lang])

  const emit = (countryCode, number) => onChange(number.trim() ? `+${countryCode} ${number.trim()}` : '')
  const pickCountry = (e) => { setIso(e.target.value); emit(CODE[e.target.value], rest) }
  const type = (e) => {
    let text = e.target.value.replace(/[^\d\s\-()+]/g, '')
    if (text.trim().startsWith('+')) {        // a whole number was pasted: take its country from it
      const found = countryOf(text)
      if (found) { setIso(found.iso); emit(found.code, text.replace(/\s/g, '').slice(found.code.length + 1)); return }
      text = text.replace(/\+/g, '')
    }
    emit(code, text.replace(/\+/g, ''))
  }

  return (
    <div className="mt-1.5 flex gap-2">
      <div className={`relative flex h-11 shrink-0 items-center gap-1.5 rounded-sm border bg-white px-3 text-[14px] font-normal text-navy focus-within:border-navy ${invalid ? 'border-destructive' : 'border-navy/15'}`}>
        <span aria-hidden="true" className="text-[17px] leading-none">{flag(iso)}</span>
        <span>+{code}</span>
        <ChevronDown className="h-3.5 w-3.5 text-ink" aria-hidden="true" />
        <select value={iso} onChange={pickCountry} aria-label={t('Country code')} className="absolute inset-0 h-full w-full cursor-pointer opacity-0">
          {names.map((x) => <option key={x.iso} value={x.iso}>{`${x.name} (+${x.code})`}</option>)}
        </select>
      </div>
      <input type="tel" inputMode="tel" autoComplete="tel-national" className="input !mt-0 h-11 min-w-0 flex-1" placeholder={placeholder || (iso === 'UZ' ? '90 123 45 67' : '')}
        value={rest} onChange={type} aria-invalid={invalid} />
    </div>
  )
}
