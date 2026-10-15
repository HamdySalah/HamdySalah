"""Generate the animated SVG assets for the GitHub profile README (SMIL only, no scripts).

Usage: python scripts/gen_assets.py assets
Writes hero.svg, capabilities.svg and footer.svg into the given directory.
"""
import math
import os
import random
import sys
from xml.sax.saxutils import escape

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "assets"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"

C = {
    "white": "#f8fafc", "text": "#e2e8f0", "body": "#8b949e", "dim": "#484f58",
    "blue": "#3b82f6", "sky": "#60a5fa", "ice": "#93c5fd", "violet": "#8b5cf6", "lilac": "#a78bfa",
    "cyan": "#22d3ee", "green": "#22c55e", "card": "#0d1117", "edge": "#30363d",
}

ACCENT_STOPS = (
    '<stop offset="0" stop-color="#3b82f6"/><stop offset="0.33" stop-color="#8b5cf6"/>'
    '<stop offset="0.66" stop-color="#06b6d4"/><stop offset="1" stop-color="#3b82f6"/>'
)
EASE_OUT = "0 0 1 1;0.16 1 0.3 1"
EASE_IN_OUT3 = "0.45 0 0.55 1;0.45 0 0.55 1;0.45 0 0.55 1"


def n(x):
    """Compact number formatting for SVG attributes."""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def mono(x, y, s, fill, cw, weight=None):
    """Monospace text with every space-free token pinned to an exact column (identical spacing in any font)."""
    w = f' font-weight="{weight}"' if weight else ""
    parts, i = [], 0
    while i < len(s):
        if s[i] == " ":
            i += 1
            continue
        j = i
        while j < len(s) and s[j] != " ":
            j += 1
        tok = s[i:j]
        tl = f' textLength="{n(len(tok) * cw)}" lengthAdjust="spacingAndGlyphs"' if len(tok) > 1 else ""
        parts.append(f'<text x="{n(x + i * cw)}" y="{n(y)}" fill="{fill}"{w}{tl}>{escape(tok)}</text>')
        i = j
    return "".join(parts)


def enter(delay, dur=0.8, rise=12):
    """Fade + rise on load. Runs from t=0 so the element is hidden until `delay`, but stays visible without SMIL."""
    end = delay + dur
    k = f"{delay / end:.3f}"
    return (
        f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k};1" dur="{n(end)}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0 {rise};0 {rise};0 0" keyTimes="0;{k};1" '
        f'calcMode="spline" keySplines="{EASE_OUT}" dur="{n(end)}s" fill="freeze"/>'
    )


def orbit_path(r, deg):
    """Closed circle path around the origin, starting at `deg` (so orbiting items can be phase-shifted)."""
    a = math.radians(deg)
    x, y = r * math.cos(a), r * math.sin(a)
    return f"M{n(x)},{n(y)} A{r},{r} 0 1 1 {n(-x)},{n(-y)} A{r},{r} 0 1 1 {n(x)},{n(y)}"


def shine(gid, width, dur):
    return (
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{width}" y2="0" spreadMethod="repeat">'
        f'{ACCENT_STOPS}<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{width} 0" '
        f'dur="{dur}s" repeatCount="indefinite"/></linearGradient>'
    )


def glow(gid, color, opacity):
    return (
        f'<radialGradient id="{gid}"><stop offset="0" stop-color="{color}" stop-opacity="{opacity}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
    )


def document(w, h, label, defs, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">\n'
        f"<title>{escape(label)}</title>\n<defs>\n" + "\n".join(defs) + "\n</defs>\n" + "\n".join(body) + "\n</svg>\n"
    )


def write(name, svg):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print(f"wrote {path} ({len(svg) / 1024:.1f} KB)")


# ── hero ────────────────────────────────────────────────────────────────────────

HERO_PHRASES = [
    "Multi-tenant SaaS · RBAC · secure REST APIs",
    "Laravel · NestJS · Spring Boot · Node.js",
    "React · Next.js · Vue · Angular",
    "AI-powered products, shipped end-to-end",
    "Linux VPS · Docker · Nginx · CI/CD",
]
HERO_TAGS = [
    ("Laravel", "#ff2d20"), ("React", "#61dafb"), ("NestJS", "#e0234e"),
    ("Docker", "#2496ed"), ("Next.js", "#f8fafc"), ("Spring", "#6db33f"),
]
HERO_PILLS = [
    ("Open to opportunities", C["green"], True),
    ("Cairo, Egypt", C["lilac"], False),
    ("Arabic · English", C["cyan"], False),
]


