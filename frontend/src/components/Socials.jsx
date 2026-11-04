import { Send } from 'lucide-react'

// lucide-react no longer ships brand icons, so these are simple inline glyphs.
const glyph = (d) => (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{d}</svg>
)
const Instagram = glyph(<><rect x="3" y="3" width="18" height="18" rx="5" /><circle cx="12" cy="12" r="4" /><circle cx="17.5" cy="6.5" r="0.8" fill="currentColor" /></>)
const Facebook = glyph(<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8z" />)
const Youtube = glyph(<><rect x="2.5" y="5" width="19" height="14" rx="4" /><path d="m10 9 5 3-5 3z" fill="currentColor" /></>)

const XTwitter = glyph(<path d="M4 4l6.8 8.7L4.3 20h2l5.4-6.1L16.5 20H20l-7.1-9.1L19.2 4h-2l-5 5.6L8 4H4z" />)

const SOCIAL = [
  ['instagram_url', Instagram, 'Instagram', '@al1_travel1'], ['telegram_url', Send, 'Telegram', '@al1_travel1'],
  ['facebook_url', Facebook, 'Facebook', 'ALI TRAVEL'], ['youtube_url', Youtube, 'YouTube', '@Alitravel_uz'], ['x_url', XTwitter, 'X', '@alitraveluz'],
]

export function Socials({ settings, light, className = '' }) {
  const tone = light ? 'border-ivory/20 text-ivory/80 hover:border-turquoise hover:text-turquoise' : 'border-navy/15 text-navy/70 hover:border-navy hover:text-navy'
  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {SOCIAL.filter(([k]) => settings[k]).map(([k, Icon, label, handle]) => (
        <a key={k} href={settings[k]} target="_blank" rel="noopener noreferrer" aria-label={`ALI TRAVEL — ${label}`} title={`${label} ${handle}`}
          className={`grid h-10 w-10 place-items-center rounded-full border transition-colors ${tone}`}><Icon className="h-4 w-4" /></a>
      ))}
    </div>
  )
}
