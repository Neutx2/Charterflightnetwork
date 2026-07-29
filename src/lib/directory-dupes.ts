/**
 * Legacy directory pages that serve byte-identical content at two URLs.
 *
 * Found by hashing the <main> of every built /directory/* page: seven pairs
 * come through the migration as exact duplicates, because the legacy site
 * published the same document under two names. Left alone this costs twice:
 *
 *   · Google sees seven pairs of duplicate pages competing with each other.
 *   · The directory index listed both copies, so readers saw two
 *     identical-looking links — e.g. "New Brunswick Air Charter Directory"
 *     twice — one of which went somewhere they did not expect.
 *
 * The fix is canonicalisation, not deletion: every URL stays live and keeps
 * answering (the 301 map and any external inbound links still resolve), but
 * the duplicate points its canonical at the primary and is dropped from the
 * index listing and the sitemap.
 *
 * Primary is chosen as the slug whose own <h1> matches it. e.g. the page at
 * /directory/northern-ontario-float-plane-1 is titled "Ontario Air Charter
 * Directory – Page 1", so /directory/ontario-air-charter-directory-1 is the
 * primary and the float-plane slug is the duplicate.
 *
 * Regenerate this list with: python3 scripts/find_duplicate_pages.py
 */
export const DIRECTORY_DUPLICATES: Record<string, string> = {
  'directory/nova-scotia-helicopter-directory': 'directory/canadian-helicopter-air-charter-directory',
  'directory/new-brunswick-usa-air-charter-directory': 'directory/new-brunswick-air-charter-directory',
  'directory/northern-ontario-float-plane-1': 'directory/ontario-air-charter-directory-1',
  'directory/northern-ontario-float-plane-3': 'directory/ontario-air-charter-directory-3',
  'directory/northern-ontario-float-plane-4': 'directory/ontario-air-charter-directory-4',
  'directory/northern-ontario-float-plane-5': 'directory/ontario-air-charter-directory-5',
  'directory/northern-ontario-float-plane-6': 'directory/ontario-air-charter-directory-6',
  // Near-identical rather than byte-identical: same navigational menu with two
  // sections reordered. Both carry the <h1> "Canadian Air Charter Directory",
  // so the index showed that label twice. The -1 page is the superset — it
  // additionally explains how to submit a free listing — so it is the primary.
  'directory/canadian-air-charter-directory-contact': 'directory/canadian-air-charter-directory-1',
};

/** Canonical slug for a directory page — itself, unless it's a known duplicate. */
export const canonicalSlug = (slug: string): string =>
  DIRECTORY_DUPLICATES[slug] ?? slug;

export const isDuplicate = (slug: string): boolean => slug in DIRECTORY_DUPLICATES;

/** URL paths of the duplicate copies, for the sitemap filter. */
export const DUPLICATE_PATHS = Object.keys(DIRECTORY_DUPLICATES).map((s) => `/${s}/`);
