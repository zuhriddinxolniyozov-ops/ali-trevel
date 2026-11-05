import { useT } from '../i18n'
import { MARKET, setMarket } from '../market'

/**
 * Global / Local: which version of the site is shown. The global one (US dollars) opens by default; the local one has the same
 * tours with their own prices in so'm. In the admin panel it decides which version is being edited.
 */
export default function MarketSwitch({ className = '', size = 'md' }) {
  const t = useT()
  const pad = size === 'sm' ? 'h-8 px-2.5 text-[12px]' : 'h-9 px-3.5 text-[12.5px]'
  const options = [['global', '🌍', t('Global')], ['local', '🇺🇿', t('Local')]]
  return (
    <div role="radiogroup" aria-label={t('Site version')} className={`inline-flex shrink-0 items-center rounded-full border border-navy/15 bg-white p-0.5 ${className}`}>
      {options.map(([key, icon, label]) => {
        const on = MARKET === key
        return (
          <button key={key} type="button" role="radio" aria-checked={on} onClick={() => setMarket(key)}
            className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full font-medium transition-colors ${pad} ${on ? 'bg-navy text-ivory' : 'text-navy hover:bg-sand-soft'}`}>
            {size !== 'sm' && <span aria-hidden="true" className="text-[13px] leading-none">{icon}</span>}{label}
          </button>
        )
      })}
    </div>
  )
}
