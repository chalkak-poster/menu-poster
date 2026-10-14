"""배경 라이브러리 생성기: 1080x1440 JPG 30장 + manifest.json
실서비스에서는 이 폴더를 AI로 생성한 이미지로 교체하면 된다."""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter

W, H = 1080, 1440
OUT = sys.argv[1] if len(sys.argv) > 1 else "backgrounds"
os.makedirs(OUT, exist_ok=True)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def noise(seed, sx=200, sy=None, octaves=5, pers=0.5, h=H, w=W):
    sy = sy or sx
    r = np.random.default_rng(seed); out = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for o in range(octaves):
        gw = max(2, int(w / sx * 2 ** o) + 2); gh = max(2, int(h / sy * 2 ** o) + 2)
        a = r.random((gh, gw)).astype(np.float32)
        out += np.asarray(Image.fromarray(a, "F").resize((w, h), Image.BICUBIC)) * amp
        tot += amp; amp *= pers
    return np.clip(out / tot, 0, 1)


def ramp(t, stops):
    t = np.clip(t, 0, 1); pos = [s[0] for s in stops]
    return np.stack([np.interp(t, pos, [s[1][c] for s in stops]) for c in range(3)], -1).astype(np.float32)


def col(hexs):
    return tuple(int(hexs[i:i + 2], 16) for i in (1, 3, 5))


