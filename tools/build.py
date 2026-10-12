"""Generates the 3D SVG artwork used in the profile README.

Run from the repo root:  python tools/build.py
Everything is plain SVG + SMIL/CSS animation, so it renders inside GitHub's <img> sandbox.
"""
import base64
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"

BG = "#060816"
CYAN = "#22d3ee"
TEAL = "#2dd4bf"
VIOLET = "#8b5cf6"
PINK = "#f472b6"
FONT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'Cascadia Code', Consolas, 'Courier New', monospace"

random.seed(7)


def f(v):
    """Compact number formatting."""
    return f"{v:.1f}".rstrip("0").rstrip(".")


def write(name, svg):
    (ASSETS / name).write_text(svg, encoding="utf-8")
    print(f"{name}: {len(svg.encode()) / 1024:.0f} KB")


def extruded_text(text, x, y, size, depth=9, anchor="start", grad="gTxt", side="#3b1d6e", weight=900, spacing=2):
    """Fake 3D extrusion: stacked copies offset down-right, then a bright face on top."""
    common = f'x="{x}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}" text-anchor="{anchor}"'
    layers = []
    for i in range(depth, 0, -1):
        shade = side if i > 1 else "#1e0b3d"
        layers.append(f'<text {common} y="{y}" dx="{i}" dy="{i}" fill="{shade}">{text}</text>')
    layers.append(f'<text {common} y="{y}" fill="url(#{grad})" stroke="#ffffff" stroke-opacity=".25" stroke-width="1">{text}</text>')
    return "\n".join(layers)


TEXT_GRADIENT = f"""
<linearGradient id="gTxt" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CYAN}"/>
  <stop offset=".5" stop-color="#a78bfa"/>
  <stop offset="1" stop-color="{PINK}"/>
  <animate attributeName="x1" values="0;-1;0" dur="8s" repeatCount="indefinite"/>
  <animate attributeName="x2" values="1;2;1" dur="8s" repeatCount="indefinite"/>
</linearGradient>"""


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
    per_frame = []
    for i in range(frames + 1):
        a = 2 * math.pi * i / frames
        per_frame.append([project(v, a, tilt, cx, cy, r) for v in verts])
    # wireframe as one animated path
    ds = []
    for pts in per_frame:
        ds.append("".join(f"M{f(pts[a][0])} {f(pts[a][1])}L{f(pts[b][0])} {f(pts[b][1])}" for a, b in edges))
    out = [f'<path fill="none" stroke="url(#gGlobe)" stroke-width="1.1" stroke-opacity=".75" d="{ds[0]}">'
           f'<animate attributeName="d" dur="{dur}s" repeatCount="indefinite" values="{";".join(ds)}"/></path>']
    # vertices: size + opacity follow depth, so the front glows and the back fades
    for vi in range(len(verts)):
        xs = ";".join(f(p[vi][0]) for p in per_frame)
        ys = ";".join(f(p[vi][1]) for p in per_frame)
        rs = ";".join(f(1.3 + 1.6 * (p[vi][2] + 1)) for p in per_frame)
        ops = ";".join(f"{0.15 + 0.85 * (p[vi][2] + 1) / 2:.2f}" for p in per_frame)
        col = PINK if vi % 7 == 0 else CYAN
        out.append(f'<circle fill="{col}" filter="url(#glow)">'
                   f'<animate attributeName="cx" dur="{dur}s" repeatCount="indefinite" values="{xs}"/>'
                   f'<animate attributeName="cy" dur="{dur}s" repeatCount="indefinite" values="{ys}"/>'
                   f'<animate attributeName="r" dur="{dur}s" repeatCount="indefinite" values="{rs}"/>'
                   f'<animate attributeName="opacity" dur="{dur}s" repeatCount="indefinite" values="{ops}"/></circle>')
    return "\n".join(out)


