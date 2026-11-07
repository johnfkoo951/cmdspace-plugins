#!/usr/bin/env python3
"""
eagle_export.py — Eagle 폴더(또는 태그)의 원본 파일을 작업 폴더로 복사한다 (사용 시점 스냅샷).

정본은 항상 Eagle 이다. 이 스크립트는 라이브러리를 **읽기만** 하고(metadata.json 파싱),
Eagle 앱·API 를 쓰지 않는다 → 활성 라이브러리가 아니어도 되고 사용자 화면이 바뀌지 않는다.
복사본을 고쳐도 Eagle 에 반영되지 않는다. 정본 수정은 Eagle 에서 하고, 다시 이 스크립트로 가져온다.

Usage:
  python3 eagle_export.py --library design --folder "Characters/Mascot Motion Kit" \
      --dest ~/projects/<video-project>/public/assets/mascot [--recursive] [--flatten]
      [--tag transparent] [--ext png,jpg] [--dry-run]
  python3 eagle_export.py --library design --list "Characters"        # 폴더 트리와 개수만 보기

--library : 설정 파일 libraries 의 별칭 (예: personal, design) | <.library 절대경로>
--recursive : 하위 폴더까지 (기본: 지정 폴더만). 하위 구조는 dest 안에 그대로 유지, --flatten 이면 한 폴더로.
재실행: dest/eagle-export.json 을 읽어 같은 항목은 내용이 바뀐 경우에만 덮어쓴다 (md5 비교).
        Eagle 에서 빠진 항목의 복사본은 지우지 않고 보고만 한다.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eagle_common import LIBS  # noqa: E402  (설정 파일의 라이브러리 별칭)
MANIFEST = "eagle-export.json"


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def slug(name):
    """파일 시스템·웹 번들러 친화적 이름. 한글은 유지, 공백·특수문자는 '-'."""
    s = unicodedata.normalize("NFC", name)
    s = re.sub(r"[\s/\\:*?\"<>|@·]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-.")
    return s[:120] or "untitled"


def load_library(lib):
    meta = json.load(open(os.path.join(lib, "metadata.json")))
    paths = {}   # folder id → 'A/B/C'

    def walk(nodes, prefix):
        for n in nodes:
            key = f"{prefix}/{n['name']}" if prefix else n["name"]
            paths[n["id"]] = key
            walk(n.get("children", []), key)
    walk(meta.get("folders", []), "")
    items = []
    imgdir = os.path.join(lib, "images")
    for d in os.listdir(imgdir):
        if not d.endswith(".info"):
            continue
        try:
            m = json.load(open(os.path.join(imgdir, d, "metadata.json")))
        except Exception:
            continue
        if m.get("isDeleted"):
            continue
        m["_file"] = os.path.join(imgdir, d, f"{m['name']}.{m['ext']}")
        m["_folders"] = [paths.get(f, "?") for f in m.get("folders", [])]
        items.append(m)
    return paths, items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--library", required=True)
    ap.add_argument("--folder")
    ap.add_argument("--list", metavar="PREFIX", nargs="?", const="")
    ap.add_argument("--dest")
    ap.add_argument("--recursive", action="store_true")
    ap.add_argument("--flatten", action="store_true")
    ap.add_argument("--tag", action="append", default=[], help="이 태그가 모두 있는 항목만 (반복 가능)")
    ap.add_argument("--ext", help="예: png,jpg")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    lib = os.path.expanduser(LIBS.get(a.library, a.library))
    if not os.path.exists(os.path.join(lib, "metadata.json")):
        sys.exit(f"✗ 라이브러리를 찾을 수 없음: {lib}")
    paths, items = load_library(lib)

    if a.list is not None:
        counts = {}
        for m in items:
            for f in m["_folders"]:
                counts[f] = counts.get(f, 0) + 1
        for p in sorted(set(paths.values())):
            if p.startswith(a.list):
                print(f"{counts.get(p, 0):5}  {p}")
        return

    if not a.folder or not a.dest:
        sys.exit("✗ --folder 와 --dest 가 필요합니다 (폴더 목록은 --list)")
    if a.folder not in paths.values():
        near = [p for p in paths.values() if a.folder.lower() in p.lower()][:8]
        sys.exit(f"✗ 폴더 없음: {a.folder}\n  비슷한 폴더: {near}")

    exts = set(a.ext.lower().split(",")) if a.ext else None
    sel = []
    for m in items:
        hit = None
        for f in m["_folders"]:
            if f == a.folder or (a.recursive and f.startswith(a.folder + "/")):
                hit = f
                break
        if not hit:
            continue
        if a.tag and not all(t in m.get("tags", []) for t in a.tag):
            continue
        if exts and m["ext"].lower() not in exts:
            continue
        if m["ext"] == "url" or not os.path.exists(m["_file"]):
            print(f"  - 건너뜀 (파일 없음/URL): {m['name']}")
            continue
        rel = "" if a.flatten else "/".join(slug(x) for x in hit[len(a.folder):].strip("/").split("/") if x)
        sel.append((m, rel))

    dest = os.path.abspath(os.path.expanduser(a.dest))
    mpath = os.path.join(dest, MANIFEST)
    old = json.load(open(mpath)) if os.path.exists(mpath) else {"items": {}}
    prev = old.get("items", {})
    used = {v["file"] for v in prev.values()}
    new_items, copied, updated, same = {}, 0, 0, 0

    for m, rel in sorted(sel, key=lambda x: (x[1], x[0]["name"])):
        h = md5(m["_file"])
        if m["id"] in prev:
            relfile = prev[m["id"]]["file"]          # 재실행 시 파일명 고정 (코드가 참조 중일 수 있음)
        else:
            base = os.path.join(rel, slug(m["name"]))
            relfile, k = f"{base}.{m['ext']}", 2
            while relfile in used:
                relfile, k = f"{base}-{k}.{m['ext']}", k + 1
            used.add(relfile)
        out = os.path.join(dest, relfile)
        state = "new"
        if m["id"] in prev and os.path.exists(out):
            state = "same" if prev[m["id"]].get("md5") == h else "changed"
        if not a.dry_run and state != "same":
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copy2(m["_file"], out)
        copied += state == "new"; updated += state == "changed"; same += state == "same"
        if state != "same" or a.dry_run:
            print(f"  {'+' if state == 'new' else ('~' if state == 'changed' else '=')} {relfile}")
        new_items[m["id"]] = {"file": relfile, "name": m["name"], "md5": h, "folder": m["_folders"][0],
                              "tags": m.get("tags", []), "width": m.get("width"), "height": m.get("height")}

    gone = [v["file"] for k, v in prev.items() if k not in new_items]
    if gone:
        print(f"  ⚠ Eagle 폴더에서 빠진 항목 {len(gone)}개 — 복사본은 그대로 둠: {gone[:5]}")
        for k, v in prev.items():
            if k not in new_items:
                new_items[k] = dict(v, removedFromEagle=True)
    if not a.dry_run:
        os.makedirs(dest, exist_ok=True)
        json.dump({"source": {"library": lib, "folder": a.folder, "recursive": a.recursive,
                              "tags": a.tag, "flatten": a.flatten},
                   "exportedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
                   "note": "정본은 Eagle. 이 폴더는 사용 시점 복사본 — 수정은 Eagle 에서 하고 eagle_export.py 로 다시 가져온다.",
                   "items": new_items}, open(mpath, "w"), ensure_ascii=False, indent=1)
    print(f"{'[dry] ' if a.dry_run else ''}done — new {copied} · changed {updated} · unchanged {same} → {dest}")


if __name__ == "__main__":
    main()
