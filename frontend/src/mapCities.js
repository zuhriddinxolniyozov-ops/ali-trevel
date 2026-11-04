// The cities of the Silk Road map on the home page.
// [key, English name, destination page, label position, big marker, drawn even when not green]
export const CITIES = [
  ['tashkent', 'Tashkent', 'tashkent', 'above', true, true], ['samarkand', 'Samarkand', 'samarkand', 'right', true, true], ['bukhara', 'Bukhara', 'bukhara', 'above', true, true],
  ['khiva', 'Khiva', 'khorezm', 'below', true, true], ['fergana', 'Fergana', 'fergana', 'below', true, true], ['shahrisabz', 'Shahrisabz', 'kashkadarya', 'left', false, true],
  ['termez', 'Termez', null, 'right', false, true], ['nukus', 'Nukus', 'karakalpakstan', 'above', false, true],
  // more cities the owner can switch on in Settings: they appear on the map once marked green
  ['qarshi', 'Qarshi', 'kashkadarya', 'below', false, false], ['navoi', 'Navoi', null, 'above', false, false], ['jizzakh', 'Jizzakh', null, 'above', false, false],
  ['kokand', 'Kokand', 'fergana', 'above', false, false], ['namangan', 'Namangan', 'fergana', 'above', false, false], ['andijan', 'Andijan', 'fergana', 'right', false, false],
  ['urgench', 'Urgench', 'khorezm', 'above', false, false],
]

/** What the owner chose in Settings (green or not, and where a click leads) for each city. */
export function mapState(settings) {
  const chosen = settings?.map_cities || {}
  return (key) => chosen[key] || { green: false, target: '' }
}

/** The page a city leads to: the chosen tour, else the tours of the city (green) or the city page. */
export function cityLink(key, slug, state) {
  const { green, target } = state(key)
  if (green) return target || (slug ? `/destinations/${slug}#tours` : null)
  return slug ? `/destinations/${slug}` : null
}