def stars(w, h, n, max_y=None):
    out = []
    for _ in range(n):
        x, y = random.uniform(0, w), random.uniform(0, max_y or h)
        r = random.choice([0.5, 0.7, 0.9, 1.2])
        d = random.uniform(2, 6)
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="#fff">'
                   f'<animate attributeName="opacity" values=".1;.9;.1" dur="{f(d)}s" begin="{f(random.uniform(0, d))}s" repeatCount="indefinite"/></circle>')
    return "\n".join(out)


def synth_floor(w, horizon, bottom, vx, lines=14, rays=26):
    """Perspective grid that scrolls toward the viewer."""
    out = [f'<g stroke="{VIOLET}" stroke-width="1" mask="url(#floorFade)">']
    for i in range(rays + 1):
        t = i / rays
        xb = -w * 0.6 + t * w * 2.2
        out.append(f'<line x1="{vx}" y1="{horizon}" x2="{f(xb)}" y2="{bottom}"/>')
    depth = bottom - horizon
    pos = lambda k: horizon + depth * (k / lines) ** 2.2
    for k in range(lines):
        y0, y1 = pos(k), pos(k + 1)
        out.append(f'<line x1="0" x2="{w}" y1="{f(y0)}" y2="{f(y0)}">'
                   f'<animate attributeName="y1" values="{f(y0)};{f(y1)}" dur="1.4s" repeatCount="indefinite"/>'
                   f'<animate attributeName="y2" values="{f(y0)};{f(y1)}" dur="1.4s" repeatCount="indefinite"/></line>')
    out.append("</g>")
    return "\n".join(out)


COMMON_DEFS = f"""
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="bigGlow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="18"/></filter>
{TEXT_GRADIENT}"""


# ---------------------------------------------------------------- hero
def hero():
    W, H = 1000, 420
    horizon = 300
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Yassir Hamri, Data and AI engineering student">
<defs>
{COMMON_DEFS}
<radialGradient id="sky" cx=".72" cy=".42" r=".75">
  <stop offset="0" stop-color="#1b1145"/><stop offset=".55" stop-color="#0b0d2a"/><stop offset="1" stop-color="{BG}"/>
</radialGradient>
<linearGradient id="gGlobe" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/>
</linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".35" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity=".9"/>
</linearGradient>
<mask id="floorFade"><rect y="{horizon}" width="{W}" height="{H - horizon}" fill="url(#fade)"/></mask>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars(W, H, 90, horizon - 10)}
<circle cx="770" cy="180" r="120" fill="{VIOLET}" opacity=".35" filter="url(#bigGlow)"/>
<rect y="{horizon}" width="{W}" height="{H - horizon}" fill="#0a0620"/>
{synth_floor(W, horizon, H, 770)}
<line x1="0" x2="{W}" y1="{horizon}" y2="{horizon}" stroke="{PINK}" stroke-width="2" filter="url(#glow)"/>

<!-- orbit ring behind + in front of the globe -->
<g transform="translate(770 180) rotate(-14)">
  <ellipse rx="185" ry="44" fill="none" stroke="{PINK}" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="6 10">
    <animate attributeName="stroke-dashoffset" values="0;-160" dur="6s" repeatCount="indefinite"/>
  </ellipse>
  <circle r="6" fill="{PINK}" filter="url(#glow)">
    <animateMotion dur="7s" repeatCount="indefinite" path="M185 0A185 44 0 1 1 -185 0A185 44 0 1 1 185 0"/>
  </circle>
</g>
{spinning_globe(770, 180, 118)}

<!-- shadow of the globe on the floor -->
<ellipse cx="770" cy="345" rx="110" ry="14" fill="{CYAN}" opacity=".18" filter="url(#bigGlow)"/>

<g>
  <text x="60" y="92" font-family="{MONO}" font-size="16" fill="{TEAL}" letter-spacing="3">&gt; hello_world.py</text>
  {extruded_text("YASSIR", 56, 168, 78, depth=10)}
  {extruded_text("HAMRI", 56, 248, 78, depth=10)}
  <text x="60" y="284" font-family="{FONT}" font-size="17" fill="#e2e8f0" font-weight="600">Data &amp; AI Engineering Â· LLMs Â· RAG Â· MLOps Â· IoT</text>
