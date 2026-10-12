"""Generates the 3D SVG artwork used in the profile README.

Run from the repo root:  python tools/build.py
Everything is plain SVG + SMIL/CSS animation with fonts embedded as data URIs,
so it renders the same inside GitHub's <img> sandbox on every machine.
Needs: fonttools, brotli (font subsetting) and the gh CLI (contribution data).
"""
import base64
import html
import io
import math
import random
import textwrap
from functools import lru_cache
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"
FLUENT = ASSETS / "fluent"
FONT_DIR = Path(__file__).resolve().parent / "fonts"

BG = "#060816"
CYAN = "#22d3ee"
TEAL = "#2dd4bf"
VIOLET = "#8b5cf6"
PINK = "#f472b6"
INK = "#e2e8f0"
MUTED = "#94a3b8"

DISPLAY = "'Orb', 'Segoe UI', Arial, sans-serif"      # Orbitron: ASCII only!
FONT = "'SG', 'Segoe UI', Arial, sans-serif"          # Space Grotesk
MONO = "'JB', Consolas, monospace"                    # JetBrains Mono

random.seed(7)
esc = lambda s: html.escape(s, quote=True)   # safe for both text nodes and attributes


def f(v):
    """Compact number formatting."""
    return f"{v:.1f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- fonts
FONT_FACES = {  # css family -> [(source file, weight)]
    "Orb": [("Orbitron", 900)],
    "SG": [("SpaceGrotesk", 400), ("SpaceGrotesk", 700)],
    "JB": [("JetBrainsMono", 500)],
}
CHARSET = "".join(chr(c) for c in range(32, 127)) + "·→ōŌ–—’×é"


@lru_cache(None)
def woff2(src, weight):
    """Pin the variable font to one weight, subset it, return base64 woff2."""
    font = instancer.instantiateVariableFont(TTFont(FONT_DIR / f"{src}.ttf"), {"wght": weight})
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    sub = subset.Subsetter(opts)
    sub.populate(text=CHARSET)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def write(name, svg):
    faces = []
    for fam, variants in FONT_FACES.items():
        if f"'{fam}'" in svg:
            for src, w in variants:
                faces.append(f"@font-face{{font-family:'{fam}';font-weight:{w};"
                             f"src:url(data:font/woff2;base64,{woff2(src, w)}) format('woff2')}}")
    if faces:
        cut = svg.index(">") + 1
        svg = svg[:cut] + f"<style>{''.join(faces)}</style>" + svg[cut:]
    (ASSETS / name).write_text(svg, encoding="utf-8")
    print(f"{name}: {len(svg.encode()) / 1024:.0f} KB")


def fluent(key):
    """Microsoft Fluent 3D emoji (MIT), embedded so GitHub's image proxy can't break them."""
    return "data:image/png;base64," + base64.b64encode((FLUENT / f"{key}.png").read_bytes()).decode()


def icon_uri(key):
    return "data:image/svg+xml;base64," + base64.b64encode((ICONS / f"{key}.svg").read_bytes()).decode()


def wrap(text, px, size):
    """Wrap by an estimated Space Grotesk character width."""
    return textwrap.wrap(text, max(10, int(px / (size * 0.53))))


def extruded_text(text, x, y, size, depth=9, anchor="start", grad="gTxt", side="#3b1d6e", spacing=2):
    """Fake 3D extrusion: stacked copies offset down-right, then a bright face on top."""
    common = (f'x="{x}" font-family="{DISPLAY}" font-size="{size}" font-weight="900" '
              f'letter-spacing="{spacing}" text-anchor="{anchor}"')
    layers = [f'<text {common} y="{y}" dx="{i}" dy="{i}" fill="{side if i > 1 else "#1e0b3d"}">{esc(text)}</text>'
              for i in range(depth, 0, -1)]
    layers.append(f'<text {common} y="{y}" fill="url(#{grad})" stroke="#fff" stroke-opacity=".25" stroke-width="1">{esc(text)}</text>')
    return "\n".join(layers)


COMMON_DEFS = f"""
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="bigGlow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="18"/></filter>
<linearGradient id="gTxt" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="#a78bfa"/><stop offset="1" stop-color="{PINK}"/>
  <animate attributeName="x1" values="0;-1;0" dur="8s" repeatCount="indefinite"/>
  <animate attributeName="x2" values="1;2;1" dur="8s" repeatCount="indefinite"/>
</linearGradient>
<radialGradient id="panelBg" cx=".5" cy=".4" r=".8"><stop offset="0" stop-color="#140f35"/><stop offset="1" stop-color="{BG}"/></radialGradient>"""


