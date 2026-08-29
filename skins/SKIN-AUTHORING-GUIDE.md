# Skin Authoring Guide — the Library of Alexandria "skin contract"

**Audience:** Claude (or any designer) building new skins for this app on
request. Follow this exactly and a new skin drops in with **zero code changes**,
conforms to how all current skins are deployed, and avoids every bug we have
hit. This document is the single source of truth for *how to design a skin*;
`README.md` (same folder) is the source of truth for *how the files are
deployed*.

---

## 0. TL;DR — what a skin actually is

A skin = **one `[data-theme="id"]{…}` block of CSS custom properties** (in
`tokens.css`) + **one manifest entry** (in `skins.json`) + *optionally* a few
**scoped flourish rules** (in `app.css`). Nothing else. No HTML, no JS, no
backend. The whole UI re-themes because every component in `app.css` is written
against the tokens — never against hard-coded colours.

`<html data-theme="my-skin">` activates it. The picker (Admin → Appearance)
lists everything in `skins.json`. The chosen skin persists per-user in
localStorage and, when an admin sets it, as the shared default in the DB.

There are currently **34 skins**. To add the 35th you touch **two files**
(`tokens.css`, `skins.json`) and *maybe* a third (`app.css`).

---

## 1. The hard laws (break these and you reproduce old bugs)

These are non-negotiable. Every one corresponds to a bug we actually shipped
and fixed.

1. **Define the FULL token set in every skin.** Copy a complete existing block
   and recolour *every* line. Do **not** rely on inheriting from `:root`.
   - *Why:* `:root` is the light Cupertino palette. A dark skin that omits
     `--surface`/`--surface-2` inherits **white**, so its dropdown menus,
     inputs and cards render white-on-dark → the "wrong dropdown background"
     bug. All 34 current skins define all 50 tokens; yours must too.
   - The four that bite hardest if missing: `--surface` (menu/card bg),
     `--surface-2` (input/button bg), `--ctl-border`, `--accent-soft`
     (hover/selected row bg in menus).

2. **Never invent a token that exists in only one skin.** The token list is
   closed (50 names, below). If you genuinely need a new one, add it to `:root`
   first with a sensible default, then to *every* skin — otherwise components
   reading it get nothing in the other 34 skins. In practice: you never need a
   new token.

3. **No hard-coded colours in component rules.** Inside `app.css` component
   rules reference tokens only. Hard-coded colours are allowed **only** inside
   a skin's own flourish block at the bottom of `app.css`
   (`[data-theme="my-skin"] .x { … }`) — and even there, prefer `var(--…)`.

4. **Full-screen overlays must not eat clicks.** Scanlines, rain, beams, swirls
   etc. are done with `body::after`. They **must** set
   `pointer-events: none;` and live at `z-index: 999;`. Without
   `pointer-events:none` the overlay swallows every click in the app.

5. **Gate all motion behind reduced-motion.** Wrap every `animation:` in
   `@media (prefers-reduced-motion: no-preference) { … }` so print/PDF/reduced-
   motion users get a clean static state. Define the static look outside the
   media query; add motion only inside it.

6. **Don't clip popouts.** If a flourish puts `clip-path` or `overflow:hidden`
   on a container that can hold a popout (`.card`, `.search-row`, `.topbar`),
   know that the search/sort/filter menus and all skinned `<select>`s portal to
   `<body>` at runtime, so they escape — but never add `overflow:hidden` to
   `body`/`.container` or you clip the portaled menus. Outlines/box-shadows on
   covers are fine; `overflow:hidden` on `.btn`/`.book` (for a gloss sweep) is
   fine because they hold no popout.

7. **Greek must always render (core app requirement).** Book titles/authors are
   often Greek. The **body** font — `--font-ui` (and `--font-meta`) — must
   resolve to a Greek-capable face. Safe choices: any system stack
   (`-apple-system,…`, `"Iowan Old Style",…serif`), or the self-hosted
   `IBM Plex Mono`, `Oxanium`, `Chakra Petch`, `Rajdhani` (their `@font-face`
   carry greek + greek-ext subsets). Latin-only display fonts
   (Orbitron, Audiowide, Michroma, Righteous, Saira Stencil One, Special Elite,
   VT323, …) are fine for **`--font-display`** (the wordmark/headings, which are
   Latin chrome) but **never** as the sole `--font-ui`. Per-glyph fallback saves
   you if the display font is first in a stack that ends in a system face, but
   keep `--font-ui` Greek-safe by design.

