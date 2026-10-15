"""Generate animated "snake eats my contribution graph" SVGs (SMIL only, no scripts).

Reads the public contribution calendar, so it needs no token and no third-party action.
Usage: python scripts/gen_snake.py HamdySalah assets
Writes snake.svg (light) and snake-dark.svg into the given directory.
"""
import os
import re
import sys
import urllib.request
from collections import deque

USER = sys.argv[1] if len(sys.argv) > 1 else "HamdySalah"
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "assets"

STEP = 15       # grid pitch (px)
CELL = 11       # contribution square size
PAD = 12        # padding around the snake's track
DT = 0.08       # seconds per snake move
REST = 1.5      # pause on the cleared board before the loop restarts
LENGTH = 5      # snake segments
ROWS = 7

THEMES = {
    "snake.svg": {
        "empty": "#ebedf0", "levels": ["#bfdbfe", "#93c5fd", "#3b82f6", "#1d4ed8"], "head": (0x1D, 0x4E, 0xD8), "tail": (0x8B, 0x5C, 0xF6),
    },
    "snake-dark.svg": {
        "empty": "#161b22", "levels": ["#1e3a8a", "#1d4ed8", "#3b82f6", "#60a5fa"], "head": (0x60, 0xA5, 0xFA), "tail": (0xA7, 0x8B, 0xFA),
    },
}
MOVES = ((1, 0), (0, 1), (-1, 0), (0, -1))


def fetch_calendar(user):
    """Return {(week, weekday): level 0-4} from the public contributions page."""
    req = urllib.request.Request(f"https://github.com/users/{user}/contributions", headers={"User-Agent": "gen_snake"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    cells = {}
    for tag in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        pos = re.search(r'id="contribution-day-component-(\d+)-(\d+)"', tag)
        level = re.search(r'data-level="(\d)"', tag)
        if pos and level:
            cells[(int(pos.group(2)), int(pos.group(1)))] = int(level.group(1))
    if not cells:
        sys.exit("no contribution cells found; GitHub may have changed the calendar markup")
    return cells


def plan(cells, cols):
    """Walk the snake from outside the top-left corner, eating the lightest squares first, then return home."""
    start = (-1, -1)
    left = {p: lvl for p, lvl in cells.items() if lvl}
    path, eaten = [start], {}
    body = deque([start] * LENGTH)

    def inside(p):
        return -1 <= p[0] <= cols and -1 <= p[1] <= ROWS

    def bfs(src, goals, blocked):
        prev, q = {src: None}, deque([src])
        while q:
            p = q.popleft()
            if p in goals:
                route = []
                while p != src:
                    route.append(p)
                    p = prev[p]
                return route[::-1]
            for dx, dy in MOVES:
                nb = (p[0] + dx, p[1] + dy)
                if inside(nb) and nb not in prev and nb not in blocked:
                    prev[nb] = p
                    q.append(nb)
        return None

    def walk(route):
        for p in route:
            path.append(p)
            body.appendleft(p)
            body.pop()
            if p in left:
                eaten[p] = len(path) - 1
                del left[p]

    for level in range(1, 5):
        while any(lvl == level for lvl in left.values()):
            goals = {p for p, lvl in left.items() if lvl == level}
            avoid = {p for p, lvl in left.items() if lvl > level} | set(list(body)[1:-1])
            walk(bfs(path[-1], goals, avoid) or bfs(path[-1], goals, set()))
    walk(bfs(path[-1], {start}, set()) or [])
    return path, eaten


def n(x):
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def render(theme, cells, cols, path, eaten):
    W = 2 * PAD + (cols + 2) * STEP - (STEP - CELL)
    H = 2 * PAD + (ROWS + 2) * STEP - (STEP - CELL)
    steps = len(path) - 1
    T = steps * DT + REST
    loop = f'dur="{n(T)}s" repeatCount="indefinite"'

    def center(p):
        return PAD + (p[0] + 1) * STEP + CELL / 2, PAD + (p[1] + 1) * STEP + CELL / 2

    out = []
    for (x, y), lvl in sorted(cells.items()):
        px, py = PAD + (x + 1) * STEP, PAD + (y + 1) * STEP
        color = theme["levels"][lvl - 1] if lvl else theme["empty"]
        anim = (
            f'<animate attributeName="fill" values="{color};{theme["empty"]}" keyTimes="0;{eaten[(x, y)] * DT / T:.4f}" calcMode="discrete" {loop}/>'
            if (x, y) in eaten else ""
        )
        out.append(f'<rect x="{px}" y="{py}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}">{anim}</rect>')

    for i in reversed(range(LENGTH)):  # draw tail first so the head stays on top
        # linear motion only needs the corners: drop points that continue the previous move unchanged
        pts = [(s * DT, center(path[max(0, s - i)])) for s in range(steps + 1)] + [(T, center(path[-1]))]
        keep = [pts[0]] + [
            pts[k] for k in range(1, len(pts) - 1)
            if (pts[k][1][0] - pts[k - 1][1][0], pts[k][1][1] - pts[k - 1][1][1])
            != (pts[k + 1][1][0] - pts[k][1][0], pts[k + 1][1][1] - pts[k][1][1])
        ] + [pts[-1]]
        size = CELL + 1 - i * 1.3
        f = i / max(1, LENGTH - 1)
        rgb = "#" + "".join(f"{round(a + (b - a) * f):02x}" for a, b in zip(theme["head"], theme["tail"]))
        out.append(
            f'<rect x="{n(-size / 2)}" y="{n(-size / 2)}" width="{n(size)}" height="{n(size)}" rx="{n(size * 0.32)}" fill="{rgb}">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="{";".join(f"{n(cx)} {n(cy)}" for _, (cx, cy) in keep)}" '
            f'keyTimes="{";".join(f"{t / T:.5f}" for t, _ in keep)}" {loop}/></rect>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="A snake eating {USER}\'s contribution graph">\n<title>Snake eating my contribution graph</title>\n'
        + "\n".join(out) + "\n</svg>\n"
    )


if __name__ == "__main__":
    cells = fetch_calendar(USER)
    cols = max(x for x, _ in cells) + 1
    path, eaten = plan(cells, cols)
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, theme in THEMES.items():
        svg = render(theme, cells, cols, path, eaten)
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(svg)
        print(f"wrote {os.path.join(OUT_DIR, name)} ({len(svg) / 1024:.1f} KB)")
    print(f"{len(eaten)} contribution days eaten in {len(path) - 1} moves, loop {(len(path) - 1) * DT + REST:.1f}s")
