"""site/ 에 이용약관 · 개인정보처리방침 · 오픈소스 라이선스 페이지 생성.
사업자 정보는 등록 후 BIZ 값을 채우고 다시 실행하면 됩니다."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site")
BIZ = dict(name="행운랩스", ceo="[대표자]", no="[사업자등록번호]", sale="[통신판매업 신고번호]",
           addr="[주소]", tel="[전화번호]", mail="[이메일]", officer="[개인정보 보호책임자]", date="[시행일]")
SITE = "https://chalkak-poster.github.io/menu-poster/"
REPO = "https://github.com/chalkak-poster/menu-poster"

HEAD = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; script-src 'none'; base-uri 'none'; form-action 'none'">
<title>{title} — 찰칵포스터</title>
<meta name="theme-color" content="#0c1311">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=IBM+Plex+Sans+KR:wght@400;600;700&display=swap">
<style>
:root{{--bg:#0c1311;--panel:#1c2421;--ink:#eaf0ed;--muted:#a2b2ab;--line:#2d3834;--accent:#5fbfa0;--pop:#f0b93a;color-scheme:dark;
  --f-display:"Black Han Sans","IBM Plex Sans KR",system-ui,sans-serif;--f-ui:"IBM Plex Sans KR","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.75 var(--f-ui);
  padding:24px max(16px,env(safe-area-inset-right,0px)) 48px max(16px,env(safe-area-inset-left,0px))}}
main{{max-width:760px;margin:0 auto}}
.back{{display:inline-block;color:var(--accent);text-decoration:none;font-weight:600;margin-bottom:18px}}
.logo{{font:400 24px/1 var(--f-display)}} .logo b{{color:var(--pop);font-weight:400}}
h1{{font-size:24px;margin:14px 0 4px}} .eff{{color:var(--muted);font-size:13px;margin:0 0 22px}}
h2{{font-size:16px;margin:26px 0 6px}} p,li{{margin:6px 0}} ul,ol{{padding-left:20px}}
table{{width:100%;border-collapse:collapse;font-size:14px;margin:8px 0}} th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}}
th{{background:var(--panel)}} .wrap{{overflow-x:auto}}
a{{color:var(--accent)}}
footer{{max-width:760px;margin:40px auto 0;padding-top:16px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}}
</style>
</head>
<body>
<main>
<a class="back" href="./">← 찰칵포스터로 돌아가기</a>
<div class="logo">찰칵<b>포스터</b></div>
<h1>{title}</h1>
<p class="eff">{eff}</p>
"""
FOOT = """</main>
<footer>찰칵포스터 · {name} 서비스<br>© 2026 {name}. All rights reserved.</footer>
</body>
</html>
"""


def page(fn, title, body, eff=None):
    eff = eff or f"시행일: {BIZ['date']}"
    html = HEAD.format(title=title, eff=eff) + body.format(**BIZ, site=SITE, repo=REPO) + FOOT.format(**BIZ)
    open(os.path.join(OUT, fn), "w", encoding="utf-8").write(html)
    print(fn)


TERMS = """
<h2>제1조 (목적)</h2>
<p>이 약관은 {name}(이하 "회사")가 제공하는 찰칵포스터 서비스(이하 "서비스")의 이용 조건과 절차, 회사와 이용자의 권리·의무를 정합니다.</p>

<h2>제2조 (서비스 내용)</h2>
<p>서비스는 이용자가 올린 메뉴 사진으로 매장 홍보용 포스터를 만드는 웹 도구입니다. 사진 보정, 음식 오려내기(누끼), 배경·템플릿 선택, 이미지 저장 기능을 무료로 제공합니다.</p>
<p>모든 처리는 이용자 기기의 브라우저 안에서 이루어지며, 회사는 이용자가 올린 사진과 입력한 문구를 받거나 저장하지 않습니다.</p>

<h2>제3조 (이용자 콘텐츠)</h2>
<ol>
<li>이용자가 올린 사진과 입력한 문구(이하 "이용자 콘텐츠")에 대한 권리와 책임은 이용자에게 있습니다.</li>
<li>이용자는 타인의 저작권, 초상권, 상표권 등 권리를 침해하는 사진이나 문구를 사용해서는 안 됩니다.</li>
<li>이용자는 포스터에 넣는 가격, 원산지, 효능 등 표시·광고 내용이 관련 법령(식품 등의 표시·광고에 관한 법률 등)에 맞도록 스스로 확인해야 합니다.</li>
</ol>

<h2>제4조 (결과물의 이용)</h2>
<ol>
<li>이용자는 서비스로 만든 포스터를 매장 게시, 온라인 홍보 등 상업적 목적을 포함해 자유롭게 이용할 수 있습니다.</li>
<li>서비스가 제공하는 배경 이미지와 템플릿 디자인은 이용자가 만든 포스터의 일부로만 이용할 수 있으며, 배경 이미지만 따로 떼어 판매하거나 재배포할 수 없습니다.</li>
</ol>

<h2>제5조 (서비스의 변경·중단)</h2>
<p>회사는 운영상·기술상 필요에 따라 서비스의 전부 또는 일부를 변경하거나 중단할 수 있으며, 중요한 변경은 서비스 화면에 미리 알립니다.</p>

<h2>제6조 (책임의 한계)</h2>
<ol>
<li>AI 오려내기와 자동 보정 결과는 사진 상태와 기기 성능에 따라 달라질 수 있으며, 회사는 결과물의 완전성을 보증하지 않습니다. 이용자는 저장 전 결과물을 직접 확인해야 합니다.</li>
<li>이용자 콘텐츠로 인해 발생한 분쟁에 대해 회사는 고의 또는 중대한 과실이 없는 한 책임을 지지 않습니다.</li>
</ol>

<h2 id="refund">제7조 (유료 서비스와 환불)</h2>
<p>현재 서비스는 모두 무료입니다. 유료 기능을 도입하는 경우 가격, 결제 방법, 청약철회와 환불 기준을 이 약관과 결제 화면에 미리 알리며, 「전자상거래 등에서의 소비자보호에 관한 법률」을 따릅니다.</p>

<h2>제8조 (준거법과 관할)</h2>
<p>이 약관은 대한민국 법을 따르며, 서비스 이용과 관련한 분쟁은 민사소송법에 따른 관할 법원에서 해결합니다.</p>

<h2>부칙</h2>
<p>이 약관은 {date}부터 시행합니다.</p>
<p>문의: {mail} · {tel}</p>
"""

