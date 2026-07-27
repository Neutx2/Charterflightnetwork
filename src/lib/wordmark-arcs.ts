/**
 * The eight logotype variants offered for selection.
 *
 * All are the same family — the classic orange swoosh with an aircraft at its
 * tip, over the closed-up two-tone wordmark — differing in the arc's shape,
 * the aircraft's size and attitude, and whether the dashed contrail is drawn.
 * Switching the site's logotype means changing DEFAULT_VARIANT below; nothing
 * else moves.
 *
 * Geometry is authored in the variant's own viewBox and positioned in `em`,
 * so every variant scales as one unit with font-size and needs no
 * per-breakpoint tuning.
 *
 * Colours are sampled from the classic artwork, not chosen:
 * src/assets/legacy/Logo_green_white.jpg — #ff7d02.
 */
export type WordmarkVariant = {
  /** shown to the owner when choosing */
  label: string;
  note: string;
  viewBox: string;
  /** inline styles placing the art relative to the wordmark, in em */
  place: string;
  /** true when the swoosh runs beneath the word rather than over it */
  under?: boolean;
  paths: string;
  /**
   * Type settings. Close reading of the 2008 artwork showed "Charterflight"
   * and "Network" are set in different typefaces at different weights — a
   * heavy rounded geometric against a lighter neutral grotesque. The colour
   * split is the obvious half of that contrast; the weight split is the half
   * that gives the classic its character. Variants that omit these fall back
   * to the older uniform-ExtraBold setting.
   */
  heavy?: number;
  light?: number;
  track?: string;
  /** space above the wordmark for art that sits over it */
  padTop?: string;
  /**
   * The art paints BEHIND the letterforms instead of over them. The artwork
   * SVG is absolutely positioned, so by default it paints above the type;
   * Wordmark.astro gives the type position:relative when this is set, which
   * places it later in the stacking context and lets the letters occlude the
   * art. That occlusion is what makes "aircraft behind the word" possible.
   */
  behind?: boolean;
};

const O = '#ff7d02';
/** heritage-400 from src/styles/global.css — recedes so the aircraft leads */
const TEAL = '#2d7b8c';
const PLANE =
  'M32 8c2.6 0 4.2 2.9 4.2 7.4v9.1l16.3 9.6c.9.5 1.5 1.5 1.5 2.6v4.1c0 .9-.9 1.6-1.8 1.3l-16-5.2v9.4l4.6 3.7c.5.4.8 1 .8 1.6v2.2c0 .8-.7 1.3-1.4 1.1L32 52.8l-8.2 1.1c-.7.2-1.4-.3-1.4-1.1v-2.2c0-.6.3-1.2.8-1.6l4.6-3.7v-9.4l-16 5.2c-.9.3-1.8-.4-1.8-1.3v-4.1c0-1.1.6-2.1 1.5-2.6l16.3-9.6v-9.1C27.8 10.9 29.4 8 32 8z';

const plane = (t: string) => `<g transform="${t} translate(-32 -32)" fill="${O}">
      <path d="${PLANE}" /></g>`;