8. **Don't break the no-flash boot.** `index.html` sets `data-theme` from
   localStorage *before* CSS loads. Your skin id must match between `skins.json`
   and the `tokens.css` block exactly (kebab-case, no spaces).

---

## 2. The token contract (all 50, grouped)

Copy this whole block, rename the selector, and recolour every value. `:root`
(= the `cupertino` default) is the canonical reference; values shown are
Cupertino's.

```css
[data-theme="my-skin"] {
  /* ---- Canvas (the page behind everything) ---- */
  --bg: #f5f5f7;                 /* page background colour */
  --bg-image: none;              /* optional gradients/patterns layered on --bg (grids, vignettes) */
  --bg-size: auto;               /* background-size for --bg-image (e.g. 44px 44px for a grid) */

  /* ---- Surfaces ---- */
  --surface: #ffffff;            /* cards, dropdown MENUS, modals — MUST suit --bg (opaque or near-opaque) */
  --surface-2: rgba(0,0,0,.045); /* inset controls: input/select/button backgrounds */

  /* ---- Text ---- */
  --text: #1d1d1f;               /* primary text (must pass contrast on --surface AND --bg) */
  --text-2: #424245;             /* secondary text (authors, sub-lines) */
  --muted: #86868b;              /* tertiary/labels/help text */

  /* ---- Lines / borders ---- */
  --line: rgba(0,0,0,.1);        /* hairlines, separators, card/menu borders */
  --line-strong: rgba(0,0,0,.16);/* emphasised borders */
  --bw: 0.5px;                   /* hairline WIDTH — 0.5px Apple-crisp, 1px normal, 2px+ chunky */

  /* ---- Accent ---- */
  --accent: #0071e3;             /* primary action colour: buttons, focus ring, active states */
  --on-accent: #ffffff;          /* text/icon colour ON an --accent fill (contrast!) */
  --accent-2: #0071e3;           /* secondary accent (kickers, second neon) */
  --accent-soft: rgba(0,113,227,.1); /* tinted bg: hovered/selected menu rows, soft fills */

  /* ---- Semantic ---- */
  --ok: #1d7a3e;                 /* success text */
  --ok-soft: rgba(52,199,89,.14);/* success background (status ok) */
  --err: #c0392b;                /* error text */
  --err-soft: rgba(255,59,48,.12);/* error background (status err) */

  /* ---- Chips / badges (owned, ebook, wishlist…) ---- */
  --chip-bg: rgba(0,0,0,.05);
  --chip-border: transparent;
  --chip-text: #424245;

  /* ---- Controls (the visible button/select chrome) ---- */
  --ctl-bg: #ffffff;             /* native control fill */
  --ctl-border: rgba(0,0,0,.12); /* control + dropdown-menu border */

  /* ---- Tabs (top nav) ---- */
  --tab-text: #424245;           /* inactive tab text */
  --tab-active-bg: #0071e3;      /* active tab background */
  --tab-active-text: #ffffff;    /* active tab text */
  --tab-active-shadow: none;     /* glow/elevation on the active tab */

  /* ---- Radii ---- */
  --r-card: 14px;                /* cards/menus/modals */
  --r-ctl: 9px;                  /* inputs/buttons/selects */
  --r-chip: 99px;                /* badges (99px = pill) */
  --r-cover: 7px;                /* book covers */

  /* ---- Shadows / glow ---- */
  --shadow-card: 0 1px 2px rgba(0,0,0,.04);
  --shadow-ctl:  0 1px 2px rgba(0,0,0,.05);
  --shadow-cover: 0 1px 2px rgba(0,0,0,.18), 0 6px 14px rgba(0,0,0,.12);
  --shadow-cover-big: 0 2px 4px rgba(0,0,0,.16), 0 18px 36px rgba(0,0,0,.18);
  --glow: none;                  /* neon glow used by cyber skins; none for flat skins */

  /* ---- Chrome (topbar / wordmark) ---- */
  --topbar-bg: rgba(252,252,253,.85); /* topbar fill — semi-transparent works with --frost */
  --frost: blur(20px) saturate(1.8);  /* backdrop-filter on the topbar; none to disable */
  --wordmark-color: var(--text);      /* "LIBRARY OF ALEXANDRIA" colour */
  --wordmark-shadow: none;            /* wordmark text-shadow (neon glow etc.) */

  /* ---- Type ---- */
  --font-ui: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
                                 /* BODY text — MUST be Greek-capable (law #7) */
  --font-display: var(--font-ui);/* wordmark + card/detail headings — Latin display fonts OK here */
  --font-meta: var(--font-ui);   /* facts/meta rows — Greek-capable like --font-ui */
  --case: none;                  /* text-transform for chrome: none | uppercase */
  --track: -0.01em;              /* body letter-spacing */
  --track-chrome: -0.01em;       /* chrome (tabs/wordmark) letter-spacing */

  /* ---- Segmented controls (view-mode / destination toggles) ---- */
  --seg-on-bg: #ffffff;          /* selected segment background */
  --seg-on-text: #1d1d1f;        /* selected segment text */
  --seg-on-shadow: 0 1px 3px rgba(0,0,0,.12), 0 0 0 .5px rgba(0,0,0,.04);
}
```

