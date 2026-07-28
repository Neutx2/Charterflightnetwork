/**
 * Static JSON for the directory operator finder (built at compile time,
 * fetched lazily by the finder UI so the directory page itself stays light).
 *
 * Source of truth is src/data/operators.json (826 listings parsed from the
 * migrated directory pages by scripts/build_operator_data.py). Listings are
 * deduplicated by name+base — many operators appear on several directory
 * pages — keeping the featured variant when one exists. Every field ships
 * exactly as it appears on the source pages; nothing is invented here.
 */
import type { APIRoute } from 'astro';
import operators from '../../data/operators.json';
import { provinceForDirectoryPage } from '../../lib/directory-provinces';

type Op = (typeof operators)[number];

/** Normalized service facets from the free-text serviceType strings. */
function facets(serviceType: string | null): string[] {
  const s = (serviceType ?? '').toLowerCase();
  const out: string[] = [];
  if (s.includes('float') || s.includes('amphib')) out.push('Floats');
  if (s.includes('wheel')) out.push('Wheels');
  if (s.includes('helicopter')) out.push('Helicopter');
  if (s.includes('ski')) out.push('Skis');
  return out;
}

// Merge duplicate listings (same operator on several directory pages) by
// unioning fields: any duplicate's phone/aircraft/details fills a gap in the
// kept record, and featured wins for the flag and the linked page. Keeping a
// single arbitrary duplicate lost 56 phone numbers.
const byKey = new Map<string, Op[]>();
for (const o of operators as Op[]) {
  const key = `${o.name}|${o.baseLocations}`;
  byKey.set(key, [...(byKey.get(key) ?? []), o]);
}

const rows = [...byKey.values()]
  .map((dupes) => {
    const primary = dupes.find((o) => o.featured) ?? dupes[0]!;
    const first = <T>(pick: (o: Op) => T | null | undefined): T | null => {
      for (const o of [primary, ...dupes]) {
        const v = pick(o);
        if (v != null && (typeof v !== 'string' || v.length)) return v;
      }
      return null;
    };
    const phone = first((o) => o.phones[0]);
    const serviceType = first((o) => o.serviceType);
    return {
      n: primary.name,
      b: first((o) => o.baseLocations),
      s: serviceType,
      sf: facets(serviceType),
      a: first((o) => o.aircraftTypes),
      p: phone?.display ?? null,
      t: phone?.tel ?? null,
      d: primary.directoryPage,
      prov: provinceForDirectoryPage(primary.directoryPage),
      f: dupes.some((o) => o.featured),
    };
  })
  .sort((a, b) => Number(b.f) - Number(a.f) || a.n.localeCompare(b.n));

export const GET: APIRoute = () =>
  new Response(JSON.stringify({ generated: 'build', count: rows.length, operators: rows }), {
    headers: { 'Content-Type': 'application/json' },
  });
