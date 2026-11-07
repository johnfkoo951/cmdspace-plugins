#!/usr/bin/env python3
"""
eagle_sheet.py — 라이브러리의 폴더(또는 미분류)를 번호 붙인 모아보기 시트로 만든다 (읽기 전용, 분류 작업용).

  python3 eagle_sheet.py --library design --uncategorized --out /tmp/uncat
  python3 eagle_sheet.py --library design --folder "References/Image Reference" --out /tmp/ref [--per 48] [--vault <볼트>]

출력: {out}-0.png, {out}-1.png … + {out}.json (번호 → id·이름·형식·날짜·볼트 연결 노트).
시트를 보고 번호별 목적 폴더를 정한 뒤, 같은 라이브러리 안이면 v2 item/update(folders)로 옮기고
다른 라이브러리로 보낼 것은 eagle_transfer.py 로 옮긴다. 📝 표시는 볼트 노트에 연결된 항목(이름 변경 금지).
"""
import argparse
import datetime
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from eagle_common import VAULT, folder_paths, items, lib_path, vault_refs  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--library", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--folder")
    g.add_argument("--uncategorized", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--per", type=int, default=48)
    ap.add_argument("--vault", default=VAULT, help="📝 표시용 (없으면 노트 연결 표시를 생략)")
    a = ap.parse_args()

    lib = lib_path(a.library)
    fp = folder_paths(lib)
    fid = None
    if a.folder:
        fid = next((k for k, v in fp.items() if v == a.folder), None)
        if not fid:
            sys.exit(f"✗ 폴더 없음: {a.folder}")
    if a.uncategorized:
        sel = [m for m in items(lib) if not m.get("folders")]
    else:
        sel = [m for m in items(lib) if fid in m.get("folders", [])]
    sel.sort(key=lambda m: m.get("btime", 0))
    refs = vault_refs(a.vault)
    index = []
    for i, m in enumerate(sel):
        index.append(dict(n=i, id=m["id"], name=m["name"], ext=m["ext"], w=m.get("width"), h=m.get("height"),
                          date=datetime.datetime.fromtimestamp(m.get("btime", 0) / 1000).strftime("%Y-%m-%d"),
                          tags=m.get("tags", []), notes=sorted(refs.get(m["id"], []))))
    json.dump(index, open(a.out + ".json", "w"), ensure_ascii=False, indent=1)
    try:
        f = None
        for font in ("/System/Library/Fonts/AppleSDGothicNeo.ttc",               # macOS (한글)
                     "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",    # Linux
                     "C:/Windows/Fonts/malgun.ttf"):                              # Windows
            if os.path.exists(font):
                f = ImageFont.truetype(font, 15)
                break
        f = f or ImageFont.load_default()
    except OSError:
        f = ImageFont.load_default()
    T, cols = 240, 8
    for s in range(0, len(sel), a.per):
        chunk = sel[s:s + a.per]
        rows = (len(chunk) + cols - 1) // cols
        im = Image.new("RGB", (cols * T, rows * (T + 40)), "#EEE")
        d = ImageDraw.Draw(im)
        for k, m in enumerate(chunk):
            i = s + k
            x, y = (k % cols) * T, (k // cols) * (T + 40)
            th = os.path.join(m["_dir"], m["name"] + "_thumbnail.png")
            src = th if os.path.exists(th) else m["_file"]
            try:
                if m["ext"].lower() in ("url", "mp4", "svg", "ai"):
                    raise ValueError
                img = Image.open(src).convert("RGBA")
                bg = Image.new("RGBA", img.size, "#FFFFFF")
                bg.alpha_composite(img)
                img = bg.convert("RGB")
                img.thumbnail((T - 8, T - 8))
                im.paste(img, (x + 4 + (T - 8 - img.width) // 2, y + 4 + (T - 8 - img.height) // 2))
            except Exception:
                d.text((x + 10, y + 100), m["ext"].upper(), fill="#900", font=f)
            e = index[i]
            d.text((x + 4, y + T), f"#{i} {e['date'][2:]} {'📝' if e['notes'] else ''}", fill="#000", font=f)
            d.text((x + 4, y + T + 18), m["name"][:26], fill="#444", font=f)
        im.save(f"{a.out}-{s // a.per}.png")
    print(f"{len(sel)}개 · 시트 {(len(sel) + a.per - 1) // a.per}장 → {a.out}-*.png · 목록 {a.out}.json · 노트 연결 {sum(1 for e in index if e['notes'])}")


if __name__ == "__main__":
    main()
