/**
 * The ALI TRAVEL mark: a golden "A" over a globe, the flight path of a plane and the domes of the Silk Road, on dark blue
 * (the owner's own design, frontend/public/logo-*.png; the browser-tab icon in index.html is the same picture).
 * The picture has white corners outside its rounded square, so it is shown clipped to that rounded square.
 */
export default function LogoMark({ className = 'h-10 w-10' }) {
  return (
    <img src="/logo-96.png" srcSet="/logo-96.png 96w, /logo-192.png 192w" sizes="48px" alt="" aria-hidden="true" width="96" height="96"
      decoding="async" className={`${className} rounded-[22%] object-cover`} />
  )
}