def hero():
    W, H, X = 880, 300, 52
    OX, OY = 690, 150
    rnd = random.Random(7)

    d = [
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#050913"/>'
        '<stop offset="0.55" stop-color="#0a1122"/><stop offset="1" stop-color="#121c3a"/></linearGradient>',
        glow("gBlue", "#3b82f6", 0.5), glow("gViolet", "#8b5cf6", 0.42), glow("gCyan", "#06b6d4", 0.3),
        '<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#94a3b8"/></pattern>',
        '<radialGradient id="dotFade" cx="0.78" cy="0.5" r="0.6"><stop offset="0" stop-color="#fff" stop-opacity="0.4"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        f'<mask id="dotMask"><rect width="{W}" height="{H}" fill="url(#dotFade)"/></mask>',
        '<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="#fff" stop-opacity="0.06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        shine("edge", W, 6),
        # white name with a light-blue/violet highlight band sweeping across it
        '<linearGradient id="nameFill" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1400" y2="0" spreadMethod="repeat">'
        '<stop offset="0" stop-color="#ffffff"/><stop offset="0.12" stop-color="#ffffff"/><stop offset="0.18" stop-color="#93c5fd"/>'
        '<stop offset="0.22" stop-color="#c4b5fd"/><stop offset="0.28" stop-color="#ffffff"/><stop offset="1" stop-color="#ffffff"/>'
        '<animateTransform attributeName="gradientTransform" type="translate" from="-400 0" to="1000 0" dur="7s" repeatCount="indefinite"/>'
        "</linearGradient>",
        '<linearGradient id="core" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2563eb"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>',
        '<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3b82f6"/>'
        '<stop offset="0.5" stop-color="#8b5cf6"/><stop offset="1" stop-color="#06b6d4"/></linearGradient>',
        '<filter id="blur" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="10"/></filter>',
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>',
    ]

    # backdrop: drifting aurora, dot grid, rising particles, periodic light sweep
    b = ['<g clip-path="url(#frame)">', f'<rect width="{W}" height="{H}" fill="url(#bg)"/>']
    for cx, cy, r, gid, path, dur in (
        (700, 30, 250, "gBlue", "0 0;-80 40;-30 90;0 0", 18),
        (860, 300, 230, "gViolet", "0 0;-60 -50;20 -30;0 0", 22),
        (80, 330, 250, "gCyan", "0 0;70 -40;10 -70;0 0", 26),
    ):
        b.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})"><animateTransform attributeName="transform" type="translate" '
            f'values="{path}" keyTimes="0;0.33;0.66;1" calcMode="spline" keySplines="{EASE_IN_OUT3}" dur="{dur}s" repeatCount="indefinite"/></circle>'
        )
    b.append(f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotMask)"/>')
    for i in range(20):
        x, r = rnd.uniform(20, W - 20), rnd.uniform(0.7, 1.8)
        dur = rnd.uniform(9, 18)
        drift = rnd.uniform(-24, 24)
        timing = f'dur="{n(dur)}s" begin="{n(rnd.uniform(0, dur))}s" repeatCount="indefinite"'
        b.append(
            f'<circle cx="{n(x)}" cy="{H + 6}" r="{n(r)}" fill="{(C["sky"], C["lilac"], C["cyan"])[i % 3]}" opacity="0">'
            f'<animate attributeName="cy" from="{H + 6}" to="-6" {timing}/>'
            f'<animate attributeName="cx" values="{n(x)};{n(x + drift)};{n(x)}" {timing}/>'
            f'<animate attributeName="opacity" values="0;0.85;0" {timing}/></circle>'
        )
    b.append(
        f'<rect x="-300" y="-40" width="170" height="{H + 80}" fill="url(#sweep)" transform="skewX(-18)">'
        '<animate attributeName="x" values="-300;1150;1150" keyTimes="0;0.55;1" dur="11s" begin="1.2s" repeatCount="indefinite"/></rect>'
    )
    b.append("</g>")
    frame = f'x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="17.25" fill="none" stroke-width="1.5"'
    b.append(f'<rect {frame} stroke="#1e293b"/>')
    b.append(f'<rect {frame} stroke="url(#edge)" stroke-opacity="0.55"/>')

    # orbit system: glowing </> core, orbiting dots and tech tags
    b += [
        f'<g transform="translate({OX} {OY})"><g>',
        '<animate attributeName="opacity" values="0;0;1" keyTimes="0;0.2;1" dur="1.6s" fill="freeze"/>',
        f'<animateTransform attributeName="transform" type="scale" values="0.82;0.82;1" keyTimes="0;0.2;1" calcMode="spline" keySplines="{EASE_OUT}" dur="1.6s" fill="freeze"/>',
        '<circle r="142" fill="none" stroke="#1e293b"/>',
        '<circle r="142" fill="none" stroke="url(#accent)" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="110 782.2" opacity="0.85">'
        '<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="12s" repeatCount="indefinite"/></circle>',
        '<circle r="106" fill="none" stroke="#334155" stroke-dasharray="2 7">'
        '<animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="90s" repeatCount="indefinite"/></circle>',
        '<circle r="62" fill="none" stroke="#1e3a8a" stroke-width="1.2"/>',
        '<circle r="52" fill="url(#gBlue)"><animate attributeName="r" values="46;62;46" dur="4s" repeatCount="indefinite"/></circle>',
        '<circle r="40" fill="none" stroke="#60a5fa" stroke-opacity="0.5" stroke-dasharray="3 5">'
        '<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="24s" repeatCount="indefinite"/></circle>',
        '<circle r="31" fill="url(#core)"/>',
        '<circle r="31" fill="none" stroke="#bfdbfe" stroke-opacity="0.45"/>',
        f'<text y="7" text-anchor="middle" fill="#ffffff" font-family="{MONO}" font-size="19" font-weight="700">&lt;/&gt;</text>',
    ]
    for deg, col in ((0, C["sky"]), (180, C["lilac"])):
        b.append(
            f'<g><animateMotion path="{orbit_path(62, deg)}" dur="9s" repeatCount="indefinite"/>'
            f'<circle r="10" fill="url(#gBlue)"/><circle r="3.5" fill="{col}"/></g>'
        )
    for i, (label, col) in enumerate(HERO_TAGS):
        pw = len(label) * 7.2 + 30
        b.append(
            f'<g><animateMotion path="{orbit_path(106, -90 + i * 360 / len(HERO_TAGS))}" dur="64s" repeatCount="indefinite"/>'
            f'<rect x="{n(-pw / 2)}" y="-12" width="{n(pw)}" height="24" rx="12" fill="#0b1222" stroke="#334155"/>'
            f'<circle cx="{n(-pw / 2 + 12)}" r="3.5" fill="{col}"/>'
            f'<g font-family="{MONO}" font-size="12">{mono(-pw / 2 + 21, 4.2, label, C["text"], 7.2)}</g></g>'
        )
    b.append("</g></g>")

    # left column: eyebrow, name, role
    b.append(
        f'<g>{enter(0.1)}<rect x="{X}" y="63.5" width="26" height="3" rx="1.5" fill="url(#accent)"/>'
        f'<text x="{X + 38}" y="70" fill="{C["sky"]}" font-family="{MONO}" font-size="12.5" font-weight="600" letter-spacing="3">HI THERE, I’M</text></g>'
    )
    name = "Hamdy Salah Kamil"
    b.append(
        f'<g font-family="{SANS}" font-size="46" font-weight="700" letter-spacing="-0.5">{enter(0.25)}'
        f'<text x="{X}" y="124" fill="#3b82f6" opacity="0.45" filter="url(#blur)">{name}'
        '<animate attributeName="opacity" values="0.3;0.65;0.3" dur="4s" repeatCount="indefinite"/></text>'
        f'<text x="{X}" y="124" fill="url(#nameFill)">{name}</text></g>'
    )
    b.append(
        f'<g>{enter(0.4)}<text x="{X}" y="162" fill="{C["text"]}" font-family="{SANS}" font-size="22" font-weight="600">Full-Stack Developer</text></g>'
    )

    # typing line: each phrase types in, holds, deletes; one clip per phrase, one shared cursor
    TX, TY, CW = X + 22, 201, 9
    TYPE, DEL, HOLD, GAP = 0.055, 0.022, 2.2, 0.35
    t, cursor, tracks = 1.0, [(0.0, TX)], []
    for p in HERO_PHRASES:
        times, widths = [0.0], [0]
        for k in range(1, len(p) + 1):
            times.append(t + k * TYPE)
            widths.append(k * CW + (3 if k == len(p) else 0))
            cursor.append((t + k * TYPE, TX + k * CW))
        t += len(p) * TYPE + HOLD
        for k in range(1, len(p) + 1):
            times.append(t + k * DEL)
            widths.append((len(p) - k) * CW)
            cursor.append((t + k * DEL, TX + (len(p) - k) * CW))
        t += len(p) * DEL + GAP
        tracks.append((p, times, widths))
    T = t
    loop = f'dur="{n(T)}s" repeatCount="indefinite"'

    def keys(ts):
        return ";".join(f"{x / T:.4f}" for x in ts)

    ty = [f'<g font-family="{MONO}" font-size="15">{enter(0.55)}', mono(X, TY, ">", C["violet"], CW, 700)]
    for i, (p, times, widths) in enumerate(tracks):
        d.append(
            f'<clipPath id="type{i}"><rect x="{TX}" y="{TY - 16}" width="0" height="22">'
            f'<animate attributeName="width" values="{";".join(n(w) for w in widths)}" keyTimes="{keys(times)}" calcMode="discrete" {loop}/>'
            "</rect></clipPath>"
        )
        ty.append(f'<g clip-path="url(#type{i})">{mono(TX, TY, p, C["ice"], CW)}</g>')
    ty.append(
        f'<rect x="{TX}" y="{TY - 14}" width="{CW - 1}" height="18" rx="1" fill="{C["sky"]}">'
        f'<animate attributeName="x" values="{";".join(n(x) for _, x in cursor)}" keyTimes="{keys([c for c, _ in cursor])}" calcMode="discrete" {loop}/>'
        '<animate attributeName="opacity" values="0.9;0" calcMode="discrete" dur="1s" repeatCount="indefinite"/></rect></g>'
    )
    b += ty

    # status pills
    px, py, ph = X, 228, 28
    for i, (label, col, live) in enumerate(HERO_PILLS):
        pw = 41 + len(label) * 7.2
        cx, cy = px + 15, py + ph / 2
        pulse = (
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="4" fill="{col}">'
            '<animate attributeName="r" values="4;11" dur="1.8s" repeatCount="indefinite"/>'
            '<animate attributeName="opacity" values="0.55;0" dur="1.8s" repeatCount="indefinite"/></circle>'
        ) if live else ""
        b.append(
            f'<g>{enter(0.7 + i * 0.12)}'
            f'<rect x="{n(px)}" y="{py}" width="{n(pw)}" height="{ph}" rx="{ph // 2}" fill="#0f172a" fill-opacity="0.8" stroke="{col}" stroke-opacity="0.4"/>'
            f'{pulse}<circle cx="{n(cx)}" cy="{n(cy)}" r="4" fill="{col}"/>'
            f'<g font-family="{MONO}" font-size="12">{mono(px + 27, py + 18.3, label, C["text"], 7.2)}</g></g>'
        )
        px += pw + 10

    return document(W, H, "Hamdy Salah Kamil, Full-Stack Developer", d, b)