def panel(W, H):
    return (f'<rect width="{W}" height="{H}" rx="22" fill="url(#panelBg)"/>'
            f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="{VIOLET}" stroke-opacity=".4" stroke-width="2"/>')


# ---------------------------------------------------------------- 3D mesh
def icosphere(subdiv=1):
    t = (1 + 5 ** 0.5) / 2
    verts = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t),
             (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4),
             (11, 10, 2), (10, 7, 6), (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8),
             (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    norm = lambda v: tuple(c / math.sqrt(sum(k * k for k in v)) for c in v)
    verts = [norm(v) for v in verts]
    for _ in range(subdiv):
        cache, new_faces = {}, []

        def mid(a, b):
            key = tuple(sorted((a, b)))
            if key not in cache:
                va, vb = verts[a], verts[b]
                verts.append(norm(tuple((va[i] + vb[i]) / 2 for i in range(3))))
                cache[key] = len(verts) - 1
            return cache[key]

        for a, b, c in faces:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            new_faces += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        faces = new_faces
    edges = sorted({tuple(sorted(e)) for a, b, c in faces for e in ((a, b), (b, c), (c, a))})
    return verts, edges


def project(v, angle, tilt, cx, cy, r, cam=3.2):
    x, y, z = v
    ca, sa = math.cos(angle), math.sin(angle)
    x, z = x * ca + z * sa, -x * sa + z * ca           # spin around Y
    ct, st = math.cos(tilt), math.sin(tilt)
    y, z = y * ct - z * st, y * st + z * ct            # tilt around X
    k = cam / (cam - z)                                # perspective divide
    return cx + x * r * k, cy - y * r * k, z


def spinning_globe(cx, cy, r, frames=48, dur=18):
    verts, edges = icosphere(1)
    tilt = math.radians(-18)
    per_frame = [[project(v, 2 * math.pi * i / frames, tilt, cx, cy, r) for v in verts] for i in range(frames + 1)]
    ds = ["".join(f"M{f(p[a][0])} {f(p[a][1])}L{f(p[b][0])} {f(p[b][1])}" for a, b in edges) for p in per_frame]
    out = [f'<path fill="none" stroke="url(#gGlobe)" stroke-width="1.1" stroke-opacity=".75" d="{ds[0]}">'
           f'<animate attributeName="d" dur="{dur}s" repeatCount="indefinite" values="{";".join(ds)}"/></path>']
    # vertices: size + opacity follow depth, so the front glows and the back fades
    for vi in range(len(verts)):
        anim = lambda attr, vals: f'<animate attributeName="{attr}" dur="{dur}s" repeatCount="indefinite" values="{";".join(vals)}"/>'
        out.append(f'<circle fill="{PINK if vi % 7 == 0 else CYAN}" filter="url(#glow)">'
                   + anim("cx", [f(p[vi][0]) for p in per_frame])
                   + anim("cy", [f(p[vi][1]) for p in per_frame])
                   + anim("r", [f(1.3 + 1.6 * (p[vi][2] + 1)) for p in per_frame])
                   + anim("opacity", [f"{0.15 + 0.85 * (p[vi][2] + 1) / 2:.2f}" for p in per_frame])
                   + "</circle>")
    return "\n".join(out)


def stars(w, n, max_y):
    out = []
    for _ in range(n):
        x, y = random.uniform(0, w), random.uniform(0, max_y)
        d = random.uniform(2, 6)
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{random.choice([0.5, 0.7, 0.9, 1.2])}" fill="#fff">'
                   f'<animate attributeName="opacity" values=".1;.9;.1" dur="{f(d)}s" begin="{f(random.uniform(0, d))}s" repeatCount="indefinite"/></circle>')
    return "\n".join(out)