def light(img, strength=0.18, angle=-0.6, vign=0.35):
    # 창가 빛(대각선 그라데이션) + 비네팅
    d = (XX / W) * math.cos(angle) + (YY / H) * math.sin(angle)
    d = (d - d.min()) / (d.max() - d.min())
    g = 1 + strength * (0.5 - d) * 2
    r = np.sqrt(((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    v = 1 - vign * np.clip(r - 0.25, 0, 1) ** 1.6
    return img * (g * v)[..., None]


def fine(img, seed, amt=6):
    return img + (np.random.default_rng(seed).random((H, W)).astype(np.float32)[..., None] - 0.5) * amt


def save(arr, name):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(f"{OUT}/{name}.jpg", quality=80, optimize=True, progressive=True)


# ───── 나무 ─────
def wood(seed, dark, mid, lightc, planks=6, vertical=False, wash=0.0):
    h, w = (W, H) if vertical else (H, W)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ph = h / planks; idx = np.floor(yy / ph); local = yy - idx * ph
    r = np.random.default_rng(seed)
    off = r.random(planks + 1)[idx.astype(int)] * 40; bright = 0.88 + r.random(planks + 1)[idx.astype(int)] * 0.2
    warp = noise(seed + 1, sx=700, sy=60, octaves=4, h=h, w=w)
    fib = noise(seed + 2, sx=300, sy=3, octaves=3, h=h, w=w)
    g = 0.5 + 0.5 * np.sin((local / 9 + warp * 9 + off) * 1.0)
    g = g ** 1.6 * 0.6 + fib * 0.4
    knots = noise(seed + 3, sx=180, octaves=2, h=h, w=w)
    g = g * (1 - 0.35 * np.clip((knots - 0.72) * 6, 0, 1))
    img = ramp(g, [(0, dark), (0.55, mid), (1, lightc)]) * bright[..., None]
    seam = np.clip(1 - np.abs(local - 0) / 3, 0, 1) + np.clip(1 - np.abs(local - ph) / 3, 0, 1)
    img *= (1 - 0.55 * seam)[..., None]
    if wash:
        wn = noise(seed + 4, sx=400, sy=40, octaves=4, h=h, w=w)
        img = img * (1 - wash * (0.6 + 0.4 * wn[..., None])) + np.array([238, 234, 226], np.float32) * wash * (0.6 + 0.4 * wn[..., None])
    if vertical: img = np.transpose(img, (1, 0, 2))
    return img


# ───── 돌 ─────
def marble(seed, base_a, base_b, vein, vein_amt=0.6, freq=0.006, sharp=10, black=False):
    t = noise(seed, sx=420, octaves=6)
    v = np.sin((XX * freq * 0.6 + YY * freq + t * 9) * math.pi)
    veins = (1 - np.abs(v)) ** sharp
    t2 = noise(seed + 7, sx=260, octaves=6)
    v2 = (1 - np.abs(np.sin((XX * freq * 1.3 - YY * freq * 0.4 + t2 * 12) * math.pi))) ** (sharp * 2.5)
    base = ramp(noise(seed + 9, sx=500, octaves=4), [(0, base_a), (1, base_b)])
    gate = np.clip((noise(seed + 11, sx=380, octaves=3) - 0.42) * 3.5, 0, 1)
    gate2 = np.clip((noise(seed + 12, sx=300, octaves=3) - 0.55) * 4, 0, 1)
    soft = gaussian_filter(veins * gate, 6) * 0.35
    m = np.clip(veins * gate * vein_amt + v2 * gate2 * vein_amt * 0.6 + soft * vein_amt, 0, 1)[..., None]
    img = base * (1 - m) + np.array(vein, np.float32) * m
    return img


def concrete(seed, a, b):
    n = noise(seed, sx=300, octaves=7, pers=0.6)
    img = ramp(n, [(0, a), (1, b)])
    pits = gaussian_filter((np.random.default_rng(seed).random((H, W)) > 0.9985).astype(np.float32), 1.2) * 6
    return img * (1 - np.clip(pits, 0, .5)[..., None])


def terrazzo(seed):
    img = ramp(noise(seed, sx=400, octaves=5), [(0, col("#efe7da")), (1, col("#f7f2ea"))])
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im); r = np.random.default_rng(seed)
    pal = ["#e07a5f", "#3d405b", "#81b29a", "#f2cc8f", "#c9b79c", "#8d99ae", "#d4a373"]
    for _ in range(900):
        cx, cy, s = r.random() * W, r.random() * H, 4 + r.random() ** 3 * 34
        pts = [(cx + math.cos(a) * s * (0.6 + r.random() * 0.6), cy + math.sin(a) * s * (0.6 + r.random() * 0.6)) for a in np.sort(r.random(6)) * 2 * math.pi]
        d.polygon(pts, fill=pal[r.integers(len(pal))])
    return np.asarray(im).astype(np.float32)


def slate(seed):
    n = noise(seed, sx=900, sy=90, octaves=6, pers=0.55)
    img = ramp(n, [(0, col("#26292c")), (0.6, col("#3a3e42")), (1, col("#4c5155"))])
    streak = noise(seed + 2, sx=600, sy=8, octaves=3)
    return img + (streak[..., None] - 0.5) * 14


def travertine(seed):
    n = noise(seed, sx=900, sy=40, octaves=6)
    img = ramp(n, [(0, col("#cdb89a")), (1, col("#e9dcc6"))])
    pits = gaussian_filter((np.random.default_rng(seed).random((H, W)) > 0.997).astype(np.float32), (0.8, 3)) * 5
    return img * (1 - np.clip(pits, 0, .35)[..., None])


# ───── 천 ─────
def linen(seed, base, wrinkle=0.02):
    r = np.random.default_rng(seed)
    rows = np.repeat(r.random(H)[:, None], W, 1); cols = np.repeat(r.random(W)[None, :], H, 0)
    weave = (rows + cols) / 2 - 0.5
    img = np.array(base, np.float32) * (1 + weave[..., None] * 0.12)
    wr = noise(seed + 1, sx=380, octaves=4)
    gy, gx = np.gradient(gaussian_filter(wr, 6))
    shade = 1 + np.clip((gx - gy) * 900 * wrinkle, -0.12, 0.12)
    return img * shade[..., None]


def gingham(seed, c, size=60):
    xs = ((XX // size) % 2 == 0); ys = ((YY // size) % 2 == 0)
    k = xs.astype(np.float32) * 0.5 + ys.astype(np.float32) * 0.5
    white = np.array([246, 243, 236], np.float32); cc = np.array(col(c), np.float32)
    img = white * (1 - k[..., None]) + cc * k[..., None]
    return linen(seed, (1, 1, 1), wrinkle=0.02) * img


# ───── 종이 ─────
def paper(seed, base, shadow=0.0, mottle=0.06):
    n = noise(seed, sx=500, octaves=5)
    fib = noise(seed + 1, sx=40, sy=6, octaves=2)
    img = np.array(base, np.float32) * (1 + (n[..., None] - 0.5) * mottle + (fib[..., None] - 0.5) * 0.03)
    if shadow:
        d = (XX + YY * 0.8) / (W + H * 0.8)
        m = np.clip((d - 0.52) * 7, 0, 1)
        img *= (1 - shadow * m)[..., None]
    return img


def kraft(seed):
    img = paper(seed, col("#b8956a"), mottle=0.05)
    cr = noise(seed + 5, sx=260, octaves=5)
    gy, gx = np.gradient(gaussian_filter(cr, 3))
    fibers = noise(seed + 6, sx=15, sy=15, octaves=2)
    return img * (1 + np.clip((gx - gy)[..., None] * 25, -0.05, 0.05)) * (1 + (fibers[..., None] - 0.5) * 0.12)


def hanji(seed):
    img = paper(seed, col("#f1ead9"), mottle=0.07)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay); r = np.random.default_rng(seed)
    for _ in range(1400):
        x, y = r.random() * W, r.random() * H; a = r.random() * math.pi; L = 20 + r.random() * 90
        pts = [(x + math.cos(a + math.sin(t * 3) * 0.3) * t * L, y + math.sin(a + math.sin(t * 3) * 0.3) * t * L) for t in np.linspace(0, 1, 8)]
        shade = (120, 100, 70, int(18 + r.random() * 28)) if r.random() < 0.5 else (255, 255, 250, int(40 + r.random() * 50))
        d.line(pts, fill=shade, width=1)
    im = Image.alpha_composite(im, lay.filter(ImageFilter.GaussianBlur(0.4)))
    return np.asarray(im.convert("RGB")).astype(np.float32)


# ───── 빛과 그림자 ─────
def dappled(seed, base, tint=(0.82, 0.86, 0.95), amt=0.32):
    n = noise(seed, sx=110, octaves=5, pers=0.6)
    big = noise(seed + 9, sx=500, octaves=2)
    m = gaussian_filter(np.clip((n - 0.47) * 7, 0, 1) * np.clip((big - 0.3) * 2.5, 0, 1), 4)
    img = paper(seed + 3, base, mottle=0.04)
    t = np.array(tint, np.float32)
    return img * (1 - m[..., None] * amt * (1.25 - t) * 1.6)


def palm_shadow(seed, base):
    mask = Image.new("L", (W, H), 0); d = ImageDraw.Draw(mask); r = np.random.default_rng(seed)
    for _ in range(3):
        sx, sy = (r.random() * 0.4 - 0.1) * W, (r.random() * 0.5 - 0.1) * H; ang = 0.6 + r.random() * 0.4
        L = 1100 + r.random() * 400
        for t in np.linspace(0.05, 1, 30):
            px, py = sx + math.cos(ang) * L * t, sy + math.sin(ang) * L * t
            for side in (-1, 1):
                a2 = ang + side * (1.0 + r.random() * 0.2); ll = 200 * math.sin(t * math.pi) + 40
                d.line([(px, py), (px + math.cos(a2) * ll, py + math.sin(a2) * ll)], fill=255, width=int(14 + 8 * math.sin(t * math.pi)))
        d.line([(sx, sy), (sx + math.cos(ang) * L, sy + math.sin(ang) * L)], fill=255, width=10)
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(9))).astype(np.float32) / 255
    img = paper(seed, base, mottle=0.04)
    return img * (1 - m[..., None] * np.array([0.22, 0.26, 0.34], np.float32))


def spotlight(seed):
    n = noise(seed, sx=250, octaves=6, pers=0.6)
    img = ramp(n, [(0, col("#141414")), (1, col("#2d2b29"))])
    r = np.sqrt(((XX - W / 2) / W) ** 2 + ((YY - H * 0.45) / H) ** 2)
    return img * (0.55 + 1.3 * np.exp(-(r / 0.32) ** 2))[..., None]


def smoke(seed):
    q = noise(seed, sx=300, octaves=4); q2 = noise(seed + 1, sx=300, octaves=4)
    wx = (XX + q * 260).astype(int) % W; wy = (YY + q2 * 260).astype(int) % H
    n = noise(seed + 2, sx=220, octaves=6)[wy, wx]
    r = np.sqrt(((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2)
    m = np.clip((n - 0.45) * 2.2, 0, 1) ** 1.5 * np.clip((r - 0.45) * 1.6, 0, 1)
    base = np.full((H, W, 3), 10, np.float32)
    return base + m[..., None] * np.array([150, 150, 155], np.float32)


def bokeh(seed, top, bottom, colors, count=70, blur=22):
    img = Image.fromarray(np.clip(ramp(YY / H, [(0, top), (1, bottom)]), 0, 255).astype(np.uint8)).convert("RGBA")
    r = np.random.default_rng(seed)
    for layer, (n, bl) in enumerate([(count, blur), (count // 2, blur // 3)]):
        lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
        for _ in range(n):
            x, y = r.random() * W, (r.random() ** 1.6) * H * 0.85; s = 20 + r.random() * (110 if layer == 0 else 45)
            c = col(colors[r.integers(len(colors))]); d.ellipse([x - s, y - s, x + s, y + s], fill=c + (int(60 + r.random() * 110),))
        img = Image.alpha_composite(img, lay.filter(ImageFilter.GaussianBlur(bl)))
    return np.asarray(img.convert("RGB")).astype(np.float32)


def caustics(seed):
    n1 = noise(seed, sx=260, octaves=3); n2 = noise(seed + 1, sx=180, octaves=3)
    c = (1 - np.abs(np.sin(n1 * 26))) ** 10 + (1 - np.abs(np.sin(n2 * 22 + 1))) ** 12
    c = gaussian_filter(c, 1.2)
    base = ramp(noise(seed + 2, sx=600, octaves=3), [(0, col("#1b9aaa")), (1, col("#4fc6c9"))])
    return base + c[..., None] * np.array([120, 140, 120], np.float32)


# ───── 테두리 장식 ─────
def edge_points(r, n, inner=0.62):
    pts = []
    while len(pts) < n:
        x, y = r.random(), r.random()
        e = max(abs(x - 0.5) * 2, abs(y - 0.5) * 2)
        if e > inner + r.random() * 0.25: pts.append((x * W, y * H))
    return pts


def scatter(base_arr, seed, n, draw_fn, shadow=(0, 10, 0.35)):
    base = Image.fromarray(np.clip(base_arr, 0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H)); r = np.random.default_rng(seed)
    for (x, y) in edge_points(r, n):
        draw_fn(lay, x, y, r)
    a = lay.split()[3]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.putalpha(a.point(lambda v: int(v * shadow[2])))
    sh = sh.transform((W, H), Image.AFFINE, (1, 0, -shadow[0], 0, 1, -shadow[1])).filter(ImageFilter.GaussianBlur(7))
    out = Image.alpha_composite(Image.alpha_composite(base, sh), lay)
    return np.asarray(out.convert("RGB")).astype(np.float32)


def petal(lay, x, y, r):
    s = 24 + r.random() * 26; p = Image.new("RGBA", (int(s * 3), int(s * 3))); d = ImageDraw.Draw(p)
    c = (250, 196 + int(r.random() * 25), 210 + int(r.random() * 20), 255)
    d.ellipse([s * 0.6, s * 0.4, s * 2.4, s * 2.6], fill=c); d.polygon([(s * 1.5, s * 0.4), (s * 1.3, s * 0.1), (s * 1.7, s * 0.1)], fill=(0, 0, 0, 0))
    p = p.rotate(r.random() * 360, expand=True, resample=Image.BICUBIC)
    lay.alpha_composite(p, (int(x - p.width / 2) % W, int(y - p.height / 2) % H))


def leaf(lay, x, y, r):
    s = 40 + r.random() * 45; p = Image.new("RGBA", (int(s * 2.4), int(s * 2.4))); d = ImageDraw.Draw(p); c0 = s * 1.2
    cols = [(214, 92, 38), (232, 150, 40), (180, 50, 35), (240, 190, 70), (150, 60, 30)]
    c = cols[r.integers(len(cols))]
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * 2 * math.pi / 10; rad = s * (1.0 if i % 2 == 0 else 0.62)
        if i in (5,): rad = s * 0.35
        pts.append((c0 + math.cos(a) * rad, c0 + math.sin(a) * rad))
    d.polygon(pts, fill=c + (255,))
    for i in (0, 2, 8): a = -math.pi / 2 + i * 2 * math.pi / 10; d.line([(c0, c0), (c0 + math.cos(a) * s * 0.9, c0 + math.sin(a) * s * 0.9)], fill=tuple(int(v * 0.75) for v in c) + (255,), width=2)
    d.line([(c0, c0), (c0, c0 + s * 1.1)], fill=(110, 60, 30, 255), width=3)
    p = p.rotate(r.random() * 360, expand=True, resample=Image.BICUBIC)
    lay.alpha_composite(p, (int(x - p.width / 2) % W, int(y - p.height / 2) % H))


def pine(lay, x, y, r):
    d = ImageDraw.Draw(lay); ang = r.random() * 2 * math.pi; L = 120 + r.random() * 120
    for t in np.linspace(0, 1, 40):
        px, py = x + math.cos(ang) * L * t, y + math.sin(ang) * L * t
        for side in (-1, 1):
            a2 = ang + side * 0.9; ll = 28 * (1 - t * 0.5)
            g = (30 + int(r.random() * 30), 80 + int(r.random() * 40), 45 + int(r.random() * 20), 255)
            d.line([(px, py), (px + math.cos(a2) * ll, py + math.sin(a2) * ll)], fill=g, width=3)
    if r.random() < 0.6:
        for _ in range(3):
            bx, by = x + (r.random() - 0.5) * 60, y + (r.random() - 0.5) * 60
            d.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=(190, 25, 35, 255)); d.ellipse([bx - 4, by - 6, bx, by - 2], fill=(255, 140, 140, 255))


# ───── 라이브러리 정의 ─────
LIB = [
    ("oak", "오크 원목", "나무", lambda: light(fine(wood(11, col("#5a3a22"), col("#8a5d38"), col("#b8875a")), 1), 0.25)),
    ("ash", "밝은 원목", "나무", lambda: light(fine(wood(12, col("#b08d66"), col("#d2b48c"), col("#e8d3b0"), planks=5), 2), 0.15, vign=0.2)),
    ("walnut", "월넛", "나무", lambda: light(fine(wood(13, col("#2a1a10"), col("#4a2e1c"), col("#6f4a30"), planks=7), 3), 0.2, vign=0.5)),
    ("whitewash", "화이트워시 나무", "나무", lambda: light(fine(wood(14, col("#8b6d50"), col("#a88a6a"), col("#c8ad8c"), planks=6, vertical=True, wash=0.72), 4), 0.12, vign=0.18)),
    ("board", "도마 세로결", "나무", lambda: light(fine(wood(15, col("#7a4f2b"), col("#a87444"), col("#cf9a62"), planks=4, vertical=True), 5), 0.2)),
    ("marble", "화이트 대리석", "돌", lambda: light(fine(marble(21, col("#e9e7e4"), col("#f7f6f4"), col("#8e8e98"), 0.55, freq=0.0028, sharp=7), 6, 3), 0.1, vign=0.15)),
    ("blackmarble", "블랙 골드 대리석", "돌", lambda: light(fine(marble(22, col("#111214"), col("#23252a"), col("#c9a35a"), 0.9, freq=0.0026, sharp=9), 7, 4), 0.15, vign=0.3)),
    ("concrete", "콘크리트", "돌", lambda: light(fine(concrete(23, col("#8f9190"), col("#b9bab6")), 8, 8), 0.18, vign=0.3)),
    ("terrazzo", "테라조", "돌", lambda: light(fine(terrazzo(24), 9, 4), 0.1, vign=0.15)),
    ("slate", "슬레이트", "돌", lambda: light(fine(slate(25), 10, 6), 0.2, vign=0.4)),
    ("travertine", "트래버틴", "돌", lambda: light(fine(travertine(26), 11, 4), 0.14, vign=0.25)),
    ("linen", "베이지 리넨", "천", lambda: light(fine(linen(31, col("#e3d8c4")), 12, 4), 0.12, vign=0.22)),
    ("navylinen", "네이비 리넨", "천", lambda: light(fine(linen(32, col("#2c3e5c")), 13, 4), 0.2, vign=0.35)),
    ("gingham", "레드 깅엄", "천", lambda: light(fine(gingham(33, "#c8323a"), 14, 4), 0.12, vign=0.25)),
    ("kraft", "크라프트지", "종이", lambda: light(fine(kraft(41), 15, 5), 0.15, vign=0.25)),
    ("hanji", "한지", "종이", lambda: light(hanji(42), 0.08, vign=0.15)),
    ("pink", "파스텔 핑크", "종이", lambda: light(paper(43, col("#f6d3d5"), shadow=0.1), 0.06, vign=0.1)),
    ("mint", "파스텔 민트", "종이", lambda: light(paper(44, col("#cdeadd"), shadow=0.1), 0.06, vign=0.1)),
    ("lavender", "라벤더", "종이", lambda: light(paper(45, col("#ddd5ef"), shadow=0.08), 0.06, vign=0.1)),
    ("cream", "크림 화이트", "종이", lambda: light(paper(46, col("#f5f0e6"), shadow=0.07), 0.06, vign=0.12)),
    ("spotlight", "스포트라이트", "분위기", lambda: fine(spotlight(51), 16, 4)),
    ("smoke", "스모크 블랙", "분위기", lambda: fine(smoke(52), 17, 3)),
    ("cafebokeh", "카페 조명", "분위기", lambda: fine(bokeh(53, col("#3b2416"), col("#1a0f09"), ["#ffcf7a", "#ffb15c", "#ffe2a8", "#f59a4a"]), 18, 3)),
    ("nightbokeh", "밤 조명", "분위기", lambda: fine(bokeh(54, col("#141b33"), col("#070a15"), ["#7aa2ff", "#b07aff", "#ff7ad1", "#7ae0ff"]), 19, 3)),
    ("leafshadow", "나뭇잎 그림자", "계절", lambda: light(dappled(61, col("#f6f4ef")), 0.06, vign=0.12)),
    ("palm", "야자수 그림자", "계절", lambda: light(palm_shadow(62, col("#f8dc7a")), 0.08, vign=0.15)),
    ("cherry", "벚꽃", "계절", lambda: scatter(light(paper(63, col("#fbe6e8")), 0.05, vign=0.1), 63, 90, petal, (4, 8, 0.25))),
    ("autumn", "가을 단풍", "계절", lambda: scatter(light(fine(wood(64, col("#5a3a22"), col("#7d5434"), col("#a67b52")), 20), 0.2), 64, 60, leaf, (6, 10, 0.4))),
    ("christmas", "크리스마스", "계절", lambda: scatter(fine(bokeh(65, col("#163a2a"), col("#0c2419"), ["#ffd27a", "#ffe9b0"], count=30, blur=26), 21, 4), 65, 45, pine, (5, 9, 0.45))),
    ("water", "여름 물결", "계절", lambda: light(caustics(66), 0.1, vign=0.2)),
]

manifest = []
for key, name, cat, fn in LIB:
    arr = fn()
    save(arr, key)
    small = np.asarray(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((40, 54)), np.float32)
    L = float((small[..., 0] * .299 + small[..., 1] * .587 + small[..., 2] * .114).mean())
    manifest.append({"id": key, "name": name, "cat": cat, "tone": "light" if L > 140 else "dark"})
    print(key, round(L))
json.dump(manifest, open(f"{OUT}/manifest.json", "w"), ensure_ascii=False, indent=1)
