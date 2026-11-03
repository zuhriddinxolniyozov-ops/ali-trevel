import { Link } from 'react-router-dom'
import { Reveal } from '../hooks'
import { useT } from '../i18n'
import { CITY, OUTLINE } from '../silkRoadGeo'

/** Smooth curve through the given cities (Catmull-Rom turned into Bezier segments). */
function curve(names) {
  const p = names.map((n) => CITY[n])
  let d = `M${p[0][0]} ${p[0][1]}`
  for (let i = 0; i < p.length - 1; i += 1) {
    const [p0, p1, p2, p3] = [p[i - 1] || p[i], p[i], p[i + 1], p[i + 2] || p[i + 1]]
    d += ` C${(p1[0] + (p2[0] - p0[0]) / 6).toFixed(1)} ${(p1[1] + (p2[1] - p0[1]) / 6).toFixed(1)} ${(p2[0] - (p3[0] - p1[0]) / 6).toFixed(1)} ${(p2[1] - (p3[1] - p1[1]) / 6).toFixed(1)} ${p2[0]} ${p2[1]}`
  }
  return d
}

// The Great Silk Road through Uzbekistan: the main line west from Tashkent, a branch through the Fergana Valley and one south to Termez.
const MAIN = curve(['tashkent', 'samarkand', 'bukhara', 'urgench', 'khiva'])
const BRANCHES = [curve(['tashkent', 'kokand', 'fergana']), curve(['samarkand', 'shahrisabz', 'termez'])]

// [city key, English name, destination page, label position, big marker]
const STOPS = [
  ['tashkent', 'Tashkent', 'tashkent', 'above', true], ['samarkand', 'Samarkand', 'samarkand', 'right', true], ['bukhara', 'Bukhara', 'bukhara', 'above', true],
  ['khiva', 'Khiva', 'khorezm', 'below', true], ['fergana', 'Fergana', 'fergana', 'below', true], ['shahrisabz', 'Shahrisabz', 'kashkadarya', 'left', false],
  ['termez', 'Termez', null, 'right', false], ['nukus', 'Nukus', 'karakalpakstan', 'above', false],
]

export default function SilkRoadMap() {
  const t = useT()
  return (
    <section className="bg-sand-soft/60 py-20 lg:py-28">
      <div className="shell">
        <p className="eyebrow">{t('The Great Silk Road')}</p>
        <h2 className="display-lg mt-3 max-w-2xl">{t('Follow the caravan route across Uzbekistan')}</h2>
        <p className="mt-4 max-w-xl text-[15px] leading-relaxed text-ink">{t('For two thousand years caravans carried silk, spices and ideas through these oasis cities. Our journeys follow the same road.')}</p>
        <Reveal className="mt-10 overflow-hidden rounded-[4px] border border-navy/10 bg-card p-3 sm:p-6">
          <svg viewBox="0 0 1040 687" role="img" aria-label={t('Map of Uzbekistan with the Great Silk Road route')} className="mx-auto block h-auto w-full max-w-4xl">
            <path d={OUTLINE} className="fill-sand-soft stroke-navy/40" strokeWidth="2" strokeLinejoin="round" />
            {BRANCHES.map((d) => <path key={d} d={d} fill="none" className="stroke-gold" strokeWidth="4" strokeLinecap="round" strokeDasharray="2 10" />)}
            <path d={MAIN} fill="none" className="stroke-gold" strokeWidth="10" strokeLinecap="round" opacity="0.3" />
            <path d={MAIN} fill="none" className="silk-flow stroke-navy" strokeWidth="4" strokeLinecap="round" strokeDasharray="14 10" />
            {STOPS.map(([key, name, slug, side, big]) => {
              const [x, y] = CITY[key]
              const marker = (<>
                <circle cx={x} cy={y} r={big ? 13 : 9} className="fill-ivory stroke-navy" strokeWidth="3" />
                <circle cx={x} cy={y} r={big ? 5 : 3.5} className="fill-gold" />
                <text x={side === 'right' ? x + 22 : side === 'left' ? x - 22 : x} y={side === 'above' ? y - 26 : side === 'below' ? y + 46 : y + 12} textAnchor={side === 'right' ? 'start' : side === 'left' ? 'end' : 'middle'}
                  className="fill-navy font-heading" stroke="#fff" strokeWidth="8" strokeLinejoin="round" style={{ fontSize: 40, paintOrder: 'stroke' }}>{t(name)}</text>
              </>)
              return slug
                ? <Link key={key} to={`/destinations/${slug}`} aria-label={t(name)} className="outline-none"><g className="cursor-pointer">{marker}</g></Link>
                : <g key={key}>{marker}</g>
            })}
          </svg>
          <ul className="mt-4 flex flex-wrap items-center justify-center gap-x-8 gap-y-2 text-[12.5px] text-ink">
            <li className="flex items-center gap-2"><span className="inline-block h-[3px] w-8 bg-navy" />{t('Main Silk Road')}</li>
            <li className="flex items-center gap-2"><span className="inline-block w-8 border-t-[3px] border-dotted border-gold" />{t('Branches: Fergana Valley and the south')}</li>
          </ul>
        </Reveal>
      </div>
    </section>
  )
}
