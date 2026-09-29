"""Extract a representative figure from a paper PDF for the site.

Not part of the site build (generate.py stays stdlib-only). Dev dependency:
    uv pip install pymupdf pillow

Usage:
    python scripts/extract_figure.py PAPER.pdf SLUG            # list candidates, save previews
    python scripts/extract_figure.py PAPER.pdf SLUG --pick N   # write assets/figures/SLUG.webp

Candidates come from "Fig. N" / "Figure N" / "그림 N" captions: the vector
drawings and images above (or below) each caption are merged into one crop.
Look at the previews in /tmp/figure-candidates/ and pick the figure that best
represents the paper (a concept diagram or vehicle picture usually beats a
result plot). Then add  "figure": "assets/figures/SLUG.webp"  to the paper in
papers.json. Only use a PDF of the paper itself, never private documents.
"""
import argparse
import io
import os
import re

import pymupdf
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CAP=re.compile(r'^\s*(Fig\.?|Figure|FIG\.?|FIGURE|그림)\s*(\d+)', re.I)
def figures(doc, maxpages=60):
    out=[]
    for pno,page in enumerate(doc):
        if pno>=maxpages: break
        W,H=page.rect.width,page.rect.height
        blocks=[b for b in page.get_text("blocks") if b[6]==0]
        gfx=[pymupdf.Rect(d["rect"]) for d in page.get_drawings() if d["rect"].width*d["rect"].height>4 or d["rect"].width>20 or d["rect"].height>20]
        gfx+=[pymupdf.Rect(i["bbox"]) for i in page.get_image_info()]
        gfx=[g&page.rect for g in gfx if g.width<W*0.97 and g.height<H*0.92 and not g.is_empty]
        if not gfx: continue
        for b in blocks:
            m=CAP.match(b[4])
            if not m or len(b[4])>400: continue
            cap=pymupdf.Rect(b[:4]); cx=(cap.x0+cap.x1)/2
            best=None
            for direction in ("above","below"):
                if direction=="above":
                    lim=max([pymupdf.Rect(t[:4]).y1 for t in blocks if pymupdf.Rect(t[:4]).y1<=cap.y0-1 and len(t[4].strip())>150 and pymupdf.Rect(t[:4]).x0<cx<pymupdf.Rect(t[:4]).x1]+[0])
                    sel=[g for g in gfx if g.y1<=cap.y0+3 and g.y0>=lim-3]
                else:
                    lim=min([pymupdf.Rect(t[:4]).y0 for t in blocks if pymupdf.Rect(t[:4]).y0>=cap.y1+1 and len(t[4].strip())>150 and pymupdf.Rect(t[:4]).x0<cx<pymupdf.Rect(t[:4]).x1]+[H])
                    sel=[g for g in gfx if g.y0>=cap.y1-3 and g.y1<=lim+3]
                # horizontal: graphics overlapping caption column
                half=max(cap.width/2+40, W*0.22)
                sel=[g for g in sel if g.x1>cx-half and g.x0<cx+half]
                if not sel: continue
                # cluster: grow from graphic nearest to caption
                sel.sort(key=lambda g: (cap.y0-g.y1) if direction=="above" else (g.y0-cap.y1))
                u=pymupdf.Rect(sel[0])
                changed=True
                while changed:
                    changed=False
                    for g in sel:
                        if not g in u and g.intersects(u+(-14,-14,14,14)) and not (u.contains(g)):
                            u|=g; changed=True
                        elif u.contains(g): pass
                # add text labels inside/adjacent
                for t in blocks:
                    r=pymupdf.Rect(t[:4])
                    if len(t[4].strip())<60 and r.intersects(u+(-8,-8,8,8)) and not CAP.match(t[4]): u|=r
                if u.width<70 or u.height<50: continue
                a=u.width*u.height/(W*H)
                if not best or a>best["area"]:
                    best=dict(page=pno,num=int(m.group(2)),rect=u,cap=b[4].strip().replace("\n"," ")[:200],area=a,dir=direction)
            if best: out.append(best)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("slug")
    ap.add_argument("--pick", type=int)
    args = ap.parse_args()
    doc = pymupdf.open(args.pdf)
    seen, figs = set(), []
    for f in figures(doc):
        if f["area"] > 0.05 and f["num"] not in seen:
            seen.add(f["num"])
            figs.append(f)
    if not figs:
        raise SystemExit("No captioned figures found; crop manually.")
    if args.pick is None:
        os.makedirs("/tmp/figure-candidates", exist_ok=True)
        for i, f in enumerate(figs):
            out = f"/tmp/figure-candidates/{args.slug}__{i}.png"
            doc[f["page"]].get_pixmap(clip=f["rect"] + (-4, -4, 4, 4), dpi=110).save(out)
            print(f"[{i}] page {f['page'] + 1}  Fig. {f['num']}  {f['cap'][:70]}  -> {out}")
        return
    f = figs[args.pick]
    pix = doc[f["page"]].get_pixmap(clip=f["rect"] + (-4, -4, 4, 4), dpi=220)
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    if im.width > 1200:
        im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
    out = os.path.join(ROOT, "assets", "figures", f"{args.slug}.webp")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, "WEBP", quality=82, method=6)
    print(f"wrote {out} ({im.width}x{im.height}); add \"figure\": \"assets/figures/{args.slug}.webp\" to papers.json")


if __name__ == "__main__":
    main()
