import { useEffect, useState } from 'react'
import { api } from './api'

// Group pricing: the listed price is for the biggest group of the table (14 or more), smaller groups pay more per person.
// The tiers are edited in Admin → Group pricing and arrive with the site settings. Percentages of the listed price; for the
// 2-day Samarkand tour ($209) they give exactly $209, $249, $267, $289 and $294.
export const DEFAULT_TIERS = [
  { min: 14, percent: 100 }, { min: 11, percent: 119.138756 }, { min: 7, percent: 127.751196 },
  { min: 3, percent: 138.277512 }, { min: 1, percent: 140.669856 },
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

/** The group size the listed price is for (the first row of the table, e.g. 14). */
export const biggestGroup = (tiers) => sortedTiers(tiers)[0].min

// one request for the whole page: every tour card needs the table, the site settings are fetched only once
let shared = null
let loading = null
export function useGroupTiers() {
  const [tiers, setTiers] = useState(shared)
  useEffect(() => {
    if (shared) return undefined
    let alive = true
    loading ||= api.get('/site-content/').then((d) => { shared = d?.group_pricing_tiers?.length ? d.group_pricing_tiers : DEFAULT_TIERS; return shared }).catch(() => DEFAULT_TIERS)
    loading.then((x) => { if (alive) setTiers(x) })
    return () => { alive = false }
  }, [])
  return tiers || DEFAULT_TIERS
}
