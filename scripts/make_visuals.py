"""Profile visuals: the character portrait in a terminal window, a project constellation and a launch timeline.

Run from the repository root:  python scripts/make_visuals.py
Needs Pillow; repository data comes from the public GitHub API.
"""
import json
import urllib.request
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

USER = "Eyad-Elnakib1"
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

# Featured projects: repository name -> name shown and a short line.
FEATURED = {
    "Atelier": ("Atelier", "Clothes segmentation & restyling"),
    "Automated-Transit-Safety-Platform-with-RAG-Powered-Analytics": ("Transit Safety Platform", "Driver monitoring + RAG analytics"),
    "Real-Eyes": ("RealEyes", "Deepfake detection & fact-checking"),
    "Fathia-AI-Development-of-an-Intelligent-Culinary-Assistant-and-Food-Community-": ("Fridge Fusion", "AI chef & food community"),
    "KodAI": ("KodAI", "AI competitive-programming coach"),
    "Generative-models-VAE-DDPM": ("VAE & DDPM", "Generative models from scratch"),
}
LANG = {"Python": "PY", "JavaScript": "JS", "TypeScript": "TS", "Jupyter Notebook": "NB", None: "AI"}

# Palette shared with the portrait
BG, PANEL, BORDER = "#0b0a14", "#100e1d", "#2b2547"
ACCENT, LAVENDER, TEXT, MUTED = "#7c5cff", "#b79cff", "#ece8ff", "#8f87b3"
MONO = "JetBrains Mono, Consolas, 'Courier New', monospace"


