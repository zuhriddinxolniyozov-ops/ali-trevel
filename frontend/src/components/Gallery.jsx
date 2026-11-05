import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useT } from '../i18n'
import { Photo } from './ui'

/**
 * A photo slider. Swipe on a phone, drag with the mouse, use the arrows, the dots, the thumbnails or the arrow keys:
 * the first photo slides out to the left and the next one slides in.
 *   images  list of photo links (the cover first)
 *   to      optional link: a click on a photo (not a drag) opens it
 *   thumbs  show a row of small previews under the slider
 *   arrows  'hover' (visible on hover, always on phones) or 'always'
 *   dots    show the dots under the photo (off where a caption sits there)
 */
export default function Gallery({ images = [], alt = '', className = 'aspect-[4/3]', to, thumbs = false, arrows = 'hover', rounded = '', dots = true }) {
  const t = useT()
  const list = images.filter(Boolean)
  const box = useRef(null)
  const drag = useRef(null)
  const [index, setIndex] = useState(0)
  const [dragging, setDragging] = useState(false)

  const width = () => box.current?.clientWidth || 1
  const go = useCallback((i) => {
    const next = Math.max(0, Math.min(list.length - 1, i))
    box.current?.scrollTo({ left: next * width(), behavior: 'smooth' })
    setIndex(next)
  }, [list.length])

  // keep the dots and thumbnails in step when the visitor swipes
  useEffect(() => {
    const el = box.current
    if (!el) return undefined
    let frame = 0
    const onScroll = () => {
      cancelAnimationFrame(frame)
      frame = requestAnimationFrame(() => setIndex(Math.round(el.scrollLeft / width())))
    }
    el.addEventListener('scroll', onScroll, { passive: true })
    return () => { el.removeEventListener('scroll', onScroll); cancelAnimationFrame(frame) }
  }, [list.length])

  const clickBlocked = useRef(false)
  const onPointerDown = (e) => {
    if (e.pointerType !== 'mouse' || e.button !== 0 || list.length < 2) return
    clickBlocked.current = false
    drag.current = { x: e.clientX, left: box.current.scrollLeft, moved: false }
  }
  const onPointerMove = (e) => {
    const d = drag.current
    if (!d) return
    const dx = e.clientX - d.x
    // the slider holds the mouse only once it really drags: a plain click must still reach the photo's link
    if (Math.abs(dx) > 5 && !d.moved) {
      d.moved = true
      setDragging(true)
      try { box.current.setPointerCapture(e.pointerId) } catch { /* the drag still works without capture */ }
    }
    if (!d.moved) return
    box.current.scrollLeft = d.left - dx
  }
  const onPointerUp = (e) => {
    const d = drag.current
    if (!d) return
    drag.current = null
    setDragging(false)
    try { box.current.releasePointerCapture(e.pointerId) } catch { /* pointer already released */ }
    clickBlocked.current = d.moved  // a drag must not count as a click on the photo's link
    const dx = e.clientX - d.x
    const nearest = Math.round((d.left - dx) / width())
    // a short quick drag still turns the page
    go(nearest === index && dx < -40 ? index + 1 : nearest === index && dx > 40 ? index - 1 : nearest)
  }
  const stopClickAfterDrag = (e) => { if (clickBlocked.current) { e.preventDefault(); e.stopPropagation(); clickBlocked.current = false } }
  const onKeyDown = (e) => {
    if (e.key === 'ArrowRight') { e.preventDefault(); go(index + 1) }
    if (e.key === 'ArrowLeft') { e.preventDefault(); go(index - 1) }
  }

  if (!list.length) return <Photo src="" className={`${className} w-full ${rounded}`} />
  const single = list.length < 2
  const arrowTone = arrows === 'always' ? 'opacity-100' : 'opacity-100 md:opacity-0 md:group-hover/gallery:opacity-100 md:focus-visible:opacity-100'
  const button = 'absolute top-1/2 z-10 grid h-9 w-9 -translate-y-1/2 place-items-center rounded-full bg-ivory/90 text-navy shadow-md transition hover:bg-white disabled:hidden'

  return (
    <div className="min-w-0 max-w-full">
      <div className={`group/gallery relative overflow-hidden ${rounded}`}>
        <div ref={box} tabIndex={single ? -1 : 0} onKeyDown={onKeyDown} onPointerDown={onPointerDown} onPointerMove={onPointerMove} onPointerUp={onPointerUp} onPointerCancel={onPointerUp}
          onClickCapture={stopClickAfterDrag} role="group" aria-roledescription="carousel" aria-label={alt}
          className={`flex w-full overflow-x-auto scroll-smooth [scrollbar-width:none] [&::-webkit-scrollbar]:hidden ${dragging ? 'cursor-grabbing snap-none !scroll-auto' : `${single ? '' : 'cursor-grab'} snap-x snap-mandatory`} ${className}`}>
          {list.map((src, i) => {
            const image = <Photo src={src} sizes="(max-width: 1023px) 100vw, 62vw" alt={`${alt} ${i + 1}/${list.length}`} draggable={false} loading={i === 0 ? 'eager' : 'lazy'} className="h-full w-full select-none object-cover" />
            return (
              <div key={`${src}-${i}`} role="group" aria-roledescription="slide" aria-label={`${i + 1} / ${list.length}`} className="h-full w-full shrink-0 snap-center">
                {to ? <Link to={to} draggable={false} tabIndex={-1} className="block h-full w-full">{image}</Link> : image}
              </div>
            )
          })}
        </div>
        {!single && (
          <>
            <button type="button" aria-label={t('Previous photo')} disabled={index === 0} onClick={() => go(index - 1)} className={`${button} left-3 ${arrowTone}`}><ChevronLeft className="h-5 w-5" /></button>
            <button type="button" aria-label={t('Next photo')} disabled={index === list.length - 1} onClick={() => go(index + 1)} className={`${button} right-3 ${arrowTone}`}><ChevronRight className="h-5 w-5" /></button>
            {dots && <div className="pointer-events-none absolute inset-x-0 bottom-3 z-10 flex justify-center gap-1.5">
              {list.map((_, i) => <span key={i} className={`h-1.5 rounded-full transition-all ${i === index ? 'w-4 bg-ivory' : 'w-1.5 bg-ivory/60'}`} />)}
            </div>}
            <span className="pointer-events-none absolute right-3 top-3 z-10 rounded-full bg-navy/60 px-2.5 py-1 font-mono text-[10px] text-ivory">{index + 1} / {list.length}</span>
          </>
        )}
      </div>
      {thumbs && !single && (
        <div className="mt-3 flex gap-2 overflow-x-auto pb-1" role="tablist" aria-label={t('Photos')}>
          {list.map((src, i) => (
            <button key={`${src}-${i}`} type="button" role="tab" aria-selected={i === index} aria-label={`${i + 1} / ${list.length}`} onClick={() => go(i)}
              className={`h-16 w-24 shrink-0 overflow-hidden rounded-sm border-2 transition ${i === index ? 'border-navy' : 'border-transparent opacity-70 hover:opacity-100'}`}>
              <Photo src={src} sizes="160px" alt="" className="h-full w-full object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
