# Library of Alexandria — Skins Handover

**For: Claude Code, working on the Library of Alexandria Flask app.**

This package replaces the app's stylesheet layer with a token-based skin
system: **26 switchable skins** over the app's *existing markup and class
names*. No HTML, JS-behavior, or backend changes are required beyond the
integration steps below. All features (search scopes, needs-review filter,
filter panel, bulk select, enrich/edit/delete, copies, maps, stats, admin)
are untouched — this is CSS + a 70-line theme switcher only.

## The 26 skins

| id                   | Name              | Character |
|----------------------|-------------------|-----------|
| `cupertino`          | Cupertino         | Apple-light: cool neutrals, system blue, frosted toolbar (DEFAULT) |
| `reading-room`       | Reading Room      | Apple-warm: ivory, antique gold, serif display type |
| `midnight`           | Midnight          | Apple-dark: graphite, vivid blue, true elevation |
| `neon-noir`          | Neon Noir         | Cyberpunk: indigo black, cyan/magenta glow |
| `acid-terminal`      | Acid Terminal     | Cyberpunk: phosphor-green CRT, mono, scanlines |
| `night-city`         | Night City        | Cyberpunk: warm black, amber/red, cut corners |
| `blade-rain`         | BR · 2019 Rain    | Blade Runner: blue-black rain streaks, neon-sign red, washed cyan |
| `blade-tyrell`       | BR · Tyrell Corp  | Blade Runner: golden smog, bronze, deco serif (Marcellus) |
| `blade-esper`        | BR · Esper VK     | Blade Runner: pale-cyan measurement grid, machine mono |
| `neuro-matrix`       | NM · Cyberspace   | Neuromancer: black void, electric-blue lattice, ICE cyan |
| `neuro-dead-channel` | NM · Dead Channel | Neuromancer: grayscale TV static, lowercase mono, red signal dot |
| `neuro-chiba`        | NM · Chiba City   | Neuromancer: violet black, magenta + teal neon |
| `cass-beige`         | Cassette · Beige Box | Cassette futurism: console-plastic beige, Michroma, hard plastic edges |
| `cass-nostromo`      | Cassette · Nostromo  | Cassette futurism: amber CRT terminal, scanlines, MU/TH/UR prompt |
| `cass-vhs`           | Cassette · VHS 80s   | Cassette futurism (heavy 80s): magenta+cyan VHS, chromatic aberration, Audiowide |
| `atom-googie`        | Atompunk · Googie    | Atompunk: 50s optimism, teal+red, atomic dots, pill controls, Righteous |
| `atom-defense`       | Atompunk · Civil Defense | Atompunk: olive + caution-yellow stencil placards, Saira Stencil One |
| `ray-gothic`         | Raypunk · Raygun Gothic  | Raypunk: deep-space violet, starfield, gold fins, Orbitron |
| `ray-saucer`         | Raypunk · Chrome Saucer  | Raypunk: bright chrome streamline, glossy pills, Orbitron |
| `diesel-steel`       | Dieselpunk · Steelworks  | Dieselpunk: gunmetal + riveted brass, hard rules, Oswald |
| `diesel-aviator`     | Dieselpunk · Aviator     | Dieselpunk: canvas & leather tan, stitched borders, Oswald |
| `steam-brass`        | Steampunk · Brass & Mahogany | Steampunk: dark wood + brass, ornate Playfair serif, filigree |
| `steam-parchment`    | Steampunk · Parchment    | Steampunk: aged paper ledger, sepia ink, Playfair serif |
| `dos-green`          | MS-DOS · Green Screen    | DOS Navigator homage: black screen, phosphor green, double-line box borders, inverted menu bars, scanlines, VT323 |
| `tron-grid`          | Tron · The Grid          | Tron: black void + cyan perspective grid, glowing electric-blue circuitry, hot-orange adversary accent, Orbitron |
| `soviet-constructivist` | Soviet · Constructivist | Constructivist poster: aged cream paper, Party red + ink black, condensed Oswald, hard printed block shadows |

## Files in this package

| File        | Ship? | Purpose |
|-------------|-------|---------|
| `tokens.css`| YES   | All design tokens. `:root` = cupertino (no-JS fallback); one `[data-theme="…"]` block per skin. |
| `app.css`   | YES   | Every component, styled once against the tokens. Theme-specific flourishes (scanlines, clip-corners, static overlay, deco rules) scoped at the bottom. |
| `themes.js` | YES   | Injects a "Skin" `<select>` into `.topbar`, sets `data-theme` on `<html>`, persists to localStorage (`loa-skin`), exposes `window.setSkin(id)`, syncs `meta[theme-color]`. |
| `demo.js`   | NO    | Demo-only shim (fake tab nav, placeholder covers). Do not ship. |
| `HANDOVER.md` | —   | This document. |

## Integration steps

1. Copy `tokens.css`, `app.css`, `themes.js` into the app's `static/` directory.
2. In the page template (`index.html` or equivalent), **replace** the existing
   `<link rel="stylesheet" href="/static/app.css">` with:

   ```html
   <link rel="preconnect" href="https://fonts.googleapis.com">
   <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
   <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&family=IBM+Plex+Mono:wght@400;500;600;700&family=Chakra+Petch:wght@500;600;700&family=Oxanium:wght@500;600;700&family=Marcellus&family=Michroma&family=Audiowide&family=Righteous&family=Saira+Stencil+One&family=Orbitron:wght@500;600;700&family=Oswald:wght@500;600;700&family=Playfair+Display:wght@600;700&family=VT323&display=swap">
   <link rel="stylesheet" href="/static/tokens.css">
   <link rel="stylesheet" href="/static/app.css">
   <script src="/static/themes.js" defer></script>
   ```

   Keep the existing `app.js` tag unchanged, loaded after `themes.js`.
