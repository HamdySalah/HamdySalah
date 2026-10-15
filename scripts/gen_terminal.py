"""Generate a looping animated terminal SVG (SMIL only, no scripts) for a GitHub profile README.

Usage: python scripts/gen_terminal.py assets/terminal.svg
"""
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
HOLD = 7.0      # seconds the finished session stays on screen before the loop restarts
FADE = 0.6      # fade-out at the end of each loop
BLINK = 0.55    # idle cursor half-period

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
        [(0, "▸", "accent"), (2, "Building production SaaS for healthcare, automotive & EdTech", "text")],
        [(0, "▸", "accent"), (2, "Multi-tenant architecture · RBAC · secure REST APIs · AI-powered features", "text")],
    ]),
    ("cmd", "ls ~/stack"),
    ("out", [[(0, "laravel  nestjs  spring-boot  node  react  next.js  postgres  mysql  mongodb  docker", "dir")]]),
    ("cmd", "git log --oneline --career"),
    ("out", [
        [(0, "a7f3c21", "hash"), (8, "(HEAD -> main)", "head"), (23, "Full-Stack Developer — SaaS platforms", "text"), (62, "2026 – now", "muted")],
        [(0, "4be91d0", "hash"), (8, "Optomatica (Azimut) — Full-Stack Developer", "text"), (62, "2025 – 2026", "muted")],
        [(0, "2c8e5aa", "hash"), (8, "Freelance — Full-Stack & DevOps Engineer", "text"), (62, "2025", "muted")],
        [(0, "1f02b9e", "hash"), (8, "ITI — 9-Month Open-Source Track Diploma", "text"), (62, "2024 – 2025", "muted")],
        [(0, "0c41d8a", "hash"), (8, "Assiut University — BSc Computer & IT", "text"), (62, "2020 – 2024", "muted")],
    ]),
    ("cmd", "echo $STATUS"),
    ("out", [[(0, "●", "green"), (2, "Open to full-time roles, freelance projects & collaborations", "green")]]),
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


# pass 1: lay out the session and its timeline
cmds, lines = [], []
y = 72
t = 0.5
for kind, payload in SCRIPT:
    if kind == "cmd":
        ts = t + 0.35
        cmds.append((y, t, ts, payload))
        y += LH
        t = ts + len(payload) * TYPE + 0.3
    else:
        for line in payload:
            lines.append((y, t, line))
            y += LH
            t += 0.12
        y += GAP
        t += 0.5
idle_y, idle_t = y, t
T = t + HOLD
H = y + 30


# pass 2: render, with every animation keyed to one shared loop of length T
def keys(times):
    return ";".join(f"{x / T:.4f}" for x in times)


LOOP = f'dur="{T:.2f}s" repeatCount="indefinite"'


def discrete(attr, values, times):
    return f'<animate attributeName="{attr}" values="{";".join(str(v) for v in values)}" keyTimes="{keys(times)}" calcMode="discrete" {LOOP}/>'


body, defs = [], []
prompt_at = lambda y: "".join(text_el(c, s, col, y) for c, s, col in PROMPT)
cx = X0 + CMD_COL * CW

for i, (y, t0, ts, cmd) in enumerate(cmds, 1):
    n = len(cmd)
    te = ts + n * TYPE
    typed = [0.0] + [ts + k * TYPE for k in range(1, n + 1)]
    defs.append(
        f'<clipPath id="c{i}"><rect x="{cx}" y="{y - LH + 6}" width="0" height="{LH}">'
        + discrete("width", [0] + [k * CW + (4 if k == n else 0) for k in range(1, n + 1)], typed)
        + "</rect></clipPath>"
    )
    body.append(
        f'<g opacity="0">{discrete("opacity", [0, 1], [0, t0])}{prompt_at(y)}'
        f'<g clip-path="url(#c{i})">{text_el(CMD_COL, cmd, "text", y)}</g>'
        f'<rect x="{cx}" y="{y - 14}" width="{CW}" height="18" fill="{C["accent"]}" opacity="0">'
        + discrete("opacity", [0, 0.85, 0], [0, t0, te + 0.2])
        + discrete("x", [cx + k * CW for k in range(n + 1)], typed)
        + "</rect></g>"
    )

for y, t0, line in lines:
    content = "".join(text_el(c, s, col, y) for c, s, col in line)
    body.append(
        f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{keys([t0, t0 + 0.25])};1" {LOOP}/>{content}</g>'
    )

# final idle prompt with blinking cursor
blink_times, blink_vals, tb = [0.0], [0], idle_t
while tb < T:
    blink_times.append(tb)
    blink_vals.append(1 if len(blink_vals) % 2 else 0)
    tb += BLINK
body.append(
    f'<g opacity="0">{discrete("opacity", [0, 1], [0, idle_t])}{prompt_at(idle_y)}'
    f'<rect x="{cx}" y="{idle_y - 14}" width="{CW}" height="18" fill="{C["accent"]}" opacity="0">'
    + discrete("opacity", blink_vals, blink_times)
    + "</rect></g>"
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal: Hamdy Salah Kamil, Full-Stack Developer in Cairo, Egypt">
<title>Hamdy Salah Kamil — Full-Stack Developer</title>
<defs>
<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0" spreadMethod="repeat">
<stop offset="0" stop-color="#3b82f6"/><stop offset="0.33" stop-color="#8b5cf6"/><stop offset="0.66" stop-color="#06b6d4"/><stop offset="1" stop-color="#3b82f6"/>
<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{W} 0" dur="6s" repeatCount="indefinite"/>
</linearGradient>
<radialGradient id="ambient" cx="0.85" cy="0" r="0.7"><stop offset="0" stop-color="#3b82f6" stop-opacity="0.12"/><stop offset="1" stop-color="#3b82f6" stop-opacity="0"/></radialGradient>
<clipPath id="win"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12"/></clipPath>
{"".join(defs)}
</defs>
<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="{C["bg"]}"/>
<rect width="{W}" height="{H}" fill="url(#ambient)"/>
<rect width="{W}" height="40" fill="{C["bar"]}"/>
<rect y="40" width="{W}" height="2" fill="url(#shine)"/>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{C["border"]}"/>
<circle cx="22" cy="20" r="6" fill="#ff5f57"/><circle cx="42" cy="20" r="6" fill="#febc2e"/><circle cx="62" cy="20" r="6" fill="#28c840"/>
<text x="{W / 2}" y="25" text-anchor="middle" fill="{C["muted"]}" font-family="-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="13">hamdy@dev: ~/profile</text>
<g font-family="ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace" font-size="{FS}">
<animate attributeName="opacity" values="1;1;0" keyTimes="0;{(T - FADE) / T:.4f};1" {LOOP}/>
{chr(10).join(body)}
</g>
</svg>
'''

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print(f"wrote {OUT} ({W}x{H}), session types out in ~{idle_t:.1f}s, loops every {T:.1f}s")