def synth_floor(w, horizon, bottom, vx, lines=14, rays=26):
    """Perspective grid that scrolls toward the viewer."""
    out = [f'<g stroke="{VIOLET}" stroke-width="1" mask="url(#floorFade)">']
    for i in range(rays + 1):
        out.append(f'<line x1="{vx}" y1="{horizon}" x2="{f(-w * 0.6 + i / rays * w * 2.2)}" y2="{bottom}"/>')
    pos = lambda k: horizon + (bottom - horizon) * (k / lines) ** 2.2
    for k in range(lines):
        y0, y1 = f(pos(k)), f(pos(k + 1))
        out.append(f'<line x1="0" x2="{w}" y1="{y0}" y2="{y0}">'
                   f'<animate attributeName="y1" values="{y0};{y1}" dur="1.4s" repeatCount="indefinite"/>'
                   f'<animate attributeName="y2" values="{y0};{y1}" dur="1.4s" repeatCount="indefinite"/></line>')
    out.append("</g>")
    return "\n".join(out)


def floor_defs(W, H, horizon):
    return f"""<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".35" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity=".9"/>
</linearGradient>
<mask id="floorFade"><rect y="{horizon}" width="{W}" height="{H - horizon}" fill="url(#fade)"/></mask>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>"""


# ---------------------------------------------------------------- hero
def hero():
    W, H, horizon = 1000, 420, 300
    gx, gy = 770, 175
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Yassir Hamri, Data and AI engineering student">
<defs>{COMMON_DEFS}
<radialGradient id="sky" cx=".72" cy=".42" r=".75">
  <stop offset="0" stop-color="#1b1145"/><stop offset=".55" stop-color="#0b0d2a"/><stop offset="1" stop-color="{BG}"/>
</radialGradient>
<linearGradient id="gGlobe" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
{floor_defs(W, H, horizon)}
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars(W, 90, horizon - 10)}
<circle cx="{gx}" cy="{gy}" r="120" fill="{VIOLET}" opacity=".35" filter="url(#bigGlow)"/>
<rect y="{horizon}" width="{W}" height="{H - horizon}" fill="#0a0620"/>
{synth_floor(W, horizon, H, gx)}
<line x1="0" x2="{W}" y1="{horizon}" y2="{horizon}" stroke="{PINK}" stroke-width="2" filter="url(#glow)"/>
<g transform="translate({gx} {gy}) rotate(-14)">
  <ellipse rx="185" ry="44" fill="none" stroke="{PINK}" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="6 10">
    <animate attributeName="stroke-dashoffset" values="0;-160" dur="6s" repeatCount="indefinite"/>
  </ellipse>
  <circle r="6" fill="{PINK}" filter="url(#glow)">
    <animateMotion dur="7s" repeatCount="indefinite" path="M185 0A185 44 0 1 1 -185 0A185 44 0 1 1 185 0"/>
  </circle>
</g>
{spinning_globe(gx, gy, 118)}
<ellipse cx="{gx}" cy="345" rx="110" ry="14" fill="{CYAN}" opacity=".18" filter="url(#bigGlow)"/>
<text x="60" y="88" font-family="{MONO}" font-size="15" fill="{TEAL}" letter-spacing="1">&gt; kudake, kyōka_suigetsu.py</text>
{extruded_text("YASSIR", 56, 165, 70, depth=10, spacing=3)}
{extruded_text("HAMRI", 56, 245, 70, depth=10, spacing=3)}
<text x="60" y="283" font-family="{FONT}" font-size="17" fill="{INK}" font-weight="700" letter-spacing=".5">Data &amp; AI Engineering · LLMs · RAG · MLOps · IoT</text>
<text x="60" y="398" font-family="{MONO}" font-size="13" fill="{MUTED}">ENSA Al Hoceima · class of 2027 · Morocco<tspan fill="{PINK}">
  <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/> █</tspan></text>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="{VIOLET}" stroke-opacity=".5" stroke-width="2"/>
</svg>"""
    write("hero.svg", svg)


# ---------------------------------------------------------------- section headers
def header(name, text, icon):
    W, H = 1000, 90
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(text)}">
<defs>{COMMON_DEFS}
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
</defs>
<image href="{fluent(icon)}" x="2" y="12" width="56" height="56"/>
{extruded_text(text, 72, 56, 36, depth=6, spacing=4)}
<rect x="74" y="72" width="600" height="3" rx="1.5" fill="url(#bar)">
  <animate attributeName="width" values="120;600;120" dur="6s" repeatCount="indefinite"/>
</rect>
</svg>"""
    write(name, svg)


