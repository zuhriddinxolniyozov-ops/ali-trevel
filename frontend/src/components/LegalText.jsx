import { Fragment } from 'react'

/**
 * Tiny markup used by the legal pages (editable in Admin → Legal pages):
 *   ## Heading        ### Sub-heading        - bullet        1. numbered step
 *   **bold**          [link text](https://example.com)       blank line / new line = new paragraph
 */
export function parseLegal(body = '') {
  const blocks = []
  let list = null
  for (const raw of String(body).split('\n')) {
    const line = raw.trim()
    if (!line) { list = null; continue }
    let m
    if ((m = line.match(/^#\s+(.*)/))) { blocks.push({ type: 'h1', text: m[1] }); list = null }
    else if ((m = line.match(/^###\s+(.*)/))) { blocks.push({ type: 'h3', text: m[1] }); list = null }
    else if ((m = line.match(/^##\s+(.*)/))) { blocks.push({ type: 'h2', text: m[1] }); list = null }
    else if ((m = line.match(/^[-*]\s+(.*)/))) {
      if (!list || list.type !== 'ul') { list = { type: 'ul', items: [] }; blocks.push(list) }
      list.items.push(m[1])
    } else if ((m = line.match(/^\d+[.)]\s+(.*)/))) {
      if (!list || list.type !== 'ol') { list = { type: 'ol', items: [] }; blocks.push(list) }
      list.items.push(m[1])
    } else { blocks.push({ type: 'p', text: line }); list = null }
  }
  return blocks
}

const safeUrl = (u) => (/^(https?:|mailto:|tel:|\/)/i.test(u) ? u : '#')

function Inline({ text }) {
  return text.split(/(\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))/g).map((part, i) => {
    const bold = part.match(/^\*\*([^*]+)\*\*$/)
    if (bold) return <strong key={i} className="font-semibold text-navy">{bold[1]}</strong>
    const link = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/)
    if (link) return <a key={i} href={safeUrl(link[2])} className="text-turquoise-deep underline underline-offset-2 hover:text-navy">{link[1]}</a>
    return <Fragment key={i}>{part}</Fragment>
  })
}

export const headingId = (index) => `section-${index}`

export default function LegalText({ body }) {
  let h = -1
  return (
    <div className="legal-text">
      {parseLegal(body).map((b, i) => {
        if (b.type === 'h2') { h += 1; return <h2 key={i} id={headingId(h)} className="mt-12 scroll-mt-28 border-t border-navy/10 pt-8 font-heading text-[28px] first:mt-0 first:border-0 first:pt-0"><Inline text={b.text} /></h2> }
        if (b.type === 'h1') return <h1 key={i} className="mt-4 text-center font-heading text-[28px]"><Inline text={b.text} /></h1>
        if (b.type === 'h3') return <h3 key={i} className="mt-6 font-heading text-[21px]"><Inline text={b.text} /></h3>
        if (b.type === 'ul') return <ul key={i} className="mt-3 list-disc space-y-1.5 pl-6 text-[16px] leading-relaxed text-ink marker:text-turquoise-deep">{b.items.map((it, j) => <li key={j}><Inline text={it} /></li>)}</ul>
        if (b.type === 'ol') return <ol key={i} className="mt-3 list-decimal space-y-1.5 pl-6 text-[16px] leading-relaxed text-ink marker:font-medium marker:text-navy">{b.items.map((it, j) => <li key={j}><Inline text={it} /></li>)}</ol>
        return <p key={i} className="mt-3 text-[16px] leading-relaxed text-ink"><Inline text={b.text} /></p>
      })}
    </div>
  )
}
