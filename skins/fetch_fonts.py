"""Regenerate the self-hosted fonts.css for ALL skin families (offline/tailnet-safe).
Keeps latin + latin-ext + greek + greek-ext subsets (Greek is a core requirement).
Original 6 families + 8 new families needed by the 14 new skins."""
import os, re, urllib.request

CSS_URL = ("https://fonts.googleapis.com/css2?"
           # --- original 6 ---
           "family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&"
           "family=IBM+Plex+Mono:wght@400;500;600;700&family=Chakra+Petch:wght@500;600;700&"
           "family=Oxanium:wght@500;600;700&family=Marcellus&"
           # --- 8 new (for the 14 new skins; decorative chrome only) ---
           "family=Michroma&family=Audiowide&family=Righteous&"
           "family=Saira+Stencil+One&family=Orbitron:wght@500;600;700&"
           "family=Oswald:wght@500;600;700&family=Playfair+Display:wght@600;700&"
           "family=VT323&"
           # --- pack 2: 1 new family (Special Elite typewriter, brazil-ministry) ---
           "family=Special+Elite&display=swap")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
KEEP = {"latin", "latin-ext", "greek", "greek-ext"}
FONTS_DIR = "/media/VM/library-of-alexandria/backend/app/static/fonts"
OUT_CSS = "/media/VM/library-of-alexandria/backend/app/static/css/fonts.css"

os.makedirs(FONTS_DIR, exist_ok=True)
req = urllib.request.Request(CSS_URL, headers=UA)
css = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

blocks = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{[^}]*\})", css)
out, seen, downloaded = [], set(), 0
for subset, block in blocks:
    if subset not in KEEP:
        continue
    m = re.search(r"url\((https://[^)]+\.woff2)\)", block)
    if not m:
        continue
    woff = m.group(1)
    fname = woff.split("/")[-1]
    if fname not in seen:
        seen.add(fname)
        urllib.request.urlretrieve(woff, os.path.join(FONTS_DIR, fname))
        downloaded += 1
    block = block.replace(woff, "/static/fonts/" + fname)
    out.append(f"/* {subset} */\n{block}")

with open(OUT_CSS, "w", encoding="utf-8") as f:
    f.write("/* Self-hosted fonts (offline/tailnet-safe). Generated from Google Fonts;\n"
            "   latin + latin-ext + greek + greek-ext subsets. 14 families for 26 skins. */\n\n")
    f.write("\n\n".join(out) + "\n")

fams = sorted(set(re.search(r"font-family:\s*'([^']+)'", b).group(1) for b in out))
print(f"downloaded {downloaded} new woff2 files, {len(out)} @font-face blocks")
print("families:", ", ".join(fams))