PRIVACY = """
<p>{name}(이하 "회사")는 「개인정보 보호법」에 따라 이용자의 개인정보를 보호하고 관련 고충을 원활하게 처리하기 위해 다음과 같이 개인정보처리방침을 둡니다.</p>

<h2>1. 처리하는 개인정보</h2>
<p>찰칵포스터는 회원가입, 로그인, 결제 기능이 없으며, <b>회사는 이용자의 개인정보를 수집하거나 저장하지 않습니다.</b></p>
<ul>
<li>이용자가 올린 사진과 입력한 상호·메뉴·가격 등 문구는 이용자 기기의 브라우저 안에서만 처리되며, 회사 서버로 전송되지 않습니다.</li>
<li>회사는 쿠키, 광고·분석 도구를 사용하지 않습니다.</li>
</ul>

<h2>2. 서비스 제공을 위해 접속하는 외부 서비스</h2>
<p>웹페이지와 기능 파일을 불러오는 과정에서 이용자의 브라우저가 아래 서비스에 직접 접속하며, 이때 접속 IP 주소와 브라우저 정보 등이 각 사업자에게 전달될 수 있습니다. 회사는 이 정보를 받거나 보관하지 않으며, 각 사업자의 개인정보처리방침이 적용됩니다.</p>
<div class="wrap"><table>
<tr><th>서비스</th><th>용도</th><th>사업자 (소재 국가)</th></tr>
<tr><td>GitHub Pages</td><td>웹사이트 호스팅</td><td>GitHub, Inc. (미국)</td></tr>
<tr><td>jsDelivr</td><td>AI 오려내기 프로그램 전송</td><td>jsDelivr / Prospect One (폴란드)</td></tr>
<tr><td>staticimgly.com</td><td>AI 오려내기 모델 파일 전송</td><td>IMG.LY GmbH (독일)</td></tr>
<tr><td>Google Fonts</td><td>글꼴 전송</td><td>Google LLC (미국)</td></tr>
</table></div>

<h2>3. 보관 및 파기</h2>
<p>회사는 개인정보를 보관하지 않습니다. 이용자가 올린 사진과 작업 내용은 브라우저 탭을 닫거나 새로고침하면 기기에서도 사라집니다. 저장한 포스터 파일은 이용자 기기에만 남습니다.</p>

<h2>4. 이용자의 권리</h2>
<p>이용자는 언제든지 개인정보 열람·정정·삭제·처리정지를 요구할 수 있습니다. 회사는 개인정보를 보유하지 않으므로, 요청 시 그 사실을 확인해 드립니다.</p>

<h2>5. 개인정보 보호책임자</h2>
<p>책임자: {officer} · 이메일: {mail} · 전화: {tel}</p>
<p>개인정보 침해에 대한 신고나 상담은 개인정보침해신고센터(privacy.kisa.or.kr, 국번 없이 118), 개인정보분쟁조정위원회(kopico.go.kr, 1833-6972)에 문의할 수 있습니다.</p>

<h2>6. 방침의 변경</h2>
<p>회원가입, 결제 등 개인정보를 처리하는 기능을 도입하면 이 방침을 개정하며, 시행 7일 전에 서비스 화면으로 알립니다.</p>
<p>이 방침은 {date}부터 시행합니다.</p>
"""

LICENSES = """
<p>찰칵포스터는 아래 오픈소스 소프트웨어와 글꼴을 사용합니다. 감사합니다.</p>
<div class="wrap"><table>
<tr><th>이름</th><th>용도</th><th>라이선스</th></tr>
<tr><td><a href="https://github.com/imgly/background-removal-js">@imgly/background-removal</a></td><td>AI 음식 오려내기</td><td>AGPL-3.0</td></tr>
<tr><td><a href="https://github.com/microsoft/onnxruntime">ONNX Runtime Web</a></td><td>AI 모델 실행</td><td>MIT</td></tr>
<tr><td>Black Han Sans, Gowun Dodum, IBM Plex Sans KR, Nanum Myeongjo, Nanum Pen Script</td><td>화면·포스터 글꼴 (Google Fonts)</td><td>SIL Open Font License 1.1</td></tr>
</table></div>
<h2>소스 코드</h2>
<p>AGPL-3.0 라이선스에 따라 찰칵포스터 웹사이트의 전체 소스 코드를 공개합니다: <a href="{repo}">{repo}</a></p>
"""

os.makedirs(OUT, exist_ok=True)
page("terms.html", "이용약관", TERMS)
page("privacy.html", "개인정보처리방침", PRIVACY)
page("licenses.html", "오픈소스 라이선스", LICENSES, eff="찰칵포스터가 사용하는 오픈소스")