# ---------------------------------------------------------------- about panel
ABOUT_PARAS = [
    "I'm Yassir, 22, from Morocco. I'm doing my engineering degree in AI at ENSA Al Hoceima and graduating in 2027. "
    "Everything is going according to plan.",
    "Most of my time goes into making LLMs actually useful: fine-tuning them, plugging them into real documents, "
    "and teaching them to say \"I don't know\" instead of casting Kyōka Suigetsu on you. "
    "When I get tired of GPUs, I go bother an ESP32.",
]
ABOUT_FACTS = [
    ("brain", "My RAG pipelines cite their sources. Unlike Aizen, they won't spend 100 years lying to you."),
    ("whale", "I've lost more nights to Docker networking than I'd like to admit. That part was not in the plan."),
    ("bug", "You say your bug is impossible to fix? Don't use such strong words. It makes you look weak."),
    ("tongue", "Arabic, French and English are at Bankai level. Chinese and German are still in Shikai."),
    ("tea", "Powered by Moroccan mint tea. Yes, way too much sugar."),
]


def about():
    W, X = 1000, 56
    parts = [extruded_text("YOKOSO, I'M YASSIR", X - 2, 82, 30, depth=5, spacing=3),
             f'<text x="{X}" y="112" font-family="{MONO}" font-size="14" fill="{TEAL}">// yōkoso, watashi no GitHub e · welcome to my GitHub</text>']
    y = 158
    for para in ABOUT_PARAS:
        for line in wrap(para, W - 2 * X, 17):
            parts.append(f'<text x="{X}" y="{y}" font-family="{FONT}" font-size="17" fill="{INK}">{esc(line)}</text>')
            y += 27
        y += 12
    parts.append(f'<line x1="{X}" x2="{W - X}" y1="{y - 6}" y2="{y - 6}" stroke="{VIOLET}" stroke-opacity=".35"/>')
    y += 22
    for i, (icon, text) in enumerate(ABOUT_FACTS):
        parts.append(f'<g class="row" style="animation-delay:{i * .15:.2f}s">'
                     f'<image href="{fluent(icon)}" x="{X}" y="{y - 22}" width="32" height="32"/>'
                     f'<text x="{X + 48}" y="{y}" font-family="{FONT}" font-size="16" fill="{INK}">{esc(text)}</text></g>')
        y += 46
    H = y + 6
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(' '.join(ABOUT_PARAS))}">
<defs>{COMMON_DEFS}</defs>
<style>
  .row {{ animation: slide .8s ease-out both; }}
  @keyframes slide {{ from {{ opacity: 0; transform: translateX(-14px) }} to {{ opacity: 1; transform: none }} }}
</style>
{panel(W, H)}
{"".join(parts)}
</svg>"""
    write("about.svg", svg)


# ---------------------------------------------------------------- isometric tech stack
STACK = [
    ("LANGUAGES", [("py", "Python"), ("java", "Java"), ("c", "C"), ("cpp", "C++"), ("js", "JavaScript"), ("ts", "TypeScript")]),
    ("AI + DATA", [("pytorch", "PyTorch"), ("sklearn", "scikit-learn"), ("postgres", "PostgreSQL"), ("mysql", "MySQL"), ("selenium", "Selenium")]),
    ("BACKEND", [("fastapi", "FastAPI"), ("spring", "Spring Boot"), ("rabbitmq", "RabbitMQ"), ("git", "Git"), ("linux", "Linux")]),
    ("CLOUD + OPS", [("docker", "Docker"), ("kubernetes", "Kubernetes"), ("terraform", "Terraform"), ("githubactions", "Actions"), ("aws", "AWS"), ("azure", "Azure")]),
]
ROW_COLORS = [(CYAN, "#0e7490"), (VIOLET, "#4c1d95"), (TEAL, "#115e59"), (PINK, "#9d174d")]


def cube(cx, ty, a, key, label, top, side, delay):
    """Isometric cube; ty = y of the top rhombus' left/right corners."""
    w, h = a * math.sqrt(3), a / 2
    L, R = cx - w / 2, cx + w / 2
    top_face = f"{f(cx)},{f(ty - h)} {f(R)},{f(ty)} {f(cx)},{f(ty + h)} {f(L)},{f(ty)}"
    left = f"{f(L)},{f(ty)} {f(cx)},{f(ty + h)} {f(cx)},{f(ty + h + a)} {f(L)},{f(ty + a)}"
    right = f"{f(cx)},{f(ty + h)} {f(R)},{f(ty)} {f(R)},{f(ty + a)} {f(cx)},{f(ty + h + a)}"
    ic = a * 0.84
    off = (a - ic) / 2
    m = f"matrix(0.866 0.5 0 1 {f(L)} {f(ty)})"   # icon square -> left face
    d = f"animation-delay:{delay:.2f}s"
    return f"""<g>
  <ellipse cx="{f(cx)}" cy="{f(ty + a + h + 14)}" rx="{f(w * .45)}" ry="7" fill="{top}" opacity=".25" class="shadow" style="{d}"/>
  <g class="lift" style="{d}">
    <polygon points="{left}" fill="#1e293b" stroke="{top}" stroke-opacity=".6"/>
    <image href="{icon_uri(key)}" width="{f(ic)}" height="{f(ic)}" x="{f(off)}" y="{f(off)}" transform="{m}"/>
    <polygon points="{right}" fill="{side}" stroke="{top}" stroke-opacity=".6"/>
    <polygon points="{top_face}" fill="{top}" fill-opacity=".9" stroke="#fff" stroke-opacity=".5"/>
    <polygon points="{top_face}" fill="url(#shine)"/>
  </g>
  <text x="{f(cx)}" y="{f(ty + a + h + 38)}" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="700" fill="{INK}">{label}</text>
</g>"""


