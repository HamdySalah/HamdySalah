"""Generate an animated terminal SVG (SMIL only, no scripts) for a GitHub profile README."""
import sys
from xml.sax.saxutils import escape

OUT = sys.argv[1]

W = 880
CW = 9          # fixed char width enforced via textLength
FS = 15
LH = 23
X0 = 28
GAP = 12
TYPE = 0.045    # seconds per typed char

C = {
    "bg": "#0d1117", "bar": "#161b22", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e", "name": "#ffffff",
    "green": "#3fb950", "blue": "#58a6ff", "accent": "#3b82f6",
    "dir": "#58a6ff", "hash": "#d29922", "head": "#39c5cf", "purple": "#a371f7",
}
BOLD = {"name", "dir", "head"}

PROMPT = [(0, "hamdy@dev", "green"), (9, ":", "text"), (10, "~", "blue"), (11, "$", "text")]
CMD_COL = 13

SCRIPT = [
    ("cmd", "whoami"),
    ("out", [[(0, "Hamdy Salah Kamil", "name"), (18, "· Full-Stack Developer · Cairo, Egypt", "muted")]]),
    ("cmd", "cat now.md"),
    ("out", [
        [(0, "▸", "accent"), (2, "Building production SaaS at Aura QR — healthcare, automotive & EdTech", "text")],
        [(0, "▸", "accent"), (2, "Multi-tenant architecture · RBAC · secure REST APIs · AI-powered features", "text")],
    ]),
    ("cmd", "ls ~/stack"),
    ("out", [[(0, "laravel  nestjs  spring-boot  node  react  next.js  postgres  mysql  mongodb  docker", "dir")]]),
    ("cmd", "git log --oneline --career"),
    ("out", [
        [(0, "a7f3c21", "hash"), (8, "(HEAD -> main)", "head"), (23, "Aura QR — Full-Stack Developer", "text"), (62, "2026 – now", "muted")],
        [(0, "4be91d0", "hash"), (8, "Optomatica (Azimut) — Full-Stack Developer", "text"), (62, "2025 – 2026", "muted")],
        [(0, "2c8e5aa", "hash"), (8, "Freelance — Full-Stack & DevOps Engineer", "text"), (62, "2025", "muted")],
        [(0, "1f02b9e", "hash"), (8, "ITI — 9-Month Open-Source Track Diploma", "text"), (62, "2024 – 2025", "muted")],
        [(0, "0c41d8a", "hash"), (8, "Assiut University — BSc Computer & IT", "text"), (62, "2020 – 2024", "muted")],
    ]),
]


def tokens(col, s):
    """Split a segment into space-free tokens with absolute columns (keeps spacing exact)."""
    out, i = [], 0
    while i < len(s):
        if s[i] == " ":
            i += 1
            continue
        j = i
        while j < len(s) and s[j] != " ":
            j += 1
        out.append((col + i, s[i:j]))
        i = j
    return out


def text_el(col, s, color, y):
    parts = []
    for c, tok in tokens(col, s):
        w = len(tok) * CW
        weight = ' font-weight="700"' if color in BOLD else ""
        tl = f' textLength="{w}" lengthAdjust="spacingAndGlyphs"' if len(tok) > 1 else ""
        parts.append(f'<text x="{X0 + c * CW}" y="{y}" fill="{C[color]}"{weight}{tl}>{escape(tok)}</text>')
    return "".join(parts)


def f(t):
    return f"{t:.2f}s"


body, defs = [], []
y = 72
t = 0.5
clip_id = 0

for kind, payload in SCRIPT:
    if kind == "cmd":
        cmd = payload
        n = len(cmd)
        cx = X0 + CMD_COL * CW
        ts = t + 0.35
        dur = n * TYPE
        te = ts + dur
        clip_id += 1
        widths = ";".join(str(i * CW + (4 if i == n else 0)) for i in range(n + 1))
        xs = ";".join(str(cx + i * CW) for i in range(n + 1))
        defs.append(
            f'<clipPath id="c{clip_id}"><rect x="{cx}" y="{y - LH + 6}" width="0" height="{LH}">'
            f'<animate attributeName="width" values="{widths}" calcMode="discrete" begin="{f(ts)}" dur="{f(dur)}" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        prompt = "".join(text_el(c, s, col, y) for c, s, col in PROMPT)
        body.append(
            f'<g opacity="0"><set attributeName="opacity" to="1" begin="{f(t)}" fill="freeze"/>'
            f"{prompt}"
            f'<g clip-path="url(#c{clip_id})">{text_el(CMD_COL, cmd, "text", y)}</g>'
            f'<rect x="{cx}" y="{y - 14}" width="{CW}" height="18" fill="{C["accent"]}" opacity="0">'
            f'<set attributeName="opacity" to="0.85" begin="{f(t)}"/>'
            f'<animate attributeName="x" values="{xs}" calcMode="discrete" begin="{f(ts)}" dur="{f(dur)}" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{f(te + 0.2)}" fill="freeze"/>'
            f"</rect></g>"
        )
        y += LH
        t = te + 0.3
    else:
        for line in payload:
            content = "".join(text_el(c, s, col, y) for c, s, col in line)
            body.append(
                f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{f(t)}" dur="0.25s" fill="freeze"/>{content}</g>'
            )
            y += LH
            t += 0.12
        y += GAP
        t += 0.5

# final idle prompt with blinking cursor
prompt = "".join(text_el(c, s, col, y) for c, s, col in PROMPT)
cx = X0 + CMD_COL * CW
body.append(
    f'<g opacity="0"><set attributeName="opacity" to="1" begin="{f(t)}" fill="freeze"/>{prompt}'
    f'<rect x="{cx}" y="{y - 14}" width="{CW}" height="18" fill="{C["accent"]}">'
    f'<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1.1s" begin="{f(t)}" repeatCount="indefinite"/>'
    f"</rect></g>"
)

H = y + 30

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal: Hamdy Salah Kamil, Full-Stack Developer at Aura QR">
<title>Hamdy Salah Kamil — Full-Stack Developer</title>
<defs>
<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0" spreadMethod="repeat">
<stop offset="0" stop-color="#3b82f6"/><stop offset="0.33" stop-color="#8b5cf6"/><stop offset="0.66" stop-color="#06b6d4"/><stop offset="1" stop-color="#3b82f6"/>
<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{W} 0" dur="6s" repeatCount="indefinite"/>
</linearGradient>
<clipPath id="win"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12"/></clipPath>
{"".join(defs)}
</defs>
<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="{C["bg"]}"/>
<rect width="{W}" height="40" fill="{C["bar"]}"/>
<rect y="40" width="{W}" height="2" fill="url(#shine)"/>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{C["border"]}"/>
<circle cx="22" cy="20" r="6" fill="#ff5f57"/><circle cx="42" cy="20" r="6" fill="#febc2e"/><circle cx="62" cy="20" r="6" fill="#28c840"/>
<text x="{W / 2}" y="25" text-anchor="middle" fill="{C["muted"]}" font-family="-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="13">hamdy@dev: ~/profile</text>
<g font-family="ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace" font-size="{FS}">
{chr(10).join(body)}
</g>
</svg>
'''

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print(f"wrote {OUT} ({W}x{H}), animation ends ~{t:.1f}s")
