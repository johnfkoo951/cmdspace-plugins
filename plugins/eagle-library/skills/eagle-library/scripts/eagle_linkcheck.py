#!/usr/bin/env python3
"""
eagle_linkcheck.py — 볼트 노트의 Eagle 링크가 실제 파일을 가리키는지 검사 (읽기 전용).

  python3 eagle_linkcheck.py [--vault <볼트>] [--ids ID ...] [--json out.json] [--fix-moved [--apply]]

- `file:///…/*.library/images/{ID}.info/{파일}` 링크: 파일 존재 여부
- `eagle://item/{ID}`, `41595/item?id={ID}`: 알려진 라이브러리 중 어디에도 살아 있는 항목이 없으면 깨짐
- --ids 를 주면 그 ID 가 볼트에 남아 있는지(이전 후 옛 ID 잔존 검사)만 본다
라이브러리 이전·이름 변경 뒤에 반드시 돌린다.
--fix-moved: 라이브러리 폴더가 옮겨져 깨진 링크를, 같은 라이브러리 이름의 현재 위치에 같은 파일이 있을 때만
             새 경로로 바꾼다 (파일명이 다르면 _thumbnail 이면 원본 파일로). 기본은 미리보기, --apply 로 적용(노트 백업).
"""
import argparse
import collections
import json
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from eagle_common import EAGLE_REF, FILE_LINK, LIB_BY_NAME, LIBS, VAULT, find_notes, items, require_vault, unquote  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=VAULT)
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--json")
    ap.add_argument("--fix-moved", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    require_vault(a.vault)
    if a.ids:
        left = find_notes(a.vault, fixed=a.ids)
        print(f"옛 ID 남은 노트: {len(left)}")
        for f in left:
            print("  ", os.path.relpath(f, a.vault))
        sys.exit(1 if left else 0)

    live = {}
    for name, lib in LIBS.items():
        if os.path.exists(os.path.join(lib, "metadata.json")):
            for m in items(lib):
                live[m["id"]] = name
    files = find_notes(a.vault, pattern=EAGLE_REF)
    total, broken = collections.Counter(), []
    rx_id = re.compile(r"(?:eagle://item/|41595/item\?id=)([A-Z0-9]{13})")
    fixed, backup = 0, os.path.join(tempfile.gettempdir(), "eagle-linkfix-" + time.strftime("%Y%m%d-%H%M%S"))
    for f in files:
        text = open(f, encoding="utf-8").read()
        rel = os.path.relpath(f, a.vault)
        new_text = text
        for libpath, iid, fn in FILE_LINK.findall(text):
            p = unquote(f"{libpath}/images/{iid}.info/{fn}")
            lib = os.path.basename(unquote(libpath))
            total[lib] += 1
            if os.path.exists(p):
                continue
            cur = LIB_BY_NAME.get(lib)
            fix = None
            if a.fix_moved and cur:
                d = os.path.join(cur, "images", f"{iid}.info")
                cand = os.path.join(d, unquote(fn))
                if os.path.exists(cand):
                    fix = fn
                elif os.path.isdir(d) and unquote(fn).endswith("_thumbnail.png"):
                    mains = [x for x in os.listdir(d) if x != "metadata.json" and not x.endswith("_thumbnail.png")]
                    fix = urllib.parse.quote(mains[0]) if mains else None
                if fix:
                    new_prefix = "file://" + urllib.parse.quote(cur)
                    new_text = new_text.replace(f"file://{libpath}/images/{iid}.info/{fn}",
                                                f"{new_prefix}/images/{iid}.info/{fix}")
                    fixed += 1
                    continue
            broken.append(dict(note=rel, kind="file", target=p))
        for iid in rx_id.findall(text):
            total["eagle://"] += 1
            if iid not in live:
                broken.append(dict(note=rel, kind="eagle-id", target=iid))
        if a.fix_moved and a.apply and new_text != text:
            b = os.path.join(backup, rel)
            os.makedirs(os.path.dirname(b), exist_ok=True)
            shutil.copy2(f, b)
            open(f, "w", encoding="utf-8").write(new_text)
    if a.fix_moved:
        print(f"{'적용' if a.apply else '[dry] 복구 가능'}: 옛 라이브러리 경로 링크 {fixed}개"
              + (f" (노트 백업 {backup})" if a.apply and fixed else ""))
    print("링크 수:", dict(total))
    print(f"깨짐: {len(broken)}")
    for b in broken:
        print(f"  [{b['kind']}] {b['note']}  →  {os.path.basename(b['target'])[:70]}")
    if a.json:
        json.dump(dict(total=total, broken=broken), open(a.json, "w"), ensure_ascii=False, indent=1)
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
