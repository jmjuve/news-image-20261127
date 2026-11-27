#!/usr/bin/env python3
"""news-image-20261127: one front-page image summing up the world news
of Friday 27 November 2026.

Pure Python 3 standard library only. No network, no third-party
packages, no external fonts. The picture is drawn with code -- flat
vector shapes and a hand-built 5x7 bitmap capital font -- and written
as a deterministic PNG (zlib level 9, no ancillary chunks), so every
run writes identical bytes.

Run:  python3 main.py            # writes out/entry.png
       MAKEFUN_OUTPUT_DIR=/output python3 main.py   # grader mode

Front page for Friday 27 November 2026:
  Hero:  Black Friday -- the world's biggest shopping day falls
         today. Adobe forecasts $12.9bn of US online spending
         (a FORECAST, not a result); stores open from 6 a.m.
  Minis: Tokyo core inflation up 2.9% (above the BoJ's 2% target) /
         India v New Zealand 2nd Test begins in Christchurch,
         India bowl first, Gurnoor Brar debuts /
         Nottingham Forest v Chelsea tonight, Premier League, 8 p.m.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

CREAM = (246, 239, 221)   # newsprint
INK = (17, 17, 17)
RED = (176, 30, 30)       # lead story only
GOLD = (212, 175, 55)     # sale tags, coin
PITCH = (34, 128, 66)     # cricket green
SKY = (58, 96, 158)       # New Zealand flag blue
SAFFRON = (255, 153, 51)  # Indian flag, top band
LEAF = (19, 136, 8)       # Indian flag, bottom band
GREY = (150, 150, 146)    # rain cloud


# ------------------------------------------------------------------ font
# Hand-built capitals on a 5-wide by 7-tall grid. "#" is ink, "." is
# blank. One blank column follows each glyph, so the advance is 6 cells.
GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
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
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", "#....", "#...."),
    "$": (".###.", "#.#.#", "#.#..", ".###.", "..#.#", "#.#.#", ".###."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
}


def glyph_rows(ch):
    """Bitmap rows for one character, or None if unknown."""
    return GLYPHS.get(ch)


# ---------------------------------------------------------------- canvas
class Sheet:
    """An RGB canvas backed by one flat bytearray."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def dot(self, x, y, color):
        x = int(round(x))
        y = int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def rect(self, x0, y0, x1, y1, color):
        x0 = max(0, int(x0))
        y0 = max(0, int(y0))
        x1 = min(self.w, int(x1))
        y1 = min(self.h, int(y1))
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def frame(self, x0, y0, x1, y1, color, t):
        self.rect(x0, y0, x1, y0 + t, color)
        self.rect(x0, y1 - t, x1, y1, color)
        self.rect(x0, y0, x0 + t, y1, color)
        self.rect(x1 - t, y0, x1, y1, color)

    def disc(self, cx, cy, r, color):
        cx = int(round(cx))
        cy = int(round(cy))
        r = int(max(1, round(r)))
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for x in range(cx - dx, cx + dx + 1):
                self.dot(x, cy + dy, color)

    def ring(self, cx, cy, r, color, t):
        cx = int(round(cx))
        cy = int(round(cy))
        r = int(max(1, round(r)))
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            dx_in = int(((r - t) * (r - t) - dy * dy) ** 0.5) \
                if abs(dy) < r - t else 0
            for x in range(cx - dx, cx - dx_in):
                self.dot(x, cy + dy, color)
            for x in range(cx + dx_in + 1, cx + dx + 1):
                self.dot(x, cy + dy, color)

    def stroke(self, x0, y0, x1, y1, color, width=1):
        steps = int(max(abs(x1 - x0), abs(y1 - y0), 1))
        rad = max(1.0, width / 2.0)
        for i in range(steps + 1):
            t = i / steps
            self.disc(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, rad, color)

    def poly(self, points, color):
        """Fill a polygon with a scanline fill."""
        pts = [(int(round(x)), int(round(y))) for x, y in points]
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.dot(x, y, color)

    # ------------------------------------------------------------ text
    def text_w(self, s, size):
        return len(s) * 6.0 * size / 7.0

    def text(self, x, y, s, size, color):
        cell = size / 7.0
        pix = max(1, int(round(cell)))
        cx = float(x)
        for ch in s:
            if ch == " ":
                cx += 6 * cell
                continue
            rows = glyph_rows(ch)
            if rows is None:
                cx += 6 * cell
                continue
            for gy, row in enumerate(rows):
                for gx, mark in enumerate(row):
                    if mark == "#":
                        self.rect(cx + gx * cell, y + gy * cell,
                                  cx + gx * cell + pix,
                                  y + gy * cell + pix, color)
            cx += 6 * cell

    def centred(self, cx, y, s, size, color):
        self.text(cx - self.text_w(s, size) / 2.0, y, s, size, color)


