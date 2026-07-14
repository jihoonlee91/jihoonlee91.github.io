# jihoonlee91.github.io

Jihoon Lee 개인 논문/이력 홈페이지. `papers.json`이 데이터 원본이고, `generate.py`가 이를 정적 HTML/BibTeX으로 빌드합니다.

## 로컬에서 수정하는 법

1. `papers.json`을 수정합니다 (논문 추가/수정, `official_link`, `doi`, `education`, `experience`, `projects`, `email` 등).
2. `python generate.py` 실행 → `index.html`, `papers/*.html`, `bibtex/*.bib`, `sitemap.xml`, `robots.txt`가 재생성됩니다.
3. `git add -A && git commit -m "..." && git push`

`main` 브랜치에 push하면 `.github/workflows/build.yml`이 자동으로 `generate.py`를 실행하고 결과를 커밋한 뒤 GitHub Pages에 배포합니다. 즉 **papers.json만 고쳐서 push해도 사이트가 자동으로 갱신**됩니다.

## 논문 PDF 추가하는 법

원문 링크가 없는 논문은 PDF를 직접 올릴 수 있습니다.

1. PDF 파일을 `papers/pdfs/<slug>.pdf` 이름으로 저장합니다. `<slug>`는 `papers.json`의 해당 논문 `slug` 값과 정확히 일치해야 합니다 (예: `papers/pdfs/2018-sliding-mode-uav-carrier-landing.pdf`).
2. `python generate.py`를 다시 실행하면 해당 논문 페이지에 자동으로 "PDF 다운로드" 버튼과 `citation_pdf_url` 메타 태그가 생기고, index 페이지의 "(PDF 준비 중)" 표시가 사라집니다.
3. 저작권상 PDF를 올릴 수 없는 논문은 `official_link`에 출판사/DOI 링크를 채워주면 됩니다.

## GitHub Pages 최초 설정

1. GitHub에 `jihoonlee91.github.io` 라는 이름으로 새 저장소를 만듭니다 (이 이름이어야 `https://jihoonlee91.github.io`로 바로 서비스됩니다).
2. 이 폴더 내용을 그 저장소의 `main` 브랜치에 push합니다.
3. 저장소 Settings → Pages → Source를 **GitHub Actions**로 설정합니다.
4. push 후 Actions 탭에서 빌드/배포가 끝나면 `https://jihoonlee91.github.io`에서 확인할 수 있습니다.

## Google Scholar가 논문을 잘 색인하게 하려면

- 각 논문은 `papers/<slug>.html`이라는 자체 랜딩 페이지를 가지며, `<head>`에 `citation_title`, `citation_author`, `citation_pdf_url` 등 Highwire Press 태그가 자동으로 들어갑니다.
- PDF는 순수 `<a href="...pdf">` 링크로 걸려 있어 크롤러가 문제없이 인식합니다.
- `robots.txt`와 `sitemap.xml`이 자동 생성되어 크롤링을 막지 않습니다.
- 색인엔 보통 며칠~몇 주가 걸릴 수 있습니다.

## 아직 채워야 할 정보 (papers.json)

- `email`: 실제 연락처 이메일
- `cv_url`: CV PDF 링크 (기존 `github.com/jihoonlee91/CV` 링크는 404라 다시 확인 필요)
- `education`, `experience`, `projects`: 현재 빈 배열이며, 아래 형식으로 채우면 index.html에 자동 반영됩니다.

```json
"education": [
  {"school": "Seoul National University", "degree": "M.S. in Aerospace Engineering", "period": "2021-2023"}
],
"experience": [
  {"organization": "Samsung Electronics", "position": "Engineer", "period": "2023-현재"}
],
"projects": [
  {"title": "프로젝트명", "description": "한 줄 설명", "period": "2023"}
]
```
