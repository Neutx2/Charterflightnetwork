/**
 * Province/region grouping for directory page slugs, keyed by slug prefix.
 * Shared by the directory index (section headings) and the operator-finder
 * JSON endpoint (per-operator province facet), so the two can never drift.
 */
export const DIRECTORY_GROUPS: [string, string[]][] = [
  ['Alberta', ['alberta-']],
  ['British Columbia', ['bc-', 'british-columbia-']],
  ['Manitoba', ['manitoba-']],
  ['New Brunswick', ['new-brunswick-']],
  ['Newfoundland & Labrador', ['newfoundland-']],
  ['Northwest Territories', ['nwt-', 'northwest-territories-']],
  ['Nova Scotia', ['nova-scotia-']],
  ['Nunavut', ['nunavut-']],
  ['Ontario', ['ontario-', 'northern-ontario-']],
  ['Quebec', ['quebec-']],
  ['Saskatchewan', ['saskatchewan-']],
  ['Yukon', ['yukon-']],
  ['Canada-wide & USA-licensed', ['canadian-', 'usa-']],
];

/** Destination-page provinceSlug → finder/group label (Ontario spans two hubs). */
export const SLUG_TO_PROVINCE_LABEL: Record<string, string> = {
  alberta: 'Alberta',
  'british-columbia': 'British Columbia',
  manitoba: 'Manitoba',
  'new-brunswick': 'New Brunswick',
  newfoundland: 'Newfoundland & Labrador',
  labrador: 'Newfoundland & Labrador',
  'northwest-territories': 'Northwest Territories',
  'nova-scotia': 'Nova Scotia',
  nunavut: 'Nunavut',
  'northern-ontario': 'Ontario',
  'southern-ontario': 'Ontario',
  quebec: 'Quebec',
  saskatchewan: 'Saskatchewan',
  yukon: 'Yukon',
};

/** Province/region label for a directory page path like "/directory/bc-…". */
export function provinceForDirectoryPage(path: string): string {
  const base = path.replace(/^\/?directory\//, '');
  for (const [label, prefixes] of DIRECTORY_GROUPS) {
    if (prefixes.some((p) => base.startsWith(p))) return label;
  }
  return 'Other';
}