# --------------------------------------------------------------------- png
def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def write_png(path, sheet):
    raw = bytearray()
    for y in range(sheet.h):
        raw.append(0)  # filter: none
        start = y * sheet.w * 3
        raw += sheet.buf[start:start + sheet.w * 3]
    ihdr = struct.pack(">IIBBBBB", sheet.w, sheet.h, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)


# -------------------------------------------------------------------- draw
def draw():
    p = Sheet(W, H, CREAM)
    p.frame(0, 0, W, H, INK, 6)

    # ---- Masthead ----------------------------------------------------
    p.centred(512, 22, "FRIDAY 27 NOVEMBER 2026", 38, INK)
    p.rect(48, 92, 976, 98, RED)        # red rule
    p.rect(48, 104, 976, 106, INK)      # hairline

    # ---- Hero panel: Black Friday ------------------------------------
    p.frame(36, 112, 988, 648, INK, 3)
    p.centred(512, 128, "THE WORLD'S BIGGEST SHOPPING DAY", 16, INK)
    p.centred(512, 152, "BLACK FRIDAY", 72, INK)
    p.centred(512, 238, "$12.9BN", 96, RED)
    p.centred(512, 348, "SHOPPERS OUT TODAY - $12.9BN EXPECTED", 18, INK)
    p.centred(512, 372, "ONLINE IN THE US; STORES OPEN FROM 6 A.M.", 18, INK)

    # Lingering East Coast rain: a small grey cloud, top right.
    p.disc(884, 150, 16, GREY)
    p.disc(908, 144, 20, GREY)
    p.disc(932, 152, 15, GREY)
    p.rect(872, 158, 946, 166, GREY)
    for x in (884, 906, 928):
        p.stroke(x, 172, x - 4, 190, GREY, 3)

    # Shopfront: facade, striped awning, open door, queue at dawn.
    p.frame(120, 452, 560, 632, INK, 3)
    p.rect(120, 452, 560, 500, RED)             # awning band
    for x in range(140, 560, 40):
        p.rect(x, 452, x + 20, 500, CREAM)      # awning stripes
    p.poly([(120, 500), (560, 500), (540, 516), (140, 516)], INK)
    # Door, open at 6 a.m., with a queue of shoppers.
    p.frame(290, 516, 390, 632, INK, 3)
    p.rect(296, 522, 384, 626, INK)
    p.centred(340, 560, "OPEN", 20, CREAM)
    p.centred(340, 590, "6 A.M.", 13, CREAM)
    # Shop window with a giant sale tag.
    p.frame(140, 530, 280, 632, INK, 3)
    p.centred(210, 556, "SALE", 30, RED)
    p.centred(210, 592, "UP TO", 14, INK)
    p.centred(210, 610, "50% OFF", 14, INK)
    # Queue: four shoppers waiting by the door.
    for qx in (420, 460, 500, 540):
        p.disc(qx, 556, 11, INK)               # head
        p.rect(qx - 9, 566, qx + 9, 632, INK)   # body
    # Big red price tag hanging on the right.
    p.stroke(700, 470, 700, 500, INK, 3)
    p.disc(700, 548, 62, RED)
    p.ring(700, 548, 62, INK, 3)
    p.centred(700, 524, "50%", 44, CREAM)
    p.centred(700, 574, "OFF", 26, CREAM)
    # Shopping bags on the pavement.
    p.poly([(800, 632), (812, 572), (862, 572), (874, 632)], GOLD)
    p.stroke(822, 572, 852, 572, INK, 3)
    p.poly([(890, 632), (900, 586), (940, 586), (950, 632)], RED)
    p.stroke(908, 586, 932, 586, INK, 3)
    p.rect(56, 632, 968, 636, INK)              # pavement line

    # ---- Divider -----------------------------------------------------
    p.rect(40, 660, 984, 664, INK)
    p.rect(341, 672, 343, 1000, INK)
    p.rect(682, 672, 684, 1000, INK)

    # ---- Mini 1: Tokyo prices ----------------------------------------
    p.centred(188, 678, "TOKYO", 17, INK)
    # Rising bars and a climbing arrow, plus a yen coin.
    p.rect(70, 800, 100, 836, INK)
    p.rect(115, 776, 145, 836, INK)
    p.rect(160, 752, 190, 836, INK)
    p.stroke(66, 812, 296, 716, RED, 5)
    p.poly([(296, 716), (272, 722), (288, 740)], RED)
    p.disc(268, 752, 27, GOLD)
    p.ring(268, 752, 27, INK, 3)
    p.centred(268, 740, "Y", 26, INK)
    p.rect(256, 752, 280, 755, INK)
    p.rect(256, 758, 280, 761, INK)
    p.centred(188, 852, "TOKYO PRICES", 26, INK)
    p.centred(188, 888, "UP 2.9%", 28, INK)
    p.centred(188, 940, "CORE INFLATION ABOVE", 14, INK)
    p.centred(188, 964, "BOJ'S 2% TARGET", 14, INK)

    # ---- Mini 2: Christchurch Test -----------------------------------
    p.centred(512, 678, "CHRISTCHURCH", 17, INK)
    # Green pitch, crease lines, bat and red ball, two small flags.
    p.rect(392, 706, 652, 836, PITCH)
    p.rect(392, 764, 652, 768, CREAM)
    p.rect(392, 800, 652, 804, CREAM)
    # India flag, top left of the pitch.
    p.rect(404, 714, 448, 722, SAFFRON)
    p.rect(404, 722, 448, 730, CREAM)
    p.rect(404, 730, 448, 738, LEAF)
    # New Zealand flag, top right of the pitch.
    p.rect(596, 714, 640, 738, SKY)
    p.stroke(596, 714, 640, 738, RED, 3)
    p.stroke(640, 714, 596, 738, RED, 3)
    p.disc(608, 720, 2, CREAM)
    p.disc(628, 732, 2, CREAM)
    # Cricket bat, angled, and the red ball.
    p.poly([(500, 726), (516, 716), (556, 786), (540, 796)], INK)
    p.stroke(516, 716, 532, 692, INK, 6)
    p.disc(600, 782, 11, RED)
    p.centred(512, 852, "TEST DECIDER", 26, INK)
    p.centred(512, 888, "BEGINS", 28, INK)
    p.centred(512, 940, "INDIA BOWL FIRST;", 14, INK)
    p.centred(512, 964, "BRAR DEBUTS", 14, INK)

    # ---- Mini 3: Forest v Chelsea ------------------------------------
    p.centred(836, 678, "NOTTINGHAM", 17, INK)
    # Floodlit night pitch, football under the lights.
    p.rect(714, 706, 954, 836, INK)
    p.rect(714, 706, 954, 712, CREAM)
    p.stroke(730, 712, 730, 760, CREAM, 3)
    p.disc(730, 716, 8, GOLD)
    p.stroke(938, 712, 938, 760, CREAM, 3)
    p.disc(938, 716, 8, GOLD)
    p.disc(834, 772, 36, CREAM)
    p.ring(834, 772, 36, GOLD, 3)
    p.poly([(834, 762), (844, 769), (840, 780), (828, 780), (824, 769)],
           INK)
    p.stroke(834, 762, 834, 738, INK, 3)
    p.stroke(824, 769, 800, 762, INK, 3)
    p.stroke(844, 769, 868, 762, INK, 3)
    p.stroke(828, 780, 820, 802, INK, 3)
    p.stroke(840, 780, 848, 802, INK, 3)
    p.centred(836, 852, "FOREST V CHELSEA", 21, INK)
    p.centred(836, 888, "TONIGHT", 28, INK)
    p.centred(836, 940, "PREMIER LEAGUE,", 14, INK)
    p.centred(836, 964, "8 P.M.", 14, INK)

    return p


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(outdir, exist_ok=True)
    page = draw()
    path = os.path.join(outdir, "entry.png")
    write_png(path, page)
    print("wrote", path)


if __name__ == "__main__":
    main()