def repos():
    req = urllib.request.Request(f"https://api.github.com/users/{USER}/repos?per_page=100", headers={"User-Agent": "profile-visuals"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    by_name = {r["name"]: r for r in data}
    out = []
    for name, (title, line) in FEATURED.items():
        r = by_name.get(name)
        if not r:
            continue
        out.append({"name": name, "title": title, "line": line, "lang": r["language"], "created": r["created_at"][:10],
                    "url": r["html_url"], "stars": r["stargazers_count"]})
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def frame(width, height, kicker, title, body, footer=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">
<defs>
  <radialGradient id="glow" cx="50%" cy="45%" r="60%"><stop offset="0%" stop-color="{ACCENT}" stop-opacity="0.16"/><stop offset="100%" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
  <radialGradient id="orb" cx="40%" cy="35%" r="70%"><stop offset="0%" stop-color="#9d84ff"/><stop offset="60%" stop-color="#4b33a8"/><stop offset="100%" stop-color="#241a52"/></radialGradient>
  <radialGradient id="orbSmall" cx="40%" cy="35%" r="70%"><stop offset="0%" stop-color="#7f6be0"/><stop offset="100%" stop-color="#1f1846"/></radialGradient>
</defs>
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.5"/>
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" fill="url(#glow)"/>
<text x="36" y="44" font-family="{MONO}" font-size="11" letter-spacing="3" fill="{MUTED}">{esc(kicker)}</text>
<text x="36" y="80" font-family="{MONO}" font-size="24" fill="{TEXT}">{esc(title)}</text>
<line x1="36" y1="104" x2="{width - 36}" y2="104" stroke="{BORDER}" stroke-dasharray="6 8"/>
{body}
{f'<text x="36" y="{height - 26}" font-family="{MONO}" font-size="12" fill="{MUTED}">{esc(footer)}</text>' if footer else ''}
</svg>
"""


def node(cx, cy, r, code, big=False, delay=0.0):
    ring = r + 12
    return f"""<g>
  <circle cx="{cx}" cy="{cy}" r="{ring}" fill="none" stroke="{LAVENDER}" stroke-opacity="0.45" stroke-dasharray="10 7">
    <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="{40 if big else 28}s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{'orb' if big else 'orbSmall'})" stroke="{ACCENT}" stroke-opacity="0.8">
    <animate attributeName="r" values="{r};{r + 2};{r}" dur="4s" begin="{delay}s" repeatCount="indefinite"/>
  </circle>
  <rect x="{cx - 15}" y="{cy - 15}" width="30" height="30" rx="7" fill="{BG}" fill-opacity="0.55" stroke="{LAVENDER}" stroke-opacity="0.7"/>
  <text x="{cx}" y="{cy + 4}" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="700" fill="{LAVENDER}">{code}</text>
</g>"""


def constellation(items):
    W, H = 900, 540
    # Centre: Atelier. Others on an ellipse around it.
    pos = {"Atelier": (450, 330, 46)}
    spots = [(180, 200), (200, 430), (700, 430), (720, 200), (450, 160)]
    others = [i for i in items if i["name"] != "Atelier"]
    for i, (x, y) in zip(others, spots):
        pos[i["name"]] = (x, y, 28)
    cx, cy, _ = pos["Atelier"]
    lines, nodes, labels = [], [], []
    for k, i in enumerate(items):
        x, y, r = pos[i["name"]]
        if i["name"] != "Atelier":
            lines.append(f'<path d="M{cx},{cy} Q{(cx + x) / 2},{(cy + y) / 2 - 30} {x},{y}" fill="none" stroke="{LAVENDER}" stroke-opacity="0.35" stroke-dasharray="3 6"/>')
        nodes.append(node(x, y, r, LANG.get(i["lang"], "AI"), big=(r > 40), delay=k * 0.6))
        when = datetime.strptime(i["created"], "%Y-%m-%d").strftime("%b %Y")
        ly = y + r + 34
        labels.append(f'<a href="{i["url"]}"><text x="{x}" y="{ly}" text-anchor="middle" font-family="{MONO}" font-size="{17 if r > 40 else 15}" font-weight="700" fill="{TEXT}">{esc(i["title"])}</text></a>'
                      f'<text x="{x}" y="{ly + 18}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{esc(i["line"])} · {when}</text>')
    stars = "".join(f'<circle cx="{x}" cy="{y}" r="{s}" fill="{LAVENDER}" opacity="{o}"><animate attributeName="opacity" values="{o};0.1;{o}" dur="{d}s" repeatCount="indefinite"/></circle>'
                    for x, y, s, o, d in [(80, 140, 1.4, 0.7, 3), (840, 130, 1.2, 0.6, 4), (590, 510, 1.3, 0.5, 5), (330, 250, 1, 0.5, 3.5), (800, 300, 1, 0.6, 4.5), (110, 300, 1.2, 0.5, 5.5)])
    body = stars + "".join(lines) + "".join(nodes) + "".join(labels)
    return frame(W, H, "PROJECT CONSTELLATION", "A universe of work", body)


def timeline(items):
    W, H = 1000, 430
    seq = sorted(items, key=lambda i: i["created"])
    y0, x_left, x_right = 250, 150, W - 150
    step = (x_right - x_left) / max(1, len(seq) - 1)
    parts = [f'<line x1="{x_left - 30}" y1="{y0}" x2="{x_right + 30}" y2="{y0}" stroke="{LAVENDER}" stroke-opacity="0.5" stroke-dasharray="8 8">'
             f'<animate attributeName="stroke-dashoffset" values="0;-32" dur="2s" repeatCount="indefinite"/></line>']
    for k, i in enumerate(seq):
        x = x_left + k * step
        big = i["name"] == "Atelier"
        r = 16 if big else 11
        parts.append(f'<circle cx="{x}" cy="{y0}" r="{r + 10}" fill="none" stroke="{LAVENDER}" stroke-opacity="0.45" stroke-dasharray="6 5"/>'
                     f'<circle cx="{x}" cy="{y0}" r="{r}" fill="url(#orbSmall)" stroke="{ACCENT}"><animate attributeName="r" values="{r};{r + 2};{r}" dur="3s" begin="{k * 0.4}s" repeatCount="indefinite"/></circle>'
                     f'<circle cx="{x}" cy="{y0}" r="4" fill="{LAVENDER}"/>')
        d = datetime.strptime(i["created"], "%Y-%m-%d")
        up = k % 2 == 0
        ty = y0 - 112 if up else y0 + 52
        parts.append(f'<text x="{x}" y="{ty}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{d.strftime("%d / %b %Y")}</text>'
                     f'<a href="{i["url"]}"><text x="{x}" y="{ty + 26}" text-anchor="middle" font-family="{MONO}" font-size="15" font-weight="700" fill="{TEXT}">{esc(i["title"])}</text></a>'
                     f'<text x="{x}" y="{ty + 46}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{MUTED}">{esc(i["line"])}</text>'
                     + (f'<text x="{x}" y="{ty + 64}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{LAVENDER}">{esc(i["lang"])}</text>' if i["lang"] else ''))
    footer = f"{len(seq)} featured repositories · follow the line from the first launch to the latest"
    return frame(W, H, "PROJECT LAUNCH SEQUENCE", "Where the work went next", "".join(parts), footer)


FONTS = Path(r"C:\Windows\Fonts")


def _font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def _sticker(kind, S):
    """One sticker in the portrait's style: dark panel, faint dot texture, lavender outline, monospace text."""
    W, H = {"eat": (250, 270), "mode": (260, 200), "alone": (250, 280), "rule": (270, 210)}[kind]
    W, H = W * S, H * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=22 * S, fill=(18, 15, 34, 245), outline=(183, 156, 255, 255), width=3 * S)
    for y in range(14 * S, H - 10 * S, 9 * S):                       # dot texture like the circle behind the portrait
        for x in range(14 * S, W - 10 * S, 9 * S):
            d.point((x, y), fill=(124, 92, 255, 70))
    bold = lambda n: _font("consolab.ttf", n * S)
    sym = lambda n: _font("seguisym.ttf", n * S)
    LAV, WHITE, ACC, DIM = (183, 156, 255), (240, 236, 255), (124, 92, 255), (120, 105, 180)
    if kind == "eat":
        for k, (icon, word) in enumerate((("Ψ", "EAT"), ("☾", "SLEEP"), ("</>", "CODE"), ("⟳", "REPEAT"))):
            y = (24 + k * 60) * S
            d.rounded_rectangle([20 * S, y, 70 * S, y + 50 * S], radius=8 * S, fill=ACC + (255,) if k == 2 else (40, 32, 78, 255))
            f = bold(20) if icon == "</>" else sym(28)
            tw = d.textlength(icon, font=f)
            d.text((45 * S - tw / 2, y + (12 if icon == "</>" else 4) * S), icon, font=f, fill=WHITE)
            d.text((84 * S, y + 6 * S), word, font=bold(32), fill=WHITE if k == 2 else LAV)
    elif kind == "mode":
        for k, word in enumerate(("ENGINEER", "MODE")):
            f = bold(40 if k else 34)
            tw = d.textlength(word, font=f)
            d.text(((W - tw) / 2, (20 + k * 42) * S), word, font=f, fill=WHITE, stroke_width=S, stroke_fill=ACC)
        x0, y0, x1, y1 = 28 * S, 122 * S, W - 28 * S, 176 * S
        d.rounded_rectangle([x0, y0, x1, y1], radius=27 * S, fill=ACC + (255,), outline=LAV + (255,), width=2 * S)
        d.text((x0 + 22 * S, y0 + 8 * S), "ON", font=bold(32), fill=WHITE)
        r = 21 * S
        d.ellipse([x1 - 6 * S - 2 * r, y0 + 6 * S, x1 - 6 * S, y0 + 6 * S + 2 * r], fill=WHITE)
    elif kind == "alone":
        for k, word in enumerate(("LEAVE ME ALONE!", "I'M CODING!")):
            f = bold(22)
            tw = d.textlength(word, font=f)
            d.text(((W - tw) / 2, (18 if k == 0 else 236) * S), word, font=f, fill=WHITE if k else LAV)
        art = ["     \\ | /    ", "      _O_     ", "     / | \\ __ ", "  ___/_|_\\|==|", " |   |   ||__|", " |___|___|    ", "   |     |    "]
        f = bold(17)
        for k, line in enumerate(art):
            tw = d.textlength(line, font=f)
            d.text(((W - tw) / 2, (62 + k * 23) * S), line, font=f, fill=LAV if k else ACC)
    elif kind == "rule":
        for k, col in enumerate(((255, 95, 87), (254, 188, 46), (40, 200, 64))):
            cx, cy = (26 + k * 24) * S, 26 * S
            d.ellipse([cx - 8 * S, cy - 8 * S, cx + 8 * S, cy + 8 * S], fill=col)
        lines = [("First rule of", WHITE), ("programming:", WHITE), ("If it works,", LAV), ("don't touch it.", (236, 120, 160))]
        for k, (t, col) in enumerate(lines):
            d.text((24 * S, (54 + k * 36) * S), t, font=bold(25), fill=col)
    return img


def window(portrait_path, out_path):
    """The portrait inside a wide terminal-style window, with stickers on both sides."""
    p = Image.open(portrait_path).convert("RGB")
    S = 2
    pw, ph = p.size
    pad, bar, label_h, side = 26, 70, 40, 300
    W, H = pw + 2 * pad + 24 + 2 * side, ph + bar + label_h + 2 * pad + 10
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W * S - 1, H * S - 1], radius=18 * S, fill="#0d0b17", outline="#2b2547", width=2 * S)
    d.line([(0, bar * S), (W * S, bar * S)], fill="#2b2547", width=S)
    for k, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        cx, cy = (34 + k * 38) * S, (bar // 2) * S
        d.ellipse([cx - 12 * S, cy - 12 * S, cx + 12 * S, cy + 12 * S], fill=col)
    font = _font("consola.ttf", 20 * S)
    small = _font("consolab.ttf", 18 * S)
    t = "eyad-elnakib1 — portrait.map"
    d.text(((W - 18) * S - d.textlength(t, font=font), (bar // 2 - 12) * S), t, font=font, fill="#8f87b3")
    x0, y0 = pad * S, (bar + pad - 6) * S
    x1, y1 = (W - pad) * S, (H - pad) * S
    d.rounded_rectangle([x0, y0, x1, y1], radius=12 * S, outline="#3d3270", width=S)
    d.rectangle([x0 + 2 * S, y0 + 2 * S, x1 - 2 * S, y1 - 2 * S], fill=(10, 8, 18, 255))   # same black as the portrait
    d.text((x0 + 14 * S, y0 + 10 * S), "V I S U A L . M A P", font=small, fill="#9d84ff")
    big = p.resize((pw * S, ph * S), Image.LANCZOS)
    px = x0 + (side + 12) * S
    img.paste(big, (px, y0 + label_h * S))
    # stickers: two on each side, tilted a little like real stickers
    inner_top = y0 + label_h * S
    inner_h = ph * S
    left_c = x0 + (side // 2 + 8) * S
    right_c = px + pw * S + (side // 2 + 4) * S
    for kind, cx, fy, angle in (("eat", left_c, 0.27, 6), ("alone", left_c, 0.74, -5), ("mode", right_c, 0.25, -6), ("rule", right_c, 0.72, 5)):
        st = _sticker(kind, S).rotate(angle, resample=Image.BICUBIC, expand=True)
        shadow = Image.new("RGBA", st.size, (0, 0, 0, 0))
        shadow.putalpha(st.getchannel("A").point(lambda v: int(v * 0.45)))
        cy = inner_top + int(inner_h * fy)
        img.alpha_composite(shadow, (cx - st.width // 2 + 8 * S, cy - st.height // 2 + 10 * S))
        img.alpha_composite(st, (cx - st.width // 2, cy - st.height // 2))
    sy = y0 + (label_h + int(ph * 0.82)) * S          # a faint scan line across the window
    d = ImageDraw.Draw(img)
    d.line([(x0 + 2 * S, sy), (x1 - 2 * S, sy)], fill=(157, 132, 255, 90), width=S)
    img = img.resize((W, H), Image.LANCZOS)
    img.save(out_path, optimize=True)
    return img.size


if __name__ == "__main__":
    items = repos()
    (ASSETS / "constellation.svg").write_text(constellation(items), encoding="utf-8")
    (ASSETS / "timeline.svg").write_text(timeline(items), encoding="utf-8")
    print("cards:", [i["title"] for i in items])
    print("window:", window(ASSETS / "portrait.png", ASSETS / "portrait-window.png"))