def stack():
    W, a, row_h, step = 1000, 44, 150, 126
    last_cx = W - 40 - a * math.sqrt(3) / 2              # right margin = left margin (40)
    first_cx = last_cx - step * (max(len(r[1]) for r in STACK) - 1)
    H = 46 + row_h * len(STACK)
    parts = []
    for r, (title, items) in enumerate(STACK):
        top, side = ROW_COLORS[r]
        base = 74 + r * row_h
        mid = base + a / 2 + 4                           # vertical middle of the cube body
        parts.append(f'<text x="40" y="{f(mid)}" font-family="{DISPLAY}" font-size="14" font-weight="900" letter-spacing="2" fill="{top}">{title}</text>')
        parts.append(f'<rect x="40" y="{f(mid + 12)}" width="34" height="3" rx="1.5" fill="{top}"/>')
        for i, (key, label) in enumerate(items):
            parts.append(cube(first_cx + i * step, base, a, key, label, top, side, delay=r * 0.35 + i * 0.18))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Tech stack: {', '.join(l for _, items in STACK for _, l in items)}">
<defs>{COMMON_DEFS}
<linearGradient id="shine" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<style>
  .lift {{ animation: float 3.2s ease-in-out infinite; }}
  .shadow {{ animation: shrink 3.2s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes float {{ 0%,100% {{ transform: translateY(0) }} 50% {{ transform: translateY(-9px) }} }}
  @keyframes shrink {{ 0%,100% {{ transform: scale(1); opacity:.3 }} 50% {{ transform: scale(.7); opacity:.12 }} }}
</style>
{panel(W, H)}
{"".join(parts)}
</svg>"""
    write("stack.svg", svg)


# ---------------------------------------------------------------- project cards
PROJECTS = [
    ("dhakira", "books", "Dhakira", "built at UM6P · summer 2026",
     "Ask it anything about your company docs. It answers with sources. No sources, no answer, no illusions.",
     ["FastAPI", "Spring Boot", "pgvector", "RabbitMQ"], CYAN),
    ("medical", "stethoscope", "Medical Bot", "Qwen2.5-7B · 4-bit QLoRA",
     "I fine-tuned a 7B model on 125k medical chats. My GPU still hasn't forgiven me.",
     ["PyTorch", "QLoRA", "FAISS", "Docker"], PINK),
    ("jobs", "briefcase", "Job Intelligent", "scrape → clean → match",
     "I scraped job boards so I'd never have to scroll them again. Now it matches people to offers too.",
     ["Selenium", "PostgreSQL", "Power BI"], VIOLET),
    ("iot", "antenna", "IoT Sensor", "ESP32 → MQTT → Azure",
     "A tiny ESP32 that snitches to Azure every time something moves. Live demo inside.",
     ["C++", "ESP32", "MQTT", "Azure"], TEAL),
    ("pfe", "gradcap", "gestion-PFE", "Java EE scheduler",
     "Final-year project scheduling at my school was pure chaos. Now an app runs it. All according to plan.",
     ["Java EE", "MySQL", "LangChain4j"], "#fbbf24"),
    ("spam", "fishing", "Phish Catcher", "Random Forest + SVM",
     "Catches 97% of spam and phishing emails. The other 3% are probably from my bank.",
     ["scikit-learn", "FastAPI", "Docker"], "#34d399"),
]


def card(key, icon, title, sub, blurb, tags, color):
    W, H = 480, 250
    cw, ch, d, tilt = 420, 180, 14, 14      # face size, extrusion depth, slant of the top edge
    x0, y0 = 22, 20
    face = f"M{x0} {y0 + tilt}L{x0 + cw} {y0}L{x0 + cw} {y0 + ch}L{x0} {y0 + ch + tilt}Z"
    side = f"M{x0 + cw} {y0}L{x0 + cw + d} {y0 + d}L{x0 + cw + d} {y0 + ch + d}L{x0 + cw} {y0 + ch}Z"
    bottom = f"M{x0} {y0 + ch + tilt}L{x0 + cw} {y0 + ch}L{x0 + cw + d} {y0 + ch + d}L{x0 + d} {y0 + ch + tilt + d}Z"
    skew = f"matrix(1 {-tilt / cw:.4f} 0 1 {x0} {y0 + tilt})"   # content follows the slanted face
    pad = 26
    lines = wrap(blurb, cw - 2 * pad, 14)
    assert len(lines) <= 3, (title, lines)
    ty = 92 + (len(lines) - 1) * 20 + 16       # tags sit right under the last text line
    tag_svg, tx = [], pad
    for t in tags:
        tw = 16 + len(t) * 7.3
        tag_svg.append(f'<rect x="{f(tx)}" y="{ty}" width="{f(tw)}" height="24" rx="12" fill="{color}" fill-opacity=".15" stroke="{color}" stroke-opacity=".7"/>'
                       f'<text x="{f(tx + tw / 2)}" y="{ty + 16}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{color}">{esc(t)}</text>')
        tx += tw + 8
    body = "".join(f'<tspan x="{pad}" y="{92 + i * 20}">{esc(l)}</tspan>' for i, l in enumerate(lines))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)}: {esc(blurb)}">
<defs>
<linearGradient id="face" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1e1b4b"/><stop offset="1" stop-color="#0b1023"/></linearGradient>
<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".12"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<clipPath id="clipFace"><path d="{face}"/></clipPath>
<filter id="soft" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
</defs>
<style>
  .card {{ animation: bob 4s ease-in-out infinite; }}
  @keyframes bob {{ 0%,100% {{ transform: translateY(0) }} 50% {{ transform: translateY(-5px) }} }}
</style>
<ellipse cx="{x0 + (cw + d) / 2}" cy="{H - 14}" rx="200" ry="10" fill="{color}" opacity=".35" filter="url(#soft)"/>
<g class="card">
  <path d="{bottom}" fill="{color}" fill-opacity=".35"/>
  <path d="{side}" fill="{color}" fill-opacity=".55"/>
  <path d="{face}" fill="url(#face)" stroke="{color}" stroke-width="2"/>
  <g clip-path="url(#clipFace)">
    <rect x="-200" y="0" width="160" height="{H}" fill="url(#sweep)" transform="skewX(-20)">
      <animate attributeName="x" values="-200;700" dur="4.5s" repeatCount="indefinite"/>
    </rect>
  </g>
  <g transform="{skew}">
    <image href="{fluent(icon)}" x="{pad - 2}" y="16" width="44" height="44"/>
    <text x="{pad + 54}" y="38" font-family="{DISPLAY}" font-size="19" font-weight="900" letter-spacing="1" fill="#f8fafc">{esc(title)}</text>
    <text x="{pad + 54}" y="57" font-family="{MONO}" font-size="12" fill="{color}">{esc(sub)}</text>
    <text font-family="{FONT}" font-size="14" fill="#cbd5e1">{body}</text>
    {"".join(tag_svg)}
  </g>
</g>
</svg>"""
    write(f"card-{key}.svg", svg)


# ---------------------------------------------------------------- master plan (currently cooking)
PLAN = [
    ("satellite", "ORION", "phase 1 · research", CYAN,
     "My research playground. Vision models, time series and knowledge graphs glued together with LangGraph "
     "agents, so they can reason about factory sensors and images at the same time."),
    ("robot", "SENTINEL", "phase 2 · MLOps", PINK,
     "MLOps on AWS/EKS that deploys models, watches them for drift and rolls back on its own. "
     "Infrastructure that doesn't need me awake. That's the plan."),
]
RECEIPTS = ["Global UGRAD semi-finalist (2023–24)", "Oracle OCI AI Foundations certified",
            "IBM courses: Istio & Kubernetes (×2)", "n8n + Canva pipeline: 90% less manual work"]


def plan():
    W, gap, m = 1000, 24, 30
    cw = (W - 2 * m - gap) / 2
    parts, card_h = [], 200
    for i, (icon, name, phase, color, text) in enumerate(PLAN):
        x = m + i * (cw + gap)
        parts.append(f'<rect x="{f(x)}" y="{m}" width="{f(cw)}" height="{card_h}" rx="16" fill="#0b1023" stroke="{color}" stroke-opacity=".7" stroke-width="1.5"/>')
        parts.append(f'<rect x="{f(x)}" y="{m}" width="5" height="{card_h}" rx="2.5" fill="{color}"/>')
        parts.append(f'<image href="{fluent(icon)}" x="{f(x + 24)}" y="{m + 22}" width="46" height="46"/>')
        parts.append(f'<text x="{f(x + 84)}" y="{m + 47}" font-family="{DISPLAY}" font-size="22" font-weight="900" letter-spacing="2" fill="#f8fafc">{name}</text>')
        parts.append(f'<text x="{f(x + 84)}" y="{m + 66}" font-family="{MONO}" font-size="12" fill="{color}">{esc(phase)}</text>')
        for j, line in enumerate(wrap(text, cw - 48, 15)[:4]):
            parts.append(f'<text x="{f(x + 24)}" y="{m + 104 + j * 23}" font-family="{FONT}" font-size="15" fill="#cbd5e1">{esc(line)}</text>')
    ry = m + card_h + gap
    rh = 120
    parts.append(f'<rect x="{m}" y="{ry}" width="{W - 2 * m}" height="{rh}" rx="16" fill="#0b1023" stroke="#fbbf24" stroke-opacity=".6" stroke-width="1.5"/>')
    parts.append(f'<image href="{fluent("trophy")}" x="{m + 22}" y="{ry + 18}" width="40" height="40"/>')
    parts.append(f'<text x="{m + 76}" y="{ry + 46}" font-family="{DISPLAY}" font-size="17" font-weight="900" letter-spacing="2" fill="#fbbf24">PROOF I DON\'T JUST TALK</text>')
    colw = (W - 2 * m - 48) / 2
    for k, item in enumerate(RECEIPTS):
        cx = m + 24 + (k % 2) * colw
        cy = ry + 82 + (k // 2) * 26
        parts.append(f'<circle cx="{f(cx + 4)}" cy="{cy - 5}" r="4" fill="#fbbf24"/>'
                     f'<text x="{f(cx + 18)}" y="{cy}" font-family="{FONT}" font-size="15" fill="{INK}">{esc(item)}</text>')
    H = ry + rh + m
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Current projects: ORION and Sentinel. {esc('. '.join(RECEIPTS))}">
<defs>{COMMON_DEFS}</defs>
{panel(W, H)}
{"".join(parts)}
</svg>"""
    write("plan.svg", svg)


# ---------------------------------------------------------------- footer
def footer():
    W, H, horizon = 1000, 210, 100
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="All according to plan. Thanks for scrolling">
<defs>{COMMON_DEFS}
{floor_defs(W, H, horizon)}
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="{BG}"/>
{stars(W, 40, horizon - 5)}
<rect y="{horizon}" width="{W}" height="{H - horizon}" fill="#0a0620"/>
{synth_floor(W, horizon, H, 500, lines=10)}
<line x1="0" x2="{W}" y1="{horizon}" y2="{horizon}" stroke="{PINK}" stroke-width="2" filter="url(#glow)"/>
{extruded_text("ALL ACCORDING TO PLAN", 500, 54, 32, depth=6, anchor="middle", spacing=4)}
<text x="500" y="84" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{MUTED}">thanks for scrolling. you were under Kyōka Suigetsu the whole time.</text>
</g>
</svg>"""
    write("footer.svg", svg)


# ---------------------------------------------------------------- 3D contribution city
CONTRIB_QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{contributionCount weekday}}}}}}"""


def fetch_contrib(login="yassirHam"):
    """Pull the last year of contributions through the gh CLI (no token handling here)."""
    import json
    import subprocess
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={CONTRIB_QUERY}", "-f", f"login={login}"],
                         capture_output=True, text=True, check=True).stdout
    cal = json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], [[(d["weekday"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]


def contrib_city():
    total, weeks = fetch_contrib()
    peak = max((c for w in weeks for _, c in w), default=1) or 1
    W, H = 1000, 590
    a = 14
    cx30, s30 = a * 0.866, a * 0.5
    span = (len(weeks) + 7) * cx30                 # isometric footprint width
    ox, oy = (W - span) / 2, 150                   # centred horizontally
    palette = ["#1e293b", "#0e7490", CYAN, "#a78bfa", PINK]
    level = lambda c: 0 if c == 0 else min(4, 1 + int(4 * c / (peak + 1)))
    cells = sorted(((wi, d, c) for wi, w in enumerate(weeks) for d, c in w), key=lambda t: (t[0] + t[1], t[0]))
    bars = []
    for wi, d, c in cells:
        x = ox + (wi - d) * cx30 + 7 * cx30        # weeks run down-right, weekdays down-left
        y = oy + (wi + d) * s30
        h = 2 if c == 0 else 6 + 70 * (c / peak) ** .8
        col = palette[level(c)]
        top = f"{f(x)},{f(y - h)} {f(x + cx30)},{f(y - h + s30)} {f(x)},{f(y - h + 2 * s30)} {f(x - cx30)},{f(y - h + s30)}"
        left = f"{f(x - cx30)},{f(y - h + s30)} {f(x)},{f(y - h + 2 * s30)} {f(x)},{f(y + 2 * s30)} {f(x - cx30)},{f(y + s30)}"
        right = f"{f(x)},{f(y - h + 2 * s30)} {f(x + cx30)},{f(y - h + s30)} {f(x + cx30)},{f(y + s30)} {f(x)},{f(y + 2 * s30)}"
        bars.append(f'<g class="b" style="animation-delay:{(wi + d) * 0.025:.2f}s">'
                    f'<polygon points="{left}" fill="{col}" fill-opacity=".55"/>'
                    f'<polygon points="{right}" fill="{col}" fill-opacity=".8"/>'
                    f'<polygon points="{top}" fill="{col}" stroke="#fff" stroke-opacity="{.35 if c else .06}" stroke-width=".5"/></g>')
    active = sum(1 for w in weeks for _, c in w if c)
    best = max((c for w in weeks for _, c in w), default=0)
    stat = lambda x, anchor, y, val, label, col: (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{DISPLAY}" font-size="30" font-weight="900" fill="{col}">{val}</text>'
        f'<text x="{x}" y="{y + 22}" text-anchor="{anchor}" font-family="{FONT}" font-size="12" font-weight="700" letter-spacing="2" fill="{MUTED}">{label}</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="3D contribution graph: {total} contributions in the last year">
<defs>{COMMON_DEFS}</defs>
<style>
  .b {{ transform-box: fill-box; transform-origin: 50% 100%; animation: rise 1.2s cubic-bezier(.2,.9,.3,1.2) both; }}
  @keyframes rise {{ from {{ transform: scaleY(0); opacity: 0 }} to {{ transform: scaleY(1); opacity: 1 }} }}
</style>
{panel(W, H)}
{stars(W, 40, 110)}
{"".join(bars)}
{stat(40, "start", 58, total, "CONTRIBUTIONS · LAST 12 MONTHS", CYAN)}
{stat(W / 2, "middle", 58, active, "ACTIVE DAYS", "#a78bfa")}
{stat(W - 40, "end", 58, best, "BEST DAY", PINK)}
</svg>"""
    write("contrib-city.svg", svg)


if __name__ == "__main__":
    hero()
    about()
    header("h-about.svg", "WHO AM I", "technologist")
    header("h-stack.svg", "MY STACK", "toolbox")
    header("h-projects.svg", "STUFF I SHIPPED", "hammer")
    header("h-cooking.svg", "THE MASTER PLAN", "cooking")
    header("h-contrib.svg", "COMMIT CITY", "city")
    stack()
    for p in PROJECTS:
        card(*p)
    plan()
    footer()
    contrib_city()
