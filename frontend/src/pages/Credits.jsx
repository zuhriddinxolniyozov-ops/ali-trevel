import { useMemo } from 'react'
import { useFetch } from '../hooks'
import { useT } from '../i18n'
import Seo from '../components/Seo'
import { PageHero } from '../components/ui'
import { IMAGES } from '../data'

const COMMONS = 'commons.wikimedia.org/wiki/Special:FilePath/'

/** The file name inside a Wikimedia Commons image link, or null for any other kind of image. */
function commonsFile(url = '') {
  const at = url.indexOf(COMMONS)
  if (at < 0) return null
  try { return decodeURIComponent(url.slice(at + COMMONS.length).split('?')[0]).replace(/_/g, ' ') } catch { return null }
}

export default function Credits() {
  const t = useT()
  const tours = useFetch('/tours/', { list: true })
  const places = useFetch('/destinations/', { list: true })
  const credits = useMemo(() => {
    const seen = new Map()
    ;[...places.data.map((d) => [d.name, d.image_url]), ...tours.data.map((x) => [x.title, x.image_url])].forEach(([name, url]) => {
      const file = commonsFile(url)
      if (file && !seen.has(file)) seen.set(file, name)
    })
    return [...seen].map(([file, name]) => ({ file, name }))
  }, [tours.data, places.data])
  return (
    <>
      <Seo title={t('Photo credits')} description={t('Where the photographs on this website come from.')} />
      <PageHero eyebrow="Legal" title="Photo credits" description="Where the photographs on this website come from." image={IMAGES.hotel} />
      <div className="shell max-w-3xl py-16 lg:py-24">
        <p className="text-[16px] leading-relaxed text-ink">{t('Many photographs of historical places on this website are shared on Wikimedia Commons under open licences such as Creative Commons. Each photograph below links to its Commons page, which names the photographer and the licence. Some other pictures on the website are illustrations made for ALI TRAVEL.')}</p>
        <ul className="mt-8 divide-y divide-navy/10 rounded-sm border border-navy/10 bg-white">
          {credits.map((c) => (
            <li key={c.file} className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 px-4 py-3 text-[14px]">
              <span className="font-medium text-navy">{c.name}</span>
              <a href={`https://commons.wikimedia.org/wiki/File:${encodeURIComponent(c.file.replace(/ /g, '_')).replace(/%2C/g, ',').replace(/%28/g, '(').replace(/%29/g, ')')}`} target="_blank" rel="noopener noreferrer"
                className="break-all text-turquoise-deep underline underline-offset-2 hover:text-navy">{c.file}</a>
            </li>
          ))}
        </ul>
      </div>
    </>
  )
}
