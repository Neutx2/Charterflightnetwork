/**
 * Static JSON for the directory operator finder (built at compile time,
 * fetched lazily by the finder UI so the directory page itself stays light).
 *
 * Records come from src/lib/operator-data.ts — the same merged, deduplicated
 * dataset the per-destination operator modules render — serialized with
 * short keys to keep the payload small.
 */
import type { APIRoute } from 'astro';
import { MERGED_OPERATORS } from '../../lib/operator-data';

const rows = MERGED_OPERATORS.map((o) => ({
  n: o.name,
  b: o.base,
  s: o.serviceType,
  sf: o.serviceFacets,
  a: o.aircraft,
  p: o.phoneDisplay,
  t: o.phoneTel,
  d: o.directoryPage,
  prov: o.province,
  f: o.featured,
}));

export const GET: APIRoute = () =>
  new Response(JSON.stringify({ generated: 'build', count: rows.length, operators: rows }), {
    headers: { 'Content-Type': 'application/json' },
  });
