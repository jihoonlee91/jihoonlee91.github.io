# jihoonlee91.github.io

**Live site: https://jihoonlee91.github.io**

Jihoon Lee의 개인 학술 홈페이지(논문 목록, CV, 연락처). `papers.json`이 데이터 원본이고, `generate.py` + `viz.py`가 이를 정적 HTML/SVG/BibTeX으로 빌드합니다.

자세한 설계/운영 문서는 [`docs/`](docs/) 폴더를 참고하세요:

- [`docs/DESIGN.md`](docs/DESIGN.md) — 디자인 시스템 (색상, 폰트, 다크/라이트 테마, 반응형 브레이크포인트)
- [`docs/CONTENT_GUIDE.md`](docs/CONTENT_GUIDE.md) — 논문/PDF/CV 추가·수정 방법
- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) — 데이터 출처(Google Scholar, ORCID, weebly, DBpia 등)와 한계
- [`docs/CONTENT_POLICY.md`](docs/CONTENT_POLICY.md) — **콘텐츠 게시 전 영업비밀/기밀정보 체크 규칙 (필독)**

Claude Code로 이 리포를 다룰 때는 [`CLAUDE.md`](CLAUDE.md)를 먼저 읽으세요.

## 빠른 시작

```bash
# papers.json 수정 후
python generate.py
git add -A && git commit -m "..." && git push
```

`main`에 push하면 `.github/workflows/build.yml`이 자동으로 `generate.py`를 실행하고 GitHub Pages에 배포합니다.

## 아직 채워야 할 정보 (papers.json)

- `email`: 실제 연락처 이메일 (현재 비어 있음)
- `cv_url`: 별도 CV PDF 링크가 필요하면 채우기 (지금은 LinkedIn/CV 페이지로 대체 예정)
