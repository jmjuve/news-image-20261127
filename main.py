#!/usr/bin/env python3
"""News in one image — Friday 27 November 2026.

Draws a 1024x1024 editorial front page with the Python standard
library only: a hand-rolled raster canvas, a hand-drawn 5x7 capital
font, and a hand-written PNG encoder (zlib level 9, no ancillary
chunks, no timestamps) so two runs produce identical bytes.

Layout: masthead date band, one big Black Friday hero panel, and a
bottom strip of three mini-stories (Tokyo inflation, the Christchurch
Test decider, Forest v Chelsea tonight).

Usage:  python3 main.py
Output: out/entry.png  (or $MAKEFUN_OUTPUT_DIR/entry.png)
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---- palette ---------------------------------------------------------
CREAM = (253, 246, 227)
PAPER = (255, 255, 255)
INK = (18, 18, 18)
RED = (198, 32, 32)
DARKRED = (150, 20, 20)
GREY = (110, 110, 108)
BLUEGREY = (90, 120, 140)
GREEN = (46, 125, 60)
LIGHTGREEN = (139, 195, 74)
GOLD = (212, 160, 32)
SKY = (176, 216, 235)
BROWN = (121, 85, 50)
ORANGE = (230, 120, 30)

# ---- 5x7 capital font (drawn for this page) --------------------------
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is empty.
GLYPHS = {
    "A": ("..#..", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "$": ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", "#....", "#...."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
}

# ---- canvas ----------------------------------------------------------
class Page:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def put(self, x, y, rgb):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(rgb)

    def rect(self, x, y, w, h, rgb):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, rgb)

    def frame(self, x, y, w, h, rgb, t):
        self.rect(x, y, w, t, rgb)
        self.rect(x, y + h - t, w, t, rgb)
        self.rect(x, y, t, h, rgb)
        self.rect(x + w - t, y, t, h, rgb)

    def disc(self, cx, cy, r, rgb):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.put(xx, yy, rgb)

    def ring(self, cx, cy, r, rgb, t):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d2 <= r * r:
                    self.put(xx, yy, rgb)

    def line(self, x0, y0, x1, y1, rgb, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            for a in range(t):
                for b in range(t):
                    self.put(x + a, y + b, rgb)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def poly(self, pts, rgb):
        # Scanline fill of a simple polygon.
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for xx in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.put(xx, yy, rgb)

    def glyph(self, x, y, ch, s, rgb):
        rows = GLYPHS.get(ch)
        if rows is None:
            return
        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                if cell == "#":
                    self.rect(x + c * s, y + r * s, s, s, rgb)

    def text(self, x, y, s, rgb, msg):
        cx = x
        for ch in msg:
            self.glyph(cx, y, ch, s, rgb)
            cx += 6 * s

    def text_width(self, s, msg):
        return len(msg) * 6 * s - s

    def centred(self, cx, y, s, rgb, msg):
        self.text(cx - self.text_width(s, msg) // 2, y, s, rgb, msg)


# ---- the front page ---------------------------------------------------
def build():
    pg = Page(W, H, CREAM)
    pg.frame(0, 0, W, H, INK, 8)

    # Masthead: the date, in the image.
    pg.centred(512, 26, 6, INK, "FRIDAY 27 NOVEMBER 2026")
    pg.rect(40, 100, 944, 8, RED)

    # ---- hero panel --------------------------------------------------
    pg.rect(40, 124, 944, 520, PAPER)
    pg.frame(40, 124, 944, 520, INK, 5)
    pg.centred(512, 146, 3, RED, "THE WORLD'S BIGGEST SHOPPING DAY")
    pg.centred(512, 186, 11, INK, "BLACK FRIDAY")
    pg.centred(512, 288, 13, RED, "$12.9BN")
    pg.centred(512, 392, 3, INK, "SHOPPERS OUT TODAY - $12.9BN EXPECTED")
    pg.centred(512, 424, 3, INK, "ONLINE IN THE US; STORES OPEN FROM 6 A.M.")

    # Storefront scene along the bottom of the hero.
    # Striped awning.
    for i in range(12):
        col = RED if i % 2 == 0 else PAPER
        pg.rect(64 + i * 76, 470, 76, 34, col)
    pg.rect(64, 504, 912, 5, DARKRED)
    # Shop front: windows, open door, queue of shoppers.
    pg.rect(84, 520, 260, 108, SKY)
    pg.frame(84, 520, 260, 108, INK, 4)
    pg.line(214, 520, 214, 628, INK, 4)
    pg.line(84, 574, 344, 574, INK, 4)
    pg.rect(700, 520, 260, 108, SKY)
    pg.frame(700, 520, 260, 108, INK, 4)
    pg.line(830, 520, 830, 628, INK, 4)
    pg.line(700, 574, 960, 574, INK, 4)
    # Door, open at dawn, with a queue.
    pg.rect(452, 512, 120, 116, INK)
    pg.rect(464, 524, 96, 104, GOLD)
    pg.rect(492, 524, 40, 104, INK)
    for i, qx in enumerate((392, 420, 592, 620)):
        pg.disc(qx, 600, 13, (200 + i * 8 % 40, 60, 60) if i % 2 else (40, 80, 160))
        pg.rect(qx - 13, 612, 26, 16, INK)
    # Sale tags hanging from the awning.
    for tx, tc in ((120, RED), (880, ORANGE)):
        pg.poly([(tx, 516), (tx + 34, 534), (tx, 552), (tx - 34, 534)], tc)
        pg.disc(tx, 534, 5, PAPER)
        pg.text(tx - 9, 522, 2, PAPER, "%")
    # Shopping bags.
    for bx, bc in ((180, RED), (800, GREEN)):
        pg.poly([(bx, 560), (bx + 84, 560), (bx + 76, 628), (bx + 8, 628)], bc)
        pg.ring(bx + 42, 556, 16, INK, 3)
    # Rain-cloud nod to the lingering East Coast rain.
    pg.disc(920, 168, 22, BLUEGREY)
    pg.disc(946, 160, 26, BLUEGREY)
    pg.disc(972, 170, 20, BLUEGREY)
    pg.rect(906, 168, 78, 14, BLUEGREY)
    for rx in (918, 940, 962):
        pg.line(rx, 190, rx - 6, 206, BLUEGREY, 3)

    # ---- bottom strip: three mini-stories ----------------------------
    cols = [
        (40, "TOKYO PRICES", "UP 2.9%", "CORE INFLATION, ABOVE", "BOJ'S 2% TARGET"),
        (352, "TEST DECIDER", "BEGINS", "INDIA BOWL FIRST;", "BRAR DEBUTS"),
        (664, "FOREST v", "CHELSEA", "TONIGHT", "PREMIER LEAGUE, 8 P.M."),
    ]
    for x0, h1, h2, s1, s2 in cols:
        pg.rect(x0, 664, 320, 300, PAPER)
        pg.frame(x0, 664, 320, 300, INK, 4)
        pg.rect(x0 + 4, 668, 312, 6, RED)

    # Mini 1 — Tokyo: rising chart arrow over a skyline.
    x0 = 40
    pg.rect(x0 + 24, 700, 272, 60, SKY)
    for bx, bh in ((x0 + 40, 22), (x0 + 80, 34), (x0 + 120, 28),
                   (x0 + 160, 44), (x0 + 200, 38), (x0 + 240, 52)):
        pg.rect(bx, 760 - bh, 28, bh, INK)
    pg.line(x0 + 36, 748, x0 + 150, 716, RED, 5)
    pg.line(x0 + 150, 716, x0 + 276, 690, RED, 5)
    pg.poly([(x0 + 276, 690), (x0 + 250, 688), (x0 + 272, 712)], RED)
    pg.disc(x0 + 264, 700, 12, GOLD)
    pg.centred(x0 + 160, 782, 4, INK, "TOKYO PRICES")
    pg.centred(x0 + 160, 818, 4, RED, "UP 2.9%")
    pg.centred(x0 + 160, 872, 2, GREY, "CORE INFLATION, ABOVE")
    pg.centred(x0 + 160, 892, 2, GREY, "BOJ'S 2% TARGET")

    # Mini 2 — Christchurch: bat, ball and green pitch.
    x0 = 352
    pg.rect(x0 + 24, 700, 272, 60, LIGHTGREEN)
    pg.rect(x0 + 24, 748, 272, 12, GREEN)
    pg.line(x0 + 90, 706, x0 + 150, 754, BROWN, 9)
    pg.rect(x0 + 82, 692, 20, 22, BROWN)
    pg.disc(x0 + 216, 730, 15, RED)
    pg.disc(x0 + 216, 730, 15, RED)
    pg.ring(x0 + 216, 730, 15, PAPER, 2)
    pg.centred(x0 + 160, 782, 4, INK, "TEST DECIDER")
    pg.centred(x0 + 160, 818, 4, RED, "BEGINS")
    pg.centred(x0 + 160, 872, 2, GREY, "INDIA BOWL FIRST;")
    pg.centred(x0 + 160, 892, 2, GREY, "BRAR DEBUTS")

    # Mini 3 — Nottingham: football under floodlights.
    x0 = 664
    pg.rect(x0 + 24, 700, 272, 60, INK)
    for fx in (x0 + 60, x0 + 150, x0 + 240):
        pg.line(fx, 700, fx, 716, GOLD, 4)
        pg.disc(fx, 716, 5, GOLD)
    pg.disc(x0 + 160, 730, 26, PAPER)
    pg.ring(x0 + 160, 730, 26, INK, 3)
    pg.poly([(x0 + 152, 722), (x0 + 168, 722), (x0 + 172, 734),
             (x0 + 160, 742), (x0 + 148, 734)], INK)
    pg.centred(x0 + 160, 776, 4, INK, "FOREST v")
    pg.centred(x0 + 160, 810, 4, INK, "CHELSEA")
    pg.centred(x0 + 160, 844, 4, RED, "TONIGHT")
    pg.centred(x0 + 160, 888, 2, GREY, "PREMIER LEAGUE,")
    pg.centred(x0 + 160, 908, 2, GREY, "8 P.M.")

    # Footer line.
    pg.centred(512, 982, 2, GREY, "ALL STORIES FROM FRIDAY 27 NOVEMBER 2026")
    return pg


# ---- deterministic PNG writer ----------------------------------------
def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(pg, path):
    raw = bytearray()
    for y in range(pg.h):
        raw.append(0)
        raw += pg.px[y * pg.w * 3:(y + 1) * pg.w * 3]
    ihdr = struct.pack(">IIBBBBB", pg.w, pg.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    write_png(build(), os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
