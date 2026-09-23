#!/usr/bin/env python3
"""Пиксельный логотип Harness Wars: промпты >_ и _< лицом к лицу, между ними молния.

  python brand/make_logo.py   # пишет logo.svg, favicon.svg и avatar.png рядом с index.html
"""
from pathlib import Path
from PIL import Image

N = 32
INK, BLUE, ORANGE, GOLD, CREAM = "#120E24", "#3A2BFF", "#FF5A1F", "#FFE14D", "#FFF4DC"
OUT = Path(__file__).resolve().parent.parent


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return ((px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2) ** 0.5


def inside(px, py, poly):
    hit = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def grid():
    g = [[None] * N for _ in range(N)]
    chevron = [((3, 8), (9.5, 14)), ((9.5, 14), (3, 20))]
    cursor = (3, 24, 10, 26)
    bolt = [(19.5, 3), (13, 16.5), (16.5, 16.5), (14, 29), (19.5, 14.5), (16.5, 14.5), (21.5, 3)]
    for y in range(N):
        for x in range(N):
            cx, cy = x + 0.5, y + 0.5
            mx = N - cx
            if inside(cx, cy, bolt):
                g[y][x] = GOLD
            elif any(seg_dist(cx, cy, *a, *b) <= 1.25 for a, b in chevron) or (
                    cursor[0] <= cx < cursor[2] and cursor[1] <= cy < cursor[3]):
                g[y][x] = BLUE
            elif any(seg_dist(mx, cy, *a, *b) <= 1.25 for a, b in chevron) or (
                    cursor[0] <= mx < cursor[2] and cursor[1] <= cy < cursor[3]):
                g[y][x] = ORANGE
    out = [row[:] for row in g]
    for y in range(N):
        for x in range(N):
            if g[y][x] is None and any(
                0 <= y + dy < N and 0 <= x + dx < N and g[y + dy][x + dx] is not None
                for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                out[y][x] = INK
    return out


def svg(g, bg=None):
    rects = []
    for y, row in enumerate(g):
        x = 0
        while x < N:
            c = row[x]
            run = 1
            while x + run < N and row[x + run] == c:
                run += 1
            if c:
                rects.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{c}"/>')
            x += run
    back = f'<rect width="{N}" height="{N}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {N} {N}" shape-rendering="crispEdges">'
            f'{back}{"".join(rects)}</svg>\n')


def png(g, size, pad, bg):
    img = Image.new("RGBA", (N + 2 * pad, N + 2 * pad), bg)
    for y, row in enumerate(g):
        for x, c in enumerate(row):
            if c:
                img.putpixel((x + pad, y + pad), Image.new("RGB", (1, 1), c).getpixel((0, 0)) + (255,))
    return img.resize((size, size), Image.NEAREST)


def main():
    g = grid()
    (OUT / "logo.svg").write_text(svg(g))
    (OUT / "favicon.svg").write_text(svg(g, "#1E1840"))
    png(g, 1024, 6, "#1E1840").save(OUT / "avatar.png")

if __name__ == "__main__":
    main()
