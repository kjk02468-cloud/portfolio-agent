// 브라우저에서 "미국 주식 포트폴리오 관리.html" 열고 F12 콘솔에 붙여넣기 → Enter
// 옛 종목(MRCY·VICR 등)을 portfolio.md 기준 최신 7종목으로 통째 교체
localStorage.setItem('j1_portfolio', JSON.stringify([
  {ticker:'OKLO', avg:65,   qty:47,  price:65.39,  sector:'Energy',     memo:'SMR 에너지 · 1단계',          dailyChg:0},
  {ticker:'IONQ', avg:69,   qty:55,  price:56.78,  sector:'Technology', memo:'양자컴퓨팅 · 2단계',          dailyChg:0},
  {ticker:'USAR', avg:28.3, qty:140, price:22.47,  sector:'Materials',  memo:'희토류/핵심광물 · 2단계',     dailyChg:0},
  {ticker:'NBIS', avg:237,  qty:12,  price:227.81, sector:'Technology', memo:'AI 클라우드 · 3단계',         dailyChg:0},
  {ticker:'PATH', avg:12,   qty:160, price:11.24,  sector:'Technology', memo:'AI 자동화·에이전틱 · 3단계',  dailyChg:0},
  {ticker:'TLS',  avg:4.7,  qty:290, price:4.14,   sector:'Technology', memo:'정부 사이버보안 · 3단계',     dailyChg:0},
  {ticker:'ALAB', avg:267,  qty:8,   price:317.06, sector:'Technology', memo:'AI 인터커넥트 · 4단계',       dailyChg:0},
]));
location.reload();
