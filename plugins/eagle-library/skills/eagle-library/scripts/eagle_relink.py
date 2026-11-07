#!/usr/bin/env python3
"""
eagle_relink.py — 라이브러리 이전 후 볼트 노트의 Eagle 링크를 새 ID·새 경로로 바꾼다.

  python3 eagle_relink.py --map idmap.json --to <라이브러리> [--vault <볼트>] [--apply] [--backup-dir DIR]

- idmap.json: {원본 ID: 새 ID} (eagle_import.py --map-out 결과)
- `file:///…/{아무 라이브러리}.library/images/{OLD}.info/{파일}` → `file:///{--to}/images/{NEW}.info/{파일}`
  파일이 새 위치에 없으면(주로 `_thumbnail.png`) 새 항목의 원본 파일로 연결한다.
- `eagle://item/{OLD}`, `41595/item?id={OLD}` → 새 ID
- --apply 없이 돌리면 바뀔 곳만 센다. --apply 는 수정 전 노트를 --backup-dir 에 복사한다.
노트 본문·프론트매터는 링크 외에 건드리지 않는다.
"""
import argparse
import json
import os
import re
import shutil
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from eagle_common import VAULT, find_notes, lib_path, require_vault  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--to", required=True, help="새 항목이 있는 라이브러리 (personal|design|… 또는 경로)")
    ap.add_argument("--vault", default=VAULT)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backup-dir")
    a = ap.parse_args()

    require_vault(a.vault)
    idmap = json.load(open(a.map))
    dst = lib_path(a.to)
    img = os.path.join(dst, "images")
    prefix = "file://" + urllib.parse.quote(img) + "/"
    backup = a.backup_dir or os.path.join(os.path.dirname(os.path.abspath(a.map)),
                                          "note-backup-" + time.strftime("%Y%m%d-%H%M%S"))
    files = set(find_notes(a.vault, fixed=list(idmap))) if idmap else set()
    rx = re.compile(r"file:///[^\n]+?\.library/images/([A-Z0-9]{13})\.info/"
                    r"([^\n]+?\.(?:png|jpe?g|webp|gif|svg|mp4))(?=[)>\s]|$)", re.IGNORECASE)
    total = 0
    for f in sorted(files):
        text = open(f, encoding="utf-8").read()
        new_text, cnt = text, [0]

        def sub(m):
            old, fn = m.group(1), m.group(2)
            if old not in idmap:
                return m.group(0)
            new = idmap[old]
            if not os.path.exists(os.path.join(img, f"{new}.info", urllib.parse.unquote(fn))):
                main_file = [x for x in os.listdir(os.path.join(img, f"{new}.info"))
                             if x != "metadata.json" and not x.endswith("_thumbnail.png")][0]
                fn = urllib.parse.quote(main_file)
            cnt[0] += 1
            return prefix + f"{new}.info/{fn}"
        new_text = rx.sub(sub, new_text)
        for old, new in idmap.items():
            cnt[0] += new_text.count(f"eagle://item/{old}") + new_text.count(f"41595/item?id={old}")
            new_text = new_text.replace(f"eagle://item/{old}", f"eagle://item/{new}")
            new_text = new_text.replace(f"41595/item?id={old}", f"41595/item?id={new}")
        left = [o for o in idmap if o in new_text]
        rel = os.path.relpath(f, a.vault)
        print(f"{cnt[0]:4}  {rel}" + (f"   ⚠ 남은 옛 ID {left}" if left else ""))
        total += cnt[0]
        if a.apply and new_text != text:
            b = os.path.join(backup, rel)
            os.makedirs(os.path.dirname(b), exist_ok=True)
            shutil.copy2(f, b)
            open(f, "w", encoding="utf-8").write(new_text)
    print(f"{'적용' if a.apply else '[dry] 바뀔 곳'} {total} · 노트 {len(files)}" + (f" · 백업 {backup}" if a.apply and files else ""))


if __name__ == "__main__":
    main()
