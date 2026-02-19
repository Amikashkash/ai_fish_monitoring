"""Generate PWA fish icons using only Python stdlib."""
import struct, zlib, os

# ── PNG writer ────────────────────────────────────────────────────────────────
def make_png(width, height, pixels):
    """pixels: flat list of (r,g,b) tuples, left-to-right top-to-bottom."""
    def chunk(name, data):
        c = struct.pack(">I", len(data)) + name + data
        return c + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    raw = b""
    for y in range(height):
        raw += b"\x00"
        for x in range(width):
            r, g, b = pixels[y * width + x]
            raw += bytes([r, g, b])
    idat = chunk(b"IDAT", zlib.compress(raw, 9))
    iend = chunk(b"IEND", b"")
    return b"\x89PNG\r\n\x1a\n" + ihdr + idat + iend

# ── Drawing helpers ───────────────────────────────────────────────────────────
def in_ellipse(px, py, cx, cy, rx, ry):
    return ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1.0

def in_triangle(px, py, pts):
    def sign(p1, p2, p3):
        return (p1[0]-p3[0])*(p2[1]-p3[1]) - (p2[0]-p3[0])*(p1[1]-p3[1])
    d1 = sign((px,py), pts[0], pts[1])
    d2 = sign((px,py), pts[1], pts[2])
    d3 = sign((px,py), pts[2], pts[0])
    return not ((d1<0 or d2<0 or d3<0) and (d1>0 or d2>0 or d3>0))

def fill_ellipse(pixels, s, cx, cy, rx, ry, color):
    for y in range(max(0, int(cy-ry)-1), min(s, int(cy+ry)+2)):
        for x in range(max(0, int(cx-rx)-1), min(s, int(cx+rx)+2)):
            if in_ellipse(x+0.5, y+0.5, cx, cy, rx, ry):
                pixels[y*s+x] = color

def fill_triangle(pixels, s, pts, color):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    for y in range(max(0, int(min(ys))-1), min(s, int(max(ys))+2)):
        for x in range(max(0, int(min(xs))-1), min(s, int(max(xs))+2)):
            if in_triangle(x+0.5, y+0.5, pts):
                pixels[y*s+x] = color

def fill_circle(pixels, s, cx, cy, r, color):
    fill_ellipse(pixels, s, cx, cy, r, r, color)

# ── Fish icon ─────────────────────────────────────────────────────────────────
def draw_icon(size):
    s = size

    BG     = (8, 30, 63)      # deep navy  #081e3f
    BODY   = (14, 165, 233)   # sky-500  (brand blue)
    BELLY  = (125, 211, 252)  # sky-300  (lighter belly)
    DARK   = (2, 117, 177)    # sky-700  (tail / fins)
    WHITE  = (255, 255, 255)
    PUPIL  = (8, 30, 63)      # same as BG
    BUBBLE = (56, 189, 248)   # sky-400

    pixels = [BG] * (s * s)

    # Fish faces RIGHT, tail on the LEFT
    cx  = s * 0.50   # body centre x
    cy  = s * 0.52   # body centre y
    brx = s * 0.27   # body half-width
    bry = s * 0.17   # body half-height

    # Tail (two lobes, left of body)
    tx = cx - brx * 0.75
    fill_triangle(pixels, s, [
        (tx,              cy - bry * 0.1),
        (tx - brx * 0.6,  cy - bry * 1.45),
        (tx - brx * 0.05, cy - bry * 0.1),
    ], DARK)
    fill_triangle(pixels, s, [
        (tx,              cy + bry * 0.1),
        (tx - brx * 0.6,  cy + bry * 1.45),
        (tx - brx * 0.05, cy + bry * 0.1),
    ], DARK)

    # Body ellipse
    fill_ellipse(pixels, s, cx, cy, brx, bry, BODY)

    # Lighter belly (lower-front quadrant)
    fill_ellipse(pixels, s, cx + brx*0.08, cy + bry*0.22, brx*0.65, bry*0.52, BELLY)

    # Dorsal fin (top)
    fill_triangle(pixels, s, [
        (cx - brx*0.12, cy - bry*0.9),
        (cx + brx*0.22, cy - bry*0.9),
        (cx + brx*0.05, cy - bry*1.75),
    ], DARK)

    # Pectoral fin (belly, small)
    fill_triangle(pixels, s, [
        (cx + brx*0.05, cy + bry*0.7),
        (cx + brx*0.35, cy + bry*0.7),
        (cx + brx*0.2,  cy + bry*1.3),
    ], DARK)

    # Eye — white sclera
    ex = cx + brx * 0.52
    ey = cy - bry * 0.18
    er = bry * 0.26
    fill_circle(pixels, s, ex, ey, er, WHITE)
    # Pupil
    fill_circle(pixels, s, ex + er*0.18, ey, er*0.48, PUPIL)

    # Bubbles (upper right)
    for (bx, by, br) in [
        (cx + brx*1.05, cy - bry*1.4,  bry*0.14),
        (cx + brx*1.2,  cy - bry*1.85, bry*0.10),
        (cx + brx*1.35, cy - bry*1.3,  bry*0.08),
    ]:
        fill_circle(pixels, s, bx, by, br, BUBBLE)
        fill_circle(pixels, s, bx, by, max(1, br*0.55), BG)   # hollow ring

    return pixels

# ── Generate ──────────────────────────────────────────────────────────────────
os.makedirs("public/icons", exist_ok=True)
for size in [192, 512]:
    pix = draw_icon(size)
    with open(f"public/icons/icon-{size}.png", "wb") as f:
        f.write(make_png(size, size, pix))
    print(f"Created public/icons/icon-{size}.png ({size}x{size})")
