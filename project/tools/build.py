"""src/app.html + backgrounds/ → dist/index.html (PC용 단일 파일), dist/artifact.html (claude.ai 게시용)"""
import base64, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = os.path.join(ROOT, "backgrounds")
src = open(os.path.join(ROOT, "src", "app.html"), encoding="utf-8").read()
lib = []
for b in json.load(open(os.path.join(BG, "manifest.json"), encoding="utf-8")):
    data = base64.b64encode(open(os.path.join(BG, b["id"] + ".jpg"), "rb").read()).decode()
    lib.append({**b, "src": "data:image/jpeg;base64," + data})
full = src.replace("/*__BG_LIBRARY__*/[]", json.dumps(lib, ensure_ascii=False))
os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(full)

# 게시용: 문서 뼈대 태그 제거, head 내용 + body 내용만
head = re.search(r"<head>(.*?)</head>", full, re.S).group(1)
body = re.search(r"<body>(.*)</body>", full, re.S).group(1)
head = re.sub(r'<meta charset="utf-8">\s*|<meta name="viewport"[^>]*>\s*', "", head)
title = re.search(r"<title>.*?</title>", head).group(0)
head = head.replace(title, "")
art = title + '\n<meta name="claude:viewport-fit-sides" content="cover">\n' + head.strip() + "\n" + body.strip() + "\n"
open(os.path.join(ROOT, "dist", "artifact.html"), "w", encoding="utf-8").write(art)
for f in ("dist/artifact.html",):
    print(f, round(os.path.getsize(os.path.join(ROOT, f)) / 1e6, 2), "MB")

# 웹사이트용: 보안 정책(CSP) 추가 — 허용한 출처에서만 코드·파일을 불러옴
CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval' 'unsafe-eval' blob: https://cdn.jsdelivr.net https://staticimgly.com; "
       "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
       "img-src 'self' data: blob:; connect-src 'self' data: blob: https://cdn.jsdelivr.net https://staticimgly.com; "
       "worker-src 'self' blob:; object-src 'none'; base-uri 'none'; form-action 'none'")
site = full.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta http-equiv="Content-Security-Policy" content="' + CSP + '">\n<meta name="referrer" content="no-referrer">', 1)
os.makedirs(os.path.join(ROOT, "site"), exist_ok=True)
open(os.path.join(ROOT, "site", "index.html"), "w", encoding="utf-8").write(site)
print("site/index.html", round(len(site.encode()) / 1e6, 2), "MB")