</g>
<text x="60" y="400" font-family="{MONO}" font-size="13" fill="#94a3b8">ENSA Al Hoceima Â· class of 2027 Â· Morocco<tspan fill="{PINK}">
  <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/> â–ˆ</tspan></text>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="{VIOLET}" stroke-opacity=".5" stroke-width="2"/>
</svg>"""
    write("hero.svg", svg)


# ---------------------------------------------------------------- section headers
def header(name, text, emoji):
    W, H = 1000, 90
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{text}">
<defs>{COMMON_DEFS}
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
</defs>
<text x="8" y="60" font-size="40">{emoji}</text>
{extruded_text(text, 70, 60, 42, depth=6, spacing=4)}
<rect x="72" y="74" width="600" height="3" rx="1.5" fill="url(#bar)">
  <animate attributeName="width" values="120;600;120" dur="6s" repeatCount="indefinite"/>
</rect>
</svg>"""
    write(name, svg)


# ---------------------------------------------------------------- isometric tech stack
def icon_uri(key):
    data = (ICONS / f"{key}.svg").read_bytes()
    return "data:image/svg+xml;base64," + base64.b64encode(data).decode()


STACK = [
    ("LANGUAGES", [("py", "Python"), ("java", "Java"), ("c", "C"), ("cpp", "C++"), ("js", "JavaScript"), ("ts", "TypeScript")]),
    ("AI Â· DATA", [("pytorch", "PyTorch"), ("sklearn", "scikit-learn"), ("postgres", "PostgreSQL"), ("mysql", "MySQL"), ("selenium", "Selenium")]),
    ("BACKEND", [("fastapi", "FastAPI"), ("spring", "Spring Boot"), ("rabbitmq", "RabbitMQ"), ("git", "Git"), ("linux", "Linux")]),
    ("CLOUD Â· OPS", [("docker", "Docker"), ("kubernetes", "Kubernetes"), ("terraform", "Terraform"), ("githubactions", "Actions"), ("aws", "AWS"), ("azure", "Azure")]),
]
ROW_COLORS = [(CYAN, "#0e7490"), (VIOLET, "#4c1d95"), (TEAL, "#115e59"), (PINK, "#9d174d")]


def cube(cx, ty, a, key, label, top, side, delay):
    """Isometric cube; ty = y of the top rhombus' left/right corners."""
    w, h = a * math.sqrt(3), a / 2          # rhombus width / half height
    L, R = cx - w / 2, cx + w / 2
    top_face = f"{f(cx)},{f(ty - h)} {f(R)},{f(ty)} {f(cx)},{f(ty + h)} {f(L)},{f(ty)}"
    left = f"{f(L)},{f(ty)} {f(cx)},{f(ty + h)} {f(cx)},{f(ty + h + a)} {f(L)},{f(ty + a)}"
    right = f"{f(cx)},{f(ty + h)} {f(R)},{f(ty)} {f(R)},{f(ty + a)} {f(cx)},{f(ty + h + a)}"
    ic = a * 0.84
    off = (a - ic) / 2
    # map icon square onto the left face: x-axis (cos30, sin30), y-axis (0, 1)
    m = f"matrix(0.866 0.5 0 1 {f(L)} {f(ty)})"
    return f"""<g class="cube" style="animation-delay:{delay:.2f}s">
  <ellipse cx="{f(cx)}" cy="{f(ty + a + h + 14)}" rx="{f(w * .45)}" ry="7" fill="{top}" opacity=".25" class="shadow" style="animation-delay:{delay:.2f}s"/>
  <g class="lift" style="animation-delay:{delay:.2f}s">
    <polygon points="{left}" fill="#1e293b" stroke="{top}" stroke-opacity=".6"/>
    <image href="{icon_uri(key)}" width="{f(ic)}" height="{f(ic)}" x="{f(off)}" y="{f(off)}" transform="{m}"/>
    <polygon points="{right}" fill="{side}" stroke="{top}" stroke-opacity=".6"/>
    <polygon points="{top_face}" fill="{top}" fill-opacity=".9" stroke="#fff" stroke-opacity=".5"/>
    <polygon points="{top_face}" fill="url(#shine)"/>
  </g>
  <text x="{f(cx)}" y="{f(ty + a + h + 36)}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" fill="#e2e8f0">{label}</text>
</g>"""


