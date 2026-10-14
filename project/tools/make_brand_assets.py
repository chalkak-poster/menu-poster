"""파비콘(32/48), 홈 화면 아이콘(180), 공유 미리보기 이미지(1200x630) 생성.
사용: python tools/make_brand_assets.py <포스터 예시 PNG 경로>
(Noto Sans CJK 글꼴 경로는 PC 환경에 맞게 BLACK/BOLD/REG 값을 바꿔 주세요)"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site")
GREEN, GOLD, CREAM, INK = (31, 90, 74), (227, 162, 26), (243, 244, 241), (28, 36, 34)
BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
KR = 1  # ttc 안의 KR 글꼴 번호


def font(path, size):
    try: return ImageFont.truetype(path, size, index=KR)
    except Exception: return ImageFont.truetype(path, size)


def icon(size):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=GREEN)
    r = s * 0.30; c = s / 2  # 셔터 원 + 금색 점: "찰칵"
    d.ellipse([c - r, c - r, c + r, c + r], outline=CREAM, width=int(s * 0.075))
    rr = s * 0.10; d.ellipse([c - rr, c - rr, c + rr, c + rr], fill=GOLD)
    return im.resize((size, size), Image.LANCZOS)


def og(poster_path):
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 18, H], fill=GREEN)
    ic = icon(84); im.paste(ic, (80, 92), ic)
    d.text((184, 98), "찰칵", font=font(BLACK, 66), fill=INK)
    w = d.textlength("찰칵", font=font(BLACK, 66))
    d.text((184 + w, 98), "포스터", font=font(BLACK, 66), fill=GOLD)
    d.text((80, 232), "메뉴 사진 한 장으로", font=font(BOLD, 50), fill=INK)
    d.text((80, 296), "매장 포스터 완성", font=font(BOLD, 50), fill=INK)
    y = 400
    for t in ["AI 누끼 · 배경 30종 · 템플릿", "사진은 서버로 전송되지 않아요"]:
        d.text((82, y), t, font=font(REG, 28), fill=(95, 106, 102)); y += 44
    d.text((82, 548), "행운랩스 서비스", font=font(BOLD, 24), fill=GREEN)
    if poster_path and os.path.exists(poster_path):
        p = Image.open(poster_path).convert("RGB"); ph = 540; pw = int(p.width * ph / p.height); p = p.resize((pw, ph), Image.LANCZOS)
        x0 = W - pw - 90; y0 = 45
        sh = Image.new("RGBA", (pw + 60, ph + 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([30, 36, pw + 30, ph + 36], fill=(0, 0, 0, 90))
        sh = sh.filter(ImageFilter.GaussianBlur(14)); im.paste(sh, (x0 - 30, y0 - 30), sh)
        im.paste(p, (x0, y0))
    im.save(os.path.join(OUT, "og-image.png"), optimize=True)


os.makedirs(OUT, exist_ok=True)
for n in (32, 48): icon(n).save(os.path.join(OUT, f"favicon-{n}.png"))
ico = icon(180); bg = Image.new("RGB", (180, 180), GREEN); bg.paste(ico, (0, 0), ico); bg.save(os.path.join(OUT, "apple-touch-icon.png"))
og(sys.argv[1] if len(sys.argv) > 1 else None)
print("assets ok")