3. Done. The Skin picker appears in the topbar next to the logout button.

### Offline LAN note
The app may run on a private network with no internet access. The Google Fonts
are used only by the non-Apple skins; without network they fall back to system
fonts gracefully (the three Apple-style skins use system fonts and are
unaffected, and every skin names a system fallback so text is never invisible).
The full family list to self-host for offline fidelity: Rajdhani, Share Tech
Mono, IBM Plex Mono, Chakra Petch, Oxanium, Marcellus, Michroma, Audiowide,
Righteous, Saira Stencil One, Orbitron, Oswald, Playfair Display, VT323. Download them
with google-webfonts-helper into `/static/fonts/`, put the `@font-face` rules at
the **top of `tokens.css`**, then delete the Google `<link>` tags.

## How the system works (read before modifying)

- `<html data-theme="cupertino">` selects the skin. `themes.js` sets it; the
  server can also render it directly to avoid a flash.
- `tokens.css` defines ~55 custom properties per skin. The `:root` block is
  both the default skin **and** the canonical token list — every other theme
  block overrides a subset of the same names. **Never invent a new token in
  only one theme**; add it to `:root` first with a sensible default.
- `app.css` contains zero hard-coded colors (except inside theme-flourish
  blocks at the bottom). Components reference tokens only.

### Token cheat-sheet

| Group | Tokens |
|---|---|
| Canvas | `--bg`, `--bg-image`, `--bg-size` |
| Surfaces | `--surface` (cards), `--surface-2` (inset controls) |
| Text | `--text`, `--text-2`, `--muted` |
| Borders | `--line`, `--line-strong`, `--bw` (hairline width: 0.5px Apple, 1px cyber) |
| Accent | `--accent`, `--on-accent` (text on accent), `--accent-2` (secondary), `--accent-soft` |
| Semantic | `--ok`, `--ok-soft`, `--err`, `--err-soft` |
| Chips | `--chip-bg`, `--chip-border`, `--chip-text` |
| Controls | `--ctl-bg`, `--ctl-border` |
| Tabs | `--tab-text`, `--tab-active-bg`, `--tab-active-text`, `--tab-active-shadow` |
| Segmented | `--seg-on-bg`, `--seg-on-text`, `--seg-on-shadow` |
| Radii | `--r-card`, `--r-ctl`, `--r-chip`, `--r-cover` |
| Shadows | `--shadow-card`, `--shadow-ctl`, `--shadow-cover`, `--shadow-cover-big`, `--glow` |
| Chrome | `--topbar-bg`, `--frost` (backdrop-filter), `--wordmark-color`, `--wordmark-shadow` |
| Type | `--font-ui`, `--font-display`, `--font-meta`, `--case` (text-transform for chrome), `--track`, `--track-chrome` |

## How to modify the original (default) style

The "original" style is now the `cupertino` skin = the `:root` block in
`tokens.css`. To adjust the app's default look:

- **Change the accent color** → edit `--accent`, `--accent-soft` (and
  `--on-accent` if the accent is light) in `:root`.
- **Darker/lighter chrome** → `--topbar-bg`, `--bg`, `--surface`.
- **Rounder/squarer** → the four `--r-*` tokens.
- **Different default font** → `--font-ui` / `--font-display`.
- **Make another skin the default** → in `themes.js`, move that skin to the
  top of the `THEMES` array, **and** copy its token block's values into
  `:root` (so no-JS users get the same look).

Component-level changes (spacing, layout, sizes) live in `app.css` — they
apply to **all** skins at once, which is usually what you want. If a change
should affect one skin only, scope it: `[data-theme="midnight"] .card { … }`
and place it in the flourishes section at the bottom of `app.css`.

## How to add a 13th skin

1. Duplicate any `[data-theme="…"]` block in `tokens.css`, rename, recolor.
2. Add `{ id, name }` to the `THEMES` array in `themes.js`.
3. (Optional) Add scoped flourishes at the bottom of `app.css`.
That's the whole procedure — no other file changes.

## Known seams to verify against the live app

The package was built from a saved copy of the rendered HTML; the original
`app.css` and `app.js` were not available. After integration, check:

- **Status messages**: `.status` is styled, plus guesses `.status.ok/.success/
  .err/.error`. If `app.js` toggles different modifier classes, extend that
  rule (search `---------- status` in `app.css`).
- **View modes**: `.lib-grid.list` styles a row layout. If `app.js` switches
  grid/list/tile with other class names, point those rules at the real names.
- **Dynamically injected markup** (filter rows, enrich diffs, user lists,
  dashboards): all inherit token-based input/button/card styles, but eyeball
  each Admin/Enrich/Stats panel once per skin family (one Apple, one cyber).
- **3D map iframes** are user-uploaded standalone HTML — they keep their own
  internal styling and won't follow the skin. That's expected.
- The **emoji glyphs** in tabs/buttons are part of the markup and are kept.
  Optional upgrade: replace with inline SVG line icons (see the approved
  mockups in `Restyle Directions.html` for the icon language).
- `themes.js` assumes `.topbar` exists at DOMContentLoaded (true for
  server-rendered markup). If the topbar is ever re-rendered client-side,
  re-call `window.setSkin(localStorage.getItem('loa-skin'))` afterwards.

## QA checklist per skin

- [ ] Topbar + tabs readable; active tab clearly distinct
- [ ] Form inputs/selects/checkboxes legible incl. focus ring
- [ ] Primary vs secondary buttons distinct; disabled/hover states sane
- [ ] Library grid covers, badges, per-book actions visible
- [ ] Detail hero, tags, copies rows, map block visible
- [ ] Status ok/err messages readable
- [ ] Login overlay renders correctly
- [ ] Mobile (≤700px): detail hero stacks, grids collapse