### Contrast budget (check before shipping)
- `--text` on `--surface` **and** on `--bg` ≥ ~4.5:1.
- `--on-accent` on `--accent` ≥ ~4.5:1 (this colours primary buttons & active tabs).
- `--muted` on `--surface` ≥ ~3:1 (it's used for help text — keep it legible).
- `--surface` must read as a surface against `--bg` (don't make them identical).

---

## 3. Flourishes (optional, in app.css) — how the current skins add character

Flourishes are scoped, additive rules that give a skin its signature. They go
in the **flourish section at the bottom of `app.css`** (just before the
`/* ---------- responsive ---------- */` block), grouped under a comment header.
They use only the app's real class names. The full list of "safe" hooks the
existing skins use:

| Hook | Used for |
|------|----------|
| `[data-theme=x] .topbar`, `.topbar .title`, `.topbar .subtitle` | banner colour, wordmark treatment, `::before/::after` tics ("FORM 27B/6", "MU/TH/UR 6000", cursor block) |
| `.tabs`, `.tab`, `.tab.active` | tab font, pill radius, active glow/underline |
| `.card`, `.card h2`, `.card h2::before/::after` | heading font, kicker glyph, divider rules |
| `.item` | `border-bottom-style: dashed` for list separators |
| `.btn`, `.btn.primary` | gradient fills, gloss sweeps (`::before` with `pointer-events:none`) |
| `.book img`, `.cover-ph`, `.detail-cover` | cover `outline`/`filter` (glow edges, desaturate) |
| `.detail-info h1` | detail-hero title font + text-shadow |
| `.badge`, `.status` | badge font/shape, status border style |
| `body::after` | **full-screen overlay** (scanlines/rain/beam/swirl) — see law #4 & #5 |

**Rules for flourishes**
- Reference tokens (`var(--accent)`, `var(--line)`) so they stay coherent if the
  palette is later tweaked. Literal colours only when the effect demands it
  (e.g. a fixed rainbow gradient).
- Keep them *additive*: never restyle layout (widths, grid columns, flex
  direction, padding that moves elements). Layout lives in the shared base rules
  and must look right in all skins. Touch only colour/border/font/shadow/pseudo-
  element decoration. (This is the "elements all over the place" guard.)
- A skin with **no** flourish block is perfectly valid — the token block alone
  delivers ~90% of the look.

### Overlay template (copy this for scanline/rain/beam effects)
```css
[data-theme="my-skin"] body::after {
  content: ""; position: fixed; inset: 0;
  pointer-events: none;        /* LAW #4 — never omit */
  z-index: 999;
  background: /* your repeating-linear-gradient / radial / conic here */ ;
}
@media (prefers-reduced-motion: no-preference) {   /* LAW #5 */
  [data-theme="my-skin"] body::after { animation: my-skin-fx 6s linear infinite; }
}
@keyframes my-skin-fx { /* … */ }
```

---

## 4. Fonts

- The app self-hosts fonts (offline/tailnet-safe — **no Google CDN at
  runtime**). Current families: Rajdhani, Share Tech Mono, IBM Plex Mono,
  Chakra Petch, Oxanium, Marcellus, Michroma, Audiowide, Righteous, Saira
  Stencil One, Orbitron, Oswald, Playfair Display, VT323, Special Elite.
- **If your skin only uses families already in that list → no font work.**
- **If you introduce a new family:**
  1. Add it to the `CSS_URL` in `fetch_fonts.py` (this folder).
  2. Run `python3 fetch_fonts.py` (needs internet). It downloads the woff2 files
     into `backend/app/static/fonts/` and regenerates
     `backend/app/static/css/fonts.css` keeping **latin + latin-ext + greek +
     greek-ext** subsets.
  3. Copy the new `fonts.css` + new `*.woff2` back into this folder (`skins/`).
  4. Use the new family for `--font-display` only unless it has Greek glyphs
     (law #7).
- Every `--font-*` value must end in a system fallback so missing fonts degrade
  gracefully (never invisible text).

---

## 5. Integration checklist (the exact steps, in order)

1. **tokens.css** — append your `[data-theme="my-skin"]{ … }` block (full 50
   tokens) at the end, under a `/* ===== My Skin ===== */` comment.
2. **skins.json** — add `{ "id": "my-skin", "name": "Display Name" }`.
   Naming convention in this app: **the specific name only, no family prefix**
   (e.g. `"Digital Rain"`, not `"Matrix · Digital Rain"`).
3. **app.css** *(optional)* — append flourishes in the flourish section,
   before the responsive block. Skip if tokens-only.
4. **fonts** *(only if new family)* — section 4 above.
5. **sw.js** — bump `const CACHE = 'loa-vNN'` so clients refetch the CSS.
6. **skins/** — re-sync the four assets (+ fonts) into this folder so it stays
   the rebuild source (README §"How to re-incorporate").
7. **Verify** (section 6).

No `app.js`, `index.html`, or Python change is ever needed: the picker reads
`skins.json`, and `GET/POST /api/settings` stores the skin id as a free-form
string (no allow-list).

---

## 6. Self-verification (run before declaring done)

- **Token completeness:** the new block defines all 50 tokens. Quick check —
  it should have the same count as `:root`:
  ```bash
  awk '/data-theme="my-skin"/{f=1} f{print} f&&/^}/{exit}' tokens.css \
    | grep -cE '^\s*--[a-z0-9-]+\s*:'   # expect 50
  ```
- **ID consistency:** every `skins.json` id has a token block and vice-versa;
  every `app.css` flourish id has a token block.
- **Brace balance:** `{` count == `}` count in tokens.css and app.css.
- **Fonts resolve:** every `url(/static/fonts/*.woff2)` in fonts.css exists on
  disk.
- **Overlays:** every `body::after` you added has `pointer-events:none`.
- **Visual pass:** render the skin and confirm, against the QA list below.

### QA checklist (per skin)
- [ ] Topbar wordmark + tabs readable; active tab clearly distinct
- [ ] Card headings, body, muted/meta text legible on the surface
- [ ] **Open a search/filter dropdown** — its menu background matches the skin
      (NOT white-on-dark), hover row uses `--accent-soft`, text legible
- [ ] Inputs/selects/buttons legible; primary vs secondary distinct; focus ring visible
- [ ] Library grid covers, badges, per-book actions visible; **Greek title renders**
- [ ] Detail hero, tags, copies, map block visible
- [ ] Status ok/err messages readable; login overlay renders
- [ ] Any full-screen overlay does not wash out text and does not block clicks
- [ ] Reduced-motion: animations stop, static look remains correct
- [ ] Mobile (≤700px): detail hero stacks, grids collapse

---

## 7. Minimal deliverable format (when asked for "a new skin")

Produce, in this order:

1. The `[data-theme="id"]{…}` token block (all 50 tokens).
2. The `skins.json` entry line.
3. (If any) the flourish block for `app.css`.
4. (If any new font) the family name(s) to add to `fetch_fonts.py`.
5. A one-line note of the intended character + which `--font-ui` keeps Greek safe.

That is everything needed to integrate. Keep ids kebab-case and unique; keep
names short and specific.
