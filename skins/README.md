# Library of Alexandria — Skins (source of truth)

This folder is the **complete, self-contained source** for the app's skin
system. Everything needed to re-incorporate skins into a rebuilt app lives
here — CSS, the picker manifest, the self-hosted fonts, and the font fetcher.

**34 skins** total (1 default + 33 alternatives). The files here are exact
copies of what is currently deployed under `backend/app/static/`.

> **To add more skins:** read `SKIN-AUTHORING-GUIDE.md` in this folder — it is
> the complete, authoritative spec (the "skin contract") for authoring new
> skins that drop in cleanly and avoid every bug we have hit. The `HANDOVER.md`
> here is the original 26-skin package handover, kept for historical reference
> only; the guide and this README supersede it.

## Files in this folder

| File / dir        | Deploy target                              | Purpose |
|-------------------|--------------------------------------------|---------|
| `SKIN-AUTHORING-GUIDE.md` | — | **The skin contract.** Authoritative, thorough spec for building new skins (every token, flourish rules, the bug-avoidance laws, integration checklist). Read this first to add skins. |
| `tokens.css`      | `backend/app/static/css/tokens.css`        | All design tokens. `:root` = `cupertino` (default + canonical token list); one `[data-theme="id"]{…}` block per other skin (33 blocks). 50 tokens each. |
| `app.css`         | `backend/app/static/css/app.css`           | Every component styled once against tokens, + per-skin flourishes at the bottom, + the **Library of Alexandria custom appends** (`.muted`, `.cover-ph`, `.dd-*` data dictionary, `.fdrop-*`/`.nsel` skinned dropdowns, `.fp-*` folder picker, `.skin-grid`, stat bars). These appends are NOT in the original package — keep them. |
| `fonts.css`       | `backend/app/static/css/fonts.css`         | `@font-face` for all 15 families, self-hosted (offline/tailnet-safe). latin + latin-ext + **greek + greek-ext** subsets (Greek is a core requirement). |
| `fonts/`          | `backend/app/static/fonts/`                | The 42 `.woff2` files referenced by `fonts.css`. Ship these for offline fidelity. |
| `skins.json`      | `backend/app/static/skins.json`            | `[{id,name}]` manifest that drives the Admin skin picker. 34 entries. |
| `fetch_fonts.py`  | run from anywhere                          | Regenerates `fonts.css` + downloads the woff2 files from Google Fonts. Use only to add/refresh fonts; needs internet. |
| `HANDOVER.md`     | —                                          | Original 26-skin package handover, kept for historical reference. Superseded by this README + the authoring guide. |

> Obsolete files from the original packages (`tokens-batch2a.css`,
> `tokens-batch2b.css`, `demo.js`, `themes.js`) were removed — they are not
> used by this app (see "How the picker works" below). The raw drop folders
> `new_skins/` and `new_skins_2/` were folded into this folder and deleted.

## How to re-incorporate skins into a rebuilt app

1. Copy the four assets to their targets:
   - `tokens.css`, `app.css`, `fonts.css` → `backend/app/static/css/`
   - `skins.json` → `backend/app/static/`
   - `fonts/*.woff2` → `backend/app/static/fonts/`
2. In `backend/app/templates/index.html` `<head>`, BEFORE the stylesheets,
   keep the no-flash script that sets the theme from localStorage:
   ```html
   <script>
     (function () {
       try {
         var s = localStorage.getItem("loa-skin") || "cupertino";
         document.documentElement.setAttribute("data-theme", s);
       } catch (e) { document.documentElement.setAttribute("data-theme", "cupertino"); }
     })();
   </script>
   <link rel="stylesheet" href="/static/css/fonts.css">
   <link rel="stylesheet" href="/static/css/tokens.css">
   <link rel="stylesheet" href="/static/css/app.css">
   ```
   Load order matters: **fonts → tokens → app**.
3. Bump the service-worker cache constant in `backend/app/static/sw.js`
   (`const CACHE = 'loa-vNN'`) so clients fetch the new CSS. The shell
   precaches `app.css`, `tokens.css`, `fonts.css`.
4. No backend change is needed: `GET/POST /api/settings` stores the chosen
   skin as a free-form string in the `settings` table (key `skin`); it does
   NOT validate against a fixed list, so new skins work automatically.

## How the picker works (this app — NOT the package's `themes.js`)

The original package shipped a `themes.js` that injects a `<select>` into the
topbar. **This app does not use it.** Instead the picker lives under **Admin →
Appearance** and is driven by `app.js`:

- `loadSkinPicker()` populates `#skin-select` from `/static/skins.json`.
- `applySkin(id, persist)` sets `<html data-theme=…>`, writes localStorage
  `loa-skin`, and (if persist) `POST /api/settings {skin}`.
- `applyServerSkin()` on login applies the DB-stored skin to **everyone**
  (admin's choice = shared default).
- `skinSelect()` / `skinAllSelects()` skin every native `<select>` app-wide by
  mirroring options into a token-styled `.fdrop-menu` (the native popup ignores
  CSS tokens, so this avoids "white dropdown on a dark skin").

So to add the picker you only need `skins.json` + the existing `app.js`
functions + the Admin "Appearance" card markup. No `themes.js`.

## To add a 27th skin

1. Append a `[data-theme="myid"]{ … }` block to `tokens.css` — **copy an
   existing 50-token block and recolour every token.** Never leave a token
   undefined on a dark skin (it would inherit cupertino's light value — the
   classic "wrong dropdown background" bug). Critical ones: `--bg`,
   `--surface`, `--surface-2`, `--text`, `--line`, `--ctl-border`,
   `--accent`, `--accent-soft`.
2. Add `{ "id":"myid", "name":"My Name" }` to `skins.json`.
3. (Optional) Add scoped flourishes at the bottom of `app.css`:
   `[data-theme="myid"] .card { … }`. If a flourish uses `clip-path` or
   `overflow` on a container that holds a popout, the popout is portaled to
   `<body>` by `fieldDropdown`/`skinSelect`, so it won't be clipped.
4. (Optional) If the skin needs a new web font, add the family to
   `fetch_fonts.py`'s `CSS_URL`, run it (needs internet), and re-copy
   `fonts.css` + the new `fonts/*.woff2`. Body text (`--font-ui`) must use a
   Greek-capable font (system or a self-hosted family with greek subsets);
   new web fonts are for decorative chrome (`--font-display`) only.

## Bug-avoidance checklist (the ones we actually hit)

- **Dropdown background wrong colour** → every skin defines its own
  `--surface`/`--surface-2`/`--ctl-border`/`--accent-soft`. All 26 verified.
- **Native `<select>` popups blue-and-white in every skin** → `skinSelect()`
  replaces them with token-styled custom dropdowns. (The 4 rich field
  dropdowns are in `_NO_SKIN` and use grouped/example menus instead.)
- **Menus clipped / "behind the books"** (clip-path skins like `night-city`)
  → popouts portal to `<body>`; no ancestor can clip them.
- **Full-screen scanline/static overlays** (`acid-terminal`, `cass-nostromo`,
  `cass-vhs`, `dos-green`) use `body::after` with `pointer-events:none` so they
  never block clicks.
