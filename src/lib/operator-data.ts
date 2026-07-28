/**
 * Merged, deduplicated operator records — the single source both the finder
 * endpoint (/data/operator-finder.json) and the per-destination operator
 * modules consume, so the two can never disagree.
 *
 * Raw source is src/data/operators.json (826 listings parsed from the
 * migrated directory pages). Operators appear on several directory pages;
 * records are merged by name+base, unioning fields (any duplicate's phone or
 * aircraft list fills a gap) with featured winning the flag and the linked
 * page. Nothing here is invented — every field ships as it appears on the
 * source pages.
 */
import operators from '../data/operators.json';
import { provinceForDirectoryPage } from './directory-provinces';

type Raw = (typeof operators)[number];

export type MergedOperator = {
  name: string;
  base: string | null;
  serviceType: string | null;
  serviceFacets: string[];
  aircraft: string | null;
  phoneDisplay: string | null;
  phoneTel: string | null;
  directoryPage: string;
  province: string;
  featured: boolean;
  /** lower-cased place tokens from the base string, for city matching */
  baseTokens: string[];
};

/** Normalized service facets from the free-text serviceType strings. */
export function serviceFacets(serviceType: string | null): string[] {
  const s = (serviceType ?? '').toLowerCase();
  const out: string[] = [];
  if (s.includes('float') || s.includes('amphib')) out.push('Floats');
  if (s.includes('wheel')) out.push('Wheels');
  if (s.includes('helicopter')) out.push('Helicopter');
  if (s.includes('ski')) out.push('Skis');
  return out;
}

function tokens(base: string | null): string[] {
  if (!base) return [];
  return base
    .split(/[\/,;()]| and /i)
    // periods vary between listings of the same operator ("Fort St. John" /
    // "Fort St John") — normalize them away so token matching is stable
    .map((t) => t.replace(/\./g, '').trim().toLowerCase())
    // drop bare province codes and empties; keep place names
    .filter((t) => t.length > 2 && !/^[a-z]{2}$/.test(t));
}

function build(): MergedOperator[] {
  // Key by normalized NAME alone: the same operator appears across directory
  // pages with differently-punctuated base strings ("Thunder Bay / Armstrong"
  // vs "Thunder Bay, Armstrong"), which a name+base key treats as two
  // companies. Verified against the dataset: of 43 same-name groups, every
  // base difference is formatting/punctuation, none are distinct businesses.
  const byKey = new Map<string, Raw[]>();
  for (const o of operators as Raw[]) {
    const key = o.name.replace(/\./g, '').replace(/\s+/g, ' ').trim().toLowerCase();
    byKey.set(key, [...(byKey.get(key) ?? []), o]);
  }
  return [...byKey.values()]
    .map((dupes) => {
      const primary = dupes.find((o) => o.featured) ?? dupes[0]!;
      const first = <T>(pick: (o: Raw) => T | null | undefined): T | null => {
        for (const o of [primary, ...dupes]) {
          const v = pick(o);
          if (v != null && (typeof v !== 'string' || v.length)) return v;
        }
        return null;
      };
      const phone = first((o) => o.phones[0]);
      const serviceType = first((o) => o.serviceType);
      // prefer the longest base string (most complete listing of bases)
      const base =
        dupes
          .map((o) => o.baseLocations)
          .filter((b): b is string => !!b)
          .sort((a, b) => b.length - a.length)[0] ?? null;
      return {
        name: primary.name,
        base,
        serviceType,
        serviceFacets: serviceFacets(serviceType),
        aircraft: first((o) => o.aircraftTypes),
        phoneDisplay: phone?.display ?? null,
        phoneTel: phone?.tel ?? null,
        directoryPage: primary.directoryPage,
        province: provinceForDirectoryPage(primary.directoryPage),
        featured: dupes.some((o) => o.featured),
        baseTokens: [...new Set(dupes.flatMap((o) => tokens(o.baseLocations)))],
      };
    })
    .sort((a, b) => Number(b.featured) - Number(a.featured) || a.name.localeCompare(b.name));
}

export const MERGED_OPERATORS: MergedOperator[] = build();

/**
 * Operators for a destination page: those whose base includes the city
 * (strongest signal — genuinely local), topped up with featured-first
 * operators from the same province group.
 */
export function operatorsForCity(
  city: string | undefined,
  provinceLabel: string | undefined,
  limit = 6
): { local: MergedOperator[]; regional: MergedOperator[]; provinceTotal: number } {
  const c = (city ?? '').trim().toLowerCase();
  const inProvince = provinceLabel
    ? MERGED_OPERATORS.filter((o) => o.province === provinceLabel)
    : [];
  const local = c ? inProvince.filter((o) => o.baseTokens.includes(c)) : [];
  const regional = inProvince.filter((o) => !local.includes(o)).slice(0, Math.max(0, limit - local.length));
  return { local: local.slice(0, limit), regional, provinceTotal: inProvince.length };
}