# ── capability cards ────────────────────────────────────────────────────────────

CARDS = [
    ("Multi-tenant SaaS", ["Tenant- and year-scoped data, five-level role", "hierarchies, platforms with 30+ modules"],
     "layers", ("#3b82f6", "#6366f1")),
    ("Secure APIs & RBAC", ["Sanctum · JWT · OAuth, approval workflows", "and multi-actor business logic"],
     "shield", ("#8b5cf6", "#d946ef")),
    ("AI-powered products", ["AI lesson preparation and exam generation", "with subscriptions and usage quotas"],
     "spark", ("#06b6d4", "#3b82f6")),
    ("Production delivery", ["Linux VPS · Coolify · Nginx · SSL · Docker", "and CI/CD pipelines with GitHub Actions"],
     "rocket", ("#22c55e", "#06b6d4")),
]


def icon(kind):
    """24×24 line icons, each with a small idle animation."""
    if kind == "layers":
        return (
            '<path d="M12 3 21 8 12 13 3 8Z"><animateTransform attributeName="transform" type="translate" values="0 0;0 -1.6;0 0" '
            'dur="2.8s" repeatCount="indefinite"/></path>'
            '<path d="M3 12.5 12 17.5 21 12.5"><animate attributeName="opacity" values="0.85;0.4;0.85" dur="2.8s" repeatCount="indefinite"/></path>'
            '<path d="M3 17 12 22 21 17"><animate attributeName="opacity" values="0.4;0.85;0.4" dur="2.8s" repeatCount="indefinite"/></path>'
        )
    if kind == "shield":
        return (
            '<path d="M12 2.8 19.5 5.8V11.5C19.5 16.2 16.3 19.6 12 21.2 7.7 19.6 4.5 16.2 4.5 11.5V5.8Z"/>'
            '<path d="M8.6 12 11 14.4 15.6 9.6" stroke-dasharray="10.2"><animate attributeName="stroke-dashoffset" values="10.2;10.2;0;0" '
            'keyTimes="0;0.15;0.4;1" dur="3.6s" repeatCount="indefinite"/></path>'
        )
    if kind == "spark":
        return (
            '<path d="M10 3 11.7 8.3 17 10 11.7 11.7 10 17 8.3 11.7 3 10 8.3 8.3Z">'
            '<animate attributeName="opacity" values="1;0.5;1" dur="2.4s" repeatCount="indefinite"/></path>'
            '<path d="M18 14.2 18.8 16.2 20.8 17 18.8 17.8 18 19.8 17.2 17.8 15.2 17 17.2 16.2Z" opacity="0">'
            '<animate attributeName="opacity" values="0;1;0" dur="2.4s" begin="0.6s" repeatCount="indefinite"/></path>'
            '<path d="M18.5 3v3.4M16.8 4.7h3.4" opacity="0"><animate attributeName="opacity" values="0;1;0" dur="2.4s" begin="1.4s" repeatCount="indefinite"/></path>'
        )
    return (  # rocket
        '<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -1.4;0 0" dur="2.2s" repeatCount="indefinite"/>'
        '<path d="M12 2.5C15.4 4.6 16.9 8.6 16.4 13L14.2 15.8H9.8L7.6 13C7.1 8.6 8.6 4.6 12 2.5Z"/>'
        '<circle cx="12" cy="9" r="1.8"/><path d="M7.6 13 5.2 16.4H8.6M16.4 13 18.8 16.4H15.4"/>'
        '<path d="M10.6 18.4Q12 22.2 13.4 18.4" stroke="#fde68a"><animate attributeName="opacity" values="1;0.3;1" dur="0.6s" repeatCount="indefinite"/></path></g>'
    )