def stack():
    W = 1000
    a = 44
    row_h = 150
    H = 40 + row_h * len(STACK)
    parts = []
    for r, (title, items) in enumerate(STACK):
        top, side = ROW_COLORS[r]
        base = 70 + r * row_h
        parts.append(f'<text x="24" y="{base + 44}" font-family="{FONT}" font-size="15" font-weight="900" letter-spacing="3" fill="{top}">{title}</text>')
        parts.append(f'<line x1="24" x2="150" y1="{base + 56}" y2="{base + 56}" stroke="{top}" stroke-opacity=".5"/>')
        for i, (key, label) in enumerate(items):
            parts.append(cube(225 + i * 128, base, a, key, label, top, side, delay=(r * 0.35 + i * 0.18)))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Tech stack: Python, Java, C, C++, JavaScript, TypeScript, PyTorch, scikit-learn, PostgreSQL, MySQL, Selenium, FastAPI, Spring Boot, RabbitMQ, Git, Linux, Docker, Kubernetes, Terraform, GitHub Actions, AWS, Azure">
<defs>
<linearGradient id="shine" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<radialGradient id="bgS" cx=".5" cy=".5" r=".7"><stop offset="0" stop-color="#140f35"/><stop offset="1" stop-color="{BG}"/></radialGradient>
</defs>
<style>
  .lift {{ animation: float 3.2s ease-in-out infinite; }}
  .shadow {{ animation: shrink 3.2s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes float {{ 0%,100% {{ transform: translateY(0) }} 50% {{ transform: translateY(-9px) }} }}
  @keyframes shrink {{ 0%,100% {{ transform: scale(1); opacity:.3 }} 50% {{ transform: scale(.7); opacity:.12 }} }}
</style>
<rect width="{W}" height="{H}" rx="22" fill="url(#bgS)"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="{VIOLET}" stroke-opacity=".4" stroke-width="2"/>
{"".join(parts)}
</svg>"""
    write("stack.svg", svg)


# ---------------------------------------------------------------- project cards
PROJECTS = [
    ("dhakira", "ðŸ›ï¸", "Dhakira", "UM6P internship Â· 2026",
     ["Company knowledge base that answers with", "citations, and says no when the docs don't."],
     ["FastAPI", "Spring Boot", "pgvector", "RabbitMQ"], CYAN),
    ("medical", "ðŸ©º", "Medical Chatbot", "Qwen2.5-7B Â· 4-bit QLoRA",
     ["125k+ dialogues, FAISS-grounded answers,", "under 500 ms on a very tired GPU."],
     ["PyTorch", "QLoRA", "FAISS", "Docker"], PINK),
    ("jobs", "ðŸ’¼", "Job Intelligent", "scrape â†’ clean â†’ match",
     ["Scrapes job portals, dedupes everything and", "matches candidates with embeddings."],
     ["Selenium", "PostgreSQL", "Power BI"], VIOLET),
    ("iot", "ðŸ“¡", "IoT Motion Sensor", "ESP32 â†’ MQTT â†’ Azure",
     ["A tiny board spots motion and pings the", "cloud. Live dashboard included."],
     ["C++", "ESP32", "MQTT", "Azure"], TEAL),
    ("pfe", "ðŸŽ“", "gestion-PFE", "Java EE scheduler",
     ["Assigns projects, juries and defense slots.", "About 70% less admin back-and-forth."],
     ["Java EE", "MySQL", "LangChain4j"], "#fbbf24"),
    ("spam", "ðŸ›¡ï¸", "Phishing Detector", "Random Forest + SVM",
     ["Sniffs out spam and phishing emails with", "97%+ accuracy on held-out data."],
     ["scikit-learn", "FastAPI", "Docker"], "#34d399"),
]


def card(key, emoji, title, sub, lines, tags, color):
    W, H = 480, 250
    cw, ch, d = 420, 175, 14   # face size + extrusion depth
    x0, y0 = 22, 22
    # skewed face gives the "tilted slab" look; extrusion drawn as the side + bottom faces
    face = f"M{x0} {y0 + 14}L{x0 + cw} {y0}L{x0 + cw} {y0 + ch}L{x0} {y0 + ch + 14}Z"
    side = f"M{x0 + cw} {y0}L{x0 + cw + d} {y0 + d}L{x0 + cw + d} {y0 + ch + d}L{x0 + cw} {y0 + ch}Z"
    bottom = f"M{x0} {y0 + ch + 14}L{x0 + cw} {y0 + ch}L{x0 + cw + d} {y0 + ch + d}L{x0 + d} {y0 + ch + 14 + d}Z"
    skew = f"matrix(1 {-14 / cw:.4f} 0 1 {x0} {y0 + 14})"   # same slope as the face's top edge
    tx = 30
    tag_svg, cx = [], tx
    for t in tags:
        tw = 14 + len(t) * 7.4
        tag_svg.append(f'<rect x="{f(cx)}" y="128" width="{f(tw)}" height="24" rx="12" fill="{color}" fill-opacity=".15" stroke="{color}" stroke-opacity=".7"/>'
                       f'<text x="{f(cx + tw / 2)}" y="144.5" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{color}">{t}</text>')
        cx += tw + 8
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}: {' '.join(lines)}">
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
<ellipse cx="{x0 + cw / 2 + 10}" cy="{H - 14}" rx="200" ry="10" fill="{color}" opacity=".35" filter="url(#soft)"/>
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
    <text x="{tx}" y="48" font-size="30">{emoji}</text>
    <text x="{tx + 46}" y="40" font-family="{FONT}" font-size="22" font-weight="900" fill="#f8fafc">{title}</text>
    <text x="{tx + 46}" y="58" font-family="{MONO}" font-size="12" fill="{color}">{sub}</text>
    <text font-family="{FONT}" font-size="14" fill="#cbd5e1"><tspan x="{tx}" y="90">{lines[0]}</tspan><tspan x="{tx}" y="110">{lines[1]}</tspan></text>
    {"".join(tag_svg)}
  </g>
</g>
</svg>"""
    write(f"card-{key}.svg", svg)


# ---------------------------------------------------------------- footer
def footer():
    W, H = 1000, 200
    horizon = 70
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Thanks for stopping by">
<defs>{COMMON_DEFS}
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".4" stop-color="#fff" stop-opacity=".6"/><stop offset="1" stop-color="#fff" stop-opacity="1"/>
</linearGradient>
<mask id="floorFade"><rect y="{horizon}" width="{W}" height="{H - horizon}" fill="url(#fade)"/></mask>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="{BG}"/>
{stars(W, H, 40, horizon - 5)}
<rect y="{horizon}" width="{W}" height="{H - horizon}" fill="#0a0620"/>
{synth_floor(W, horizon, H, 500, lines=10)}
<line x1="0" x2="{W}" y1="{horizon}" y2="{horizon}" stroke="{PINK}" stroke-width="2" filter="url(#glow)"/>
{extruded_text("THANKS FOR SCROLLING", 500, 55, 34, depth=6, anchor="middle", spacing=5)}
</g>
</svg>"""
    write("footer.svg", svg)


if __name__ == "__main__":
    hero()
    header("h-about.svg", "WHO AM I", "ðŸ‘¾")
    header("h-stack.svg", "TOOLBOX", "ðŸ§°")
    header("h-projects.svg", "THINGS I BUILT", "ðŸš€")
    header("h-cooking.svg", "CURRENTLY COOKING", "ðŸ”¥")
    header("h-contrib.svg", "COMMIT CITY", "ðŸ™ï¸")
    stack()
    for p in PROJECTS:
        card(*p)
    footer()
