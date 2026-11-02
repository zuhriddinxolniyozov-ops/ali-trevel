// Group pricing: the listed price is for 20 or more travelers, smaller groups pay more per person.
// The tiers are edited in Admin → Group pricing and arrive with the site settings.
export const DEFAULT_TIERS = [
  { min: 20, percent: 100 }, { min: 15, percent: 105 }, { min: 10, percent: 115 }, { min: 6, percent: 130 },
  { min: 4, percent: 150 }, { min: 2, percent: 180 }, { min: 1, percent: 220 },
]

export const sortedTiers = (tiers) => [...(Array.isArray(tiers) && tiers.length ? tiers : DEFAULT_TIERS)].sort((a, b) => b.min - a.min)

/** Percentage of the listed price that one traveler pays in a group of `guests`. */
export function groupPercent(tiers, guests) {
  const n = Math.max(1, Number(guests) || 1)
  const list = sortedTiers(tiers)
  return (list.find((x) => n >= x.min) || list[list.length - 1]).percent
}

/** [{min, max, percent}] from the biggest group down; `max` is null for the first (open-ended) row. */
export function tierRanges(tiers) {
  const list = sortedTiers(tiers)
  return list.map((x, i) => ({ min: x.min, max: i === 0 ? null : list[i - 1].min - 1, percent: x.percent }))
}

/** Tours with a price follow group pricing unless an admin switched it off (classes and workshops, for example). */
export const usesGroupPricing = (tour) => tour?.group_pricing !== false && Number(tour?.price_from_usd) > 0
