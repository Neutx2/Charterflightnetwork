import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * Shared frontmatter for every migrated legacy page.
 * `legacyUrl` is the old .htm/.html path (used to build the 301 redirect map);
 * `slug` is the new clean URL path.
 */
const migratedPage = z.object({
  title: z.string(),
  description: z.string(),
  h1: z.string().optional(),
  region: z.enum(['canada', 'usa', 'bahamas', 'caribbean', 'global']).optional(),
  province: z.string().optional(),
  provinceSlug: z.string().optional(),
  city: z.string().optional(),
  airportCode: z.string().optional(),
  legacyUrl: z.string(),
  slug: z.string(),
  thin: z.boolean().default(false),
  /** subject line for the quote form on this page (legacy hidden field) */
  quoteSubject: z.string().optional(),
});

const destinations = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/destinations' }),
  schema: migratedPage,
});

const hubs = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/hubs' }),
  schema: migratedPage,
});

const aircraft = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/aircraft' }),
  schema: migratedPage,
});

const directory = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/directory' }),
  schema: migratedPage,
});

const pages = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/pages' }),
  schema: migratedPage,
});

export const collections = { destinations, hubs, aircraft, directory, pages };