export const WORDMARK_VARIANTS = {
  'classic-climb': {
    label: 'Classic climb',
    note: 'dashed contrail, aircraft banking at the tip',
    viewBox: '0 0 200 56',
    place: 'left:.02em;top:-.42em;height:1.7em;width:4.6em',
    paths: `
    <path d="M4 42C32 6 96 2 136 24" stroke="${O}" stroke-width="7.5" stroke-linecap="round" fill="none" />
    <path d="M16 46C42 18 96 14 132 32" stroke="${O}" stroke-width="4.5" stroke-linecap="round" stroke-dasharray="2 7" fill="none" />
    ${plane('translate(152 6) rotate(34) scale(.86)')}`,
  },
  'steep-climb': {
    label: 'Steeper climb',
    note: 'a harder angle of attack — more lift, more energy',
    viewBox: '0 0 200 56',
    place: 'left:.02em;top:-.52em;height:1.85em;width:4.5em',
    paths: `
    <path d="M4 48C30 20 88 8 128 8" stroke="${O}" stroke-width="7.5" stroke-linecap="round" fill="none" />
    <path d="M16 52C42 30 90 18 126 17" stroke="${O}" stroke-width="4.5" stroke-linecap="round" stroke-dasharray="2 7" fill="none" />
    ${plane('translate(146 -2) rotate(48) scale(.86)')}`,
  },
  'long-sweep': {
    label: 'Long sweep',
    note: 'the arc runs the full width of the word, aircraft clears "Network"',
    viewBox: '0 0 280 56',
    place: 'left:.02em;top:-.42em;height:1.7em;width:6.6em',
    paths: `
    <path d="M4 44C50 6 150 2 210 22" stroke="${O}" stroke-width="7" stroke-linecap="round" fill="none" />
    <path d="M18 48C62 20 148 14 206 30" stroke="${O}" stroke-width="4.2" stroke-linecap="round" stroke-dasharray="2 7" fill="none" />
    ${plane('translate(228 6) rotate(32) scale(.82)')}`,
  },
  'clean-arc': {
    label: 'Clean arc',
    note: 'no contrail — the quietest, sharpest version',
    viewBox: '0 0 200 56',
    place: 'left:.02em;top:-.42em;height:1.7em;width:4.6em',
    paths: `
    <path d="M4 42C32 6 96 2 136 24" stroke="${O}" stroke-width="8" stroke-linecap="round" fill="none" />
    ${plane('translate(152 6) rotate(34) scale(.86)')}`,
  },
  'big-aircraft': {
    label: 'Big aircraft',
    note: 'aircraft dominant, arc supporting — closest to the 2008 proportions',
    viewBox: '0 0 200 56',
    place: 'left:.02em;top:-.58em;height:2em;width:4.7em',
    paths: `
    <path d="M4 46C30 16 84 10 118 26" stroke="${O}" stroke-width="7" stroke-linecap="round" fill="none" />
    <path d="M16 50C42 26 84 22 114 34" stroke="${O}" stroke-width="4.2" stroke-linecap="round" stroke-dasharray="2 7" fill="none" />
    ${plane('translate(146 8) rotate(30) scale(1.15)')}`,
  },
  ribbon: {
    label: 'Ribbon',
    note: 'the swoosh tapers like a brush stroke instead of an even line',
    viewBox: '0 0 200 56',
    place: 'left:.02em;top:-.44em;height:1.75em;width:4.8em',
    paths: `
    <path d="M4 50C30 12 96 4 138 24 L136 30 C98 14 34 22 12 52 Z" fill="${O}" />
    ${plane('translate(154 6) rotate(34) scale(.88)')}`,
  },
  'level-flight': {
    label: 'Level flight',
    note: 'aircraft cruising rather than climbing — calmer, more corporate',
    viewBox: '0 0 200 56',
    place: 'left:.02em;top:-.4em;height:1.6em;width:4.8em',
    paths: `
    <path d="M4 38C36 16 100 12 138 20" stroke="${O}" stroke-width="7.5" stroke-linecap="round" fill="none" />
    <path d="M16 43C46 26 100 23 136 29" stroke="${O}" stroke-width="4.5" stroke-linecap="round" stroke-dasharray="2 7" fill="none" />
    ${plane('translate(156 12) rotate(10) scale(.88)')}`,
  },
  underline: {
    label: 'Underline',
    note: 'the swoosh runs beneath the word and lifts away past the end',
    viewBox: '0 0 460 56',
    place: 'left:.02em;top:.92em;height:1.2em;width:11.4em',
    under: true,
    paths: `
    <path d="M6 20C90 46 290 48 392 20" stroke="${O}" stroke-width="7" stroke-linecap="round" fill="none" />
    ${plane('translate(416 14) rotate(-34) scale(.8)')}`,
  },

  // ---------------------------------------------------------------------
  // A note on the aircraft's angle, because it is not a free choice:
  // the contrail is a cubic Bezier, and its direction where it ends is
  // P3 - P2 = (44, -18). The aircraft is drawn nose-up at rotate(0), so the
  // rotation that puts it on that heading is atan2(44, 18) = 67.75 degrees,
  // and its position is that endpoint extended along the same unit vector.
  // Anything else and the aircraft flies at an angle to its own trail. Every
  // variant here was previously wrong by 40 to 90 degrees.
  //
  // Modernised classic: the 2008 logo with the dated parts removed rather
  // than a new design. Drop shadows, the bevelled banner box, irregular
  // hand-set dash spacing and the raster artwork all go; the heavy/light type
  // contrast, the shallow scoop (not a rising arc) and the swoosh's overlap
  // with the tops of the letters all come back.
  // ---------------------------------------------------------------------
  'modern-faithful': {
    label: 'Modernised — faithful',
    note: 'the classic de-dated: heavy/light contrast restored, scoop overlapping the letters, shadows gone',
    viewBox: '0 0 170 56',
    place: 'left:-.02em;top:-.30em;height:1.45em;width:4.5em',
    heavy: 800,
    light: 450,
    track: '-0.03em',
    padTop: '0.62em',
    paths: `
    <path d="M4 14C26 40 78 44 122 26" stroke="${O}" stroke-width="7" stroke-linecap="round" fill="none" />
    <path d="M20 26C40 44 80.6 48.5 116 34" stroke="${O}" stroke-width="4.2" stroke-linecap="round" stroke-dasharray="2 7" fill="none" />
    ${plane('translate(138.6 19.2) rotate(67.75) scale(.84)')}`,
  },
  'modern-clean': {
    label: 'Modernised — clean',
    note: 'same structure, contrail dropped — the sharpest reading at small sizes',
    viewBox: '0 0 170 56',
    place: 'left:-.02em;top:-.30em;height:1.45em;width:4.5em',
    heavy: 800,
    light: 450,
    track: '-0.03em',
    padTop: '0.62em',
    paths: `
    <path d="M4 14C26 40 78 44 122 26" stroke="${O}" stroke-width="7.5" stroke-linecap="round" fill="none" />
    ${plane('translate(138.6 19.2) rotate(67.75) scale(.84)')}`,
  },
  'modern-refined': {
    label: 'Modernised — refined',
    note: 'more air, lighter "Network", wider fit — the most contemporary',
    viewBox: '0 0 170 56',
    place: 'left:-.02em;top:-.32em;height:1.5em;width:4.6em',
    heavy: 700,
    light: 350,
    track: '-0.01em',
    padTop: '0.62em',
    paths: `
    <path d="M4 14C26 40 78 44 122 26" stroke="${O}" stroke-width="7.5" stroke-linecap="round" fill="none" />
    ${plane('translate(138.6 19.2) rotate(67.75) scale(.84)')}`,
  },
  'modern-bold': {
    label: 'Modernised — bold',
    note: 'everything heavier and tighter — the most present in a header',
    viewBox: '0 0 170 56',
    place: 'left:-.02em;top:-.32em;height:1.5em;width:4.5em',
    heavy: 900,
    light: 600,
    track: '-0.045em',
    padTop: '0.62em',
    paths: `
    <path d="M4 14C26 40 78 44 122 26" stroke="${O}" stroke-width="7" stroke-linecap="round" fill="none" />
    <path d="M20 26C40 44 80.6 48.5 116 34" stroke="${O}" stroke-width="4.2" stroke-linecap="round" stroke-dasharray="2 7" fill="none" />
    ${plane('translate(138.6 19.2) rotate(67.75) scale(.84)')}`,
  },
  'teal-horizon-climbout': {
    label: 'Teal horizon climb-out',
    note: 'wide teal horizon behind the word, aircraft leaving past the end of "Network"',
    viewBox: '0 -60 460 180',
    place: 'left:-.06em;top:-2.7em;height:4.5em;width:11.5em',
    behind: true,
    padTop: '1.6em',
    paths: `
    <path d="M-16 132C90 74 370 74 476 132" stroke="${TEAL}" stroke-width="6" stroke-linecap="round" fill="none" />
    ${plane('translate(368 84) rotate(38) scale(1.7)')}`,
  },
  // ---------------------------------------------------------------------
  // THE SHIPPED LOGOTYPE. Chosen by the owner through three refinement
  // rounds (options 24 -> 25 across the decision boards; generators live in
  // scripts/render_*.py): the aircraft climbing out from behind the end of
  // "Network" over a wide teal horizon drawn as a tapered lens — the line
  // swells to 9 units at the centre and fades to nothing at the ends,
  // rather than being a uniform stroke that stops.
  //
  // Geometry is measured, not eyeballed. The artboard maps 0.025em per unit
  // with the wordmark's cap line at y=105; "Network" spans x 237-390. The
  // aircraft is scale 1.7 — its ~60-unit rotated bounding box becomes 102
  // units, two-thirds of the word's 153-unit width — at (368, 84), so its
  // belly tucks behind the letters and ~65% shows above them. The viewport
  // clips at y=120, which is what hides the art below the letter tops.
  // The taper is the same cubic doubled back on itself (controls 68/80).
  // Horizon in heritage teal so the single orange aircraft owns the focus.
  // ---------------------------------------------------------------------
  'teal-taper-climbout': {
    label: 'Teal taper climb-out',
    note: 'tapered teal horizon fading at the ends, aircraft leaving past the end of "Network"',
    viewBox: '0 -60 460 180',
    place: 'left:-.06em;top:-2.7em;height:4.5em;width:11.5em',
    behind: true,
    padTop: '1.6em',
    paths: `
    <path d="M-16 132C90 68 370 68 476 132C370 80 90 80 -16 132Z" fill="${TEAL}" />
    ${plane('translate(368 84) rotate(38) scale(1.7)')}`,
  },
} satisfies Record<string, WordmarkVariant>;

export type WordmarkVariantName = keyof typeof WORDMARK_VARIANTS;

/** The logotype the site ships. Change this one value to switch. */
export const DEFAULT_VARIANT: WordmarkVariantName = 'teal-taper-climbout';