def capabilities():
    CW_, CH, GAP, R = 431, 122, 16, 14
    W, H = 880, CH * 2 + GAP + 2
    perim = 2 * (CW_ - 2 * R) + 2 * (CH - 2 * R) + 2 * math.pi * R
    d, b = [], []
    for i, (title, lines, kind, (a, z)) in enumerate(CARDS):
        x, y = 1 + (i % 2) * (CW_ + GAP), 1 + (i // 2) * (CH + GAP)
        box = f'x="{x}" y="{y}" width="{CW_}" height="{CH}" rx="{R}"'
        d += [
            f'<clipPath id="cc{i}"><rect {box}/></clipPath>',
            f'<linearGradient id="tile{i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{z}"/></linearGradient>',
            glow(f"glow{i}", a, 0.24),
        ]
        tx, ty = x + 22, y + (CH - 48) / 2
        start = -i * perim / 4  # desync the border comets
        b.append(
            f'<g>{enter(0.15 + i * 0.15)}'
            f'<rect {box} fill="{C["card"]}" stroke="{C["edge"]}"/>'
            f'<g clip-path="url(#cc{i})"><circle cx="{x + 46}" cy="{y + 40}" r="150" fill="url(#glow{i})">'
            f'<animate attributeName="opacity" values="0.55;1;0.55" dur="5s" begin="{i * 0.8}s" repeatCount="indefinite"/></circle></g>'
            f'<rect {box} fill="none" stroke="{a}" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="80 {n(perim - 80)}" stroke-dashoffset="{n(start)}">'
            f'<animate attributeName="stroke-dashoffset" from="{n(start)}" to="{n(start - perim)}" dur="9s" repeatCount="indefinite"/></rect>'
            f'<rect x="{n(tx)}" y="{n(ty)}" width="48" height="48" rx="12" fill="url(#tile{i})"/>'
            f'<rect x="{n(tx + 0.5)}" y="{n(ty + 0.5)}" width="47" height="47" rx="11.5" fill="none" stroke="#ffffff" stroke-opacity="0.2"/>'
            f'<g transform="translate({n(tx + 12)} {n(ty + 12)})" fill="none" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{icon(kind)}</g>'
            f'<text x="{x + 90}" y="{y + 47}" fill="{C["white"]}" font-family="{SANS}" font-size="17" font-weight="600">{escape(title)}</text>'
            + "".join(
                f'<text x="{x + 90}" y="{y + 71 + j * 20}" fill="{C["body"]}" font-family="{SANS}" font-size="13.5">{escape(line)}</text>'
                for j, line in enumerate(lines)
            )
            + f'<text x="{x + CW_ - 20}" y="{y + 30}" text-anchor="end" fill="{C["dim"]}" font-family="{MONO}" font-size="12">0{i + 1}</text>'
            "</g>"
        )
    return document(W, H, "What I build: multi-tenant SaaS, secure APIs and RBAC, AI-powered products, production delivery", d, b)


# ── footer ──────────────────────────────────────────────────────────────────────

def footer():
    W, H = 880, 170
    rnd = random.Random(3)
    d = [
        '<linearGradient id="w1" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1e3a8a"/><stop offset="1" stop-color="#3b82f6"/></linearGradient>',
        '<linearGradient id="w2" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#4c1d95"/><stop offset="1" stop-color="#1d4ed8"/></linearGradient>',
        '<linearGradient id="w3" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0b1222"/>'
        '<stop offset="0.5" stop-color="#0f172a"/><stop offset="1" stop-color="#172554"/></linearGradient>',
    ]
    b = []
    for i in range(7):  # twinkling sparks above the waves
        x, y, s = rnd.uniform(60, W - 60), rnd.uniform(12, 52), rnd.uniform(2.5, 4.5)
        b.append(
            f'<path d="M{n(x)} {n(y - s)}L{n(x + s * 0.3)} {n(y - s * 0.3)} {n(x + s)} {n(y)} {n(x + s * 0.3)} {n(y + s * 0.3)} '
            f'{n(x)} {n(y + s)} {n(x - s * 0.3)} {n(y + s * 0.3)} {n(x - s)} {n(y)} {n(x - s * 0.3)} {n(y - s * 0.3)}Z" '
            f'fill="{(C["sky"], C["lilac"])[i % 2]}" opacity="0"><animate attributeName="opacity" values="0;0.9;0" '
            f'dur="{n(rnd.uniform(2.4, 4))}s" begin="{n(rnd.uniform(0, 3))}s" repeatCount="indefinite"/></path>'
        )
    for period, amp, base, fill, op, dur, reverse in (
        (440, 9, 66, "url(#w1)", 0.55, 13, False),
        (880 / 3, 11, 80, "url(#w2)", 0.6, 9, True),
        (440, 7, 96, "url(#w3)", 1, 17, False),
    ):
        pts = " ".join(
            f"{n(x)},{n(base + amp * math.sin(2 * math.pi * x / period))}"
            for x in (i * 8 for i in range(math.ceil((W + period) / 8) + 1))
        )
        span = math.ceil((W + period) / 8) * 8
        frm, to = (f"{n(-period)} 0", "0 0") if reverse else ("0 0", f"{n(-period)} 0")
        b.append(
            f'<path d="M{pts} L{span},{H} L0,{H}Z" fill="{fill}" opacity="{op}">'
            f'<animateTransform attributeName="transform" type="translate" from="{frm}" to="{to}" dur="{dur}s" repeatCount="indefinite"/></path>'
        )
    b.append(
        f'<text x="{W // 2}" y="134" text-anchor="middle" fill="{C["white"]}" font-family="{SANS}" font-size="19" font-weight="700">Thanks for stopping by</text>'
    )
    b.append(
        f'<text x="{W // 2}" y="156" text-anchor="middle" fill="{C["ice"]}" font-family="{MONO}" font-size="12" letter-spacing="1">'
        "let’s build something great together</text>"
    )
    return document(W, H, "Thanks for stopping by", d, b)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    write("hero.svg", hero())
    write("capabilities.svg", capabilities())
    write("footer.svg", footer())
