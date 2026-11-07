#!/usr/bin/env python3
"""
eagle_import.py — manifest 기반으로 이미지를 Eagle 라이브러리에 가져온다.

Eagle 앱이 실행 중이어야 한다 (로컬 API http://localhost:41595). 파일시스템의
metadata.json 을 직접 쓰지 않고 항상 API 를 거친다 (앱이 실행 중일 때 직접 쓰면 덮어써짐).

Manifest (JSON):
{
  "library": "/path/to/Personal.library",                     # 활성 라이브러리 확인용 (다르면 중단)
  "trash": ["EAGLE_ITEM_ID", ...],                              # 선택: 교체 대상 (휴지통 = 복구 가능)
  "items": [
    {"path": "/abs/file.png",
     "folder": "20. Assets/23. Characters/01 Mascot",            # '/' 경로, 없으면 생성
     "name": "mascot-wave",
     "tags": ["character", "mascot"],
     "annotation": "image-gen 2026-01-15 · gen: <model> · prompt: ...",
     "url": "",
     "star": 3,                                                  # 선택 0~5
     "source_id": "OLDID"}                                       # 선택: 다른 라이브러리에서 이전할 때 원본 id
                                                                 #   → --map-out 에 {source_id: new_id} 기록 (노트 링크 갱신용)
  ]
}

Usage:
  python3 eagle_import.py manifest.json [--dry-run] [--allow-duplicate] [--map-out map.json] [--switch]

--switch: manifest 의 library 가 활성 라이브러리가 아니면 잠깐 전환해서 가져오고,
          끝나면 시작할 때 보고 있던 라이브러리로 되돌린다 (특정 라이브러리로 고정 복귀하지 않는다).

중복 방지: 라이브러리 전체 파일의 MD5 와 비교해 같은 파일이 이미 있으면 건너뛴다
(단, 같은 실행에서 trash 로 지정한 항목은 비교 대상에서 제외 → 교체 가능).

⚠ Eagle 자체 중복 병합 (실측): 살아 있는 항목과 같은 파일을 addFromPath 하면
Eagle 은 새 항목을 만들지 않고 기존 항목에 폴더만 추가한 채 success 를 돌려준다.
그래서 교체(trash)는 반드시 추가 *전에* 수행하고(휴지통 항목과는 병합되지 않음),
추가한 모든 항목은 새 id 가 생겼는지 검증한다. 실패 시 교체 원본은 휴지통에서 복구 가능.
"""
import argparse
import glob
import hashlib
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eagle_common import API  # noqa: E402  (설정 파일·EAGLE_API 반영)


def call(method, path, body=None):
    url = f"{API}/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.loads(r.read().decode())
    if res.get("status") != "success":
        raise RuntimeError(f"{path}: {res}")
    return res.get("data")


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def library_hashes(lib, skip_ids):
    out = {}
    for info in glob.glob(os.path.join(lib, "images", "*.info")):
        iid = os.path.basename(info)[:-5]
        if iid in skip_ids:
            continue
        try:
            meta = json.load(open(os.path.join(info, "metadata.json")))
        except Exception:
            continue
        if meta.get("isDeleted"):
            continue
        f = os.path.join(info, f"{meta['name']}.{meta['ext']}")
        if os.path.exists(f):
            out[md5(f)] = (iid, meta["name"])
    return out


def folder_index():
    """'A/B/C' → id, 전체 트리."""
    idx = {}

    def walk(nodes, prefix):
        for n in nodes:
            key = f"{prefix}/{n['name']}" if prefix else n["name"]
            idx[key] = n["id"]
            walk(n.get("children", []), key)
    walk(call("GET", "folder/list"), "")
    return idx


def ensure_folder(path, idx, dry):
    if path in idx:
        return idx[path]
    parts = path.split("/")
    parent = None
    for i in range(1, len(parts) + 1):
        key = "/".join(parts[:i])
        if key in idx:
            parent = idx[key]
            continue
        if dry:
            print(f"  [dry] create folder: {key}")
            idx[key] = f"DRY:{key}"
        else:
            body = {"folderName": parts[i - 1]}
            if parent:
                body["parent"] = parent
            d = call("POST", "folder/create", body)
            idx[key] = d["id"]
            print(f"  + folder: {key} ({d['id']})")
        parent = idx[key]
    return idx[path]


def find_new_item(folder_id, name, before_ids):
    # addFromPath 는 비동기라 목록 반영이 늦다 (실측: 10초 대기로 부족했던 사례) → 최대 30초
    for _ in range(60):
        items = call("GET", f"item/list?folders={folder_id}&limit=500")
        for it in items:
            if it["name"] == name and it["id"] not in before_ids:
                return it["id"]
        time.sleep(0.5)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-duplicate", action="store_true")
    ap.add_argument("--map-out", help="source_id → 새 id 매핑 JSON 저장 경로")
    ap.add_argument("--switch", action="store_true", help="대상 라이브러리로 잠깐 전환 후 원래 보던 라이브러리로 복귀")
    a = ap.parse_args()
    m = json.load(open(a.manifest))
    if a.switch and m.get("library") and not a.dry_run:
        from eagle_common import keep_active, switch
        with keep_active():
            switch(m["library"])
            return run_import(a, m)
    return run_import(a, m)


def run_import(a, m):
    lib = call("GET", "library/info")["library"]["path"]
    want = m.get("library")
    if want and os.path.realpath(want) != os.path.realpath(lib):
        sys.exit(f"✗ 활성 라이브러리가 다름: {lib} (manifest: {want}) — Eagle 에서 라이브러리 전환 후 재실행")
    print(f"library: {lib}")

    trash = m.get("trash", [])
    hashes = {} if a.allow_duplicate else library_hashes(lib, set(trash))
    idx = folder_index()
    added = skipped = failed = 0
    idmap = {}

    if trash:
        if a.dry_run:
            print(f"  [dry] moveToTrash {len(trash)} (추가 전에): {trash}")
        else:
            call("POST", "item/moveToTrash", {"itemIds": trash})
            print(f"🗑 교체 대상 {len(trash)}개 휴지통으로 (추가 전 — Eagle 중복 병합 방지, 복구 가능)")

    for it in m["items"]:
        p = os.path.expanduser(it["path"])
        if not os.path.exists(p):
            print(f"✗ 없음: {p}"); failed += 1; continue
        h = md5(p)
        if h in hashes:
            print(f"= 이미 있음: {it['name']} → {hashes[h][1]} ({hashes[h][0]})"); skipped += 1; continue
        fid = ensure_folder(it["folder"], idx, a.dry_run)
        if a.dry_run:
            print(f"  [dry] add {it['name']} → {it['folder']} tags={it.get('tags', [])}")
            hashes[h] = ("DRY", it["name"]); added += 1; continue
        before = {x["id"] for x in call("GET", f"item/list?folders={fid}&limit=500")}
        call("POST", "item/addFromPath", {
            "path": p, "name": it["name"], "folderId": fid,
            "tags": it.get("tags", []), "annotation": it.get("annotation", ""),
            "website": it.get("url", "")})
        nid = find_new_item(fid, it["name"], before)
        if not nid:
            print(f"✗ 새 항목이 생기지 않음 (Eagle 이 기존 항목에 병합했을 가능성): {it['name']}")
            failed += 1; continue
        if it.get("star"):
            call("POST", "v2/item/update", {"id": nid, "star": it["star"]})  # v1 update 는 일부 필드를 무시함
        hashes[h] = ("new", it["name"])
        if it.get("source_id"):
            idmap[it["source_id"]] = nid
        print(f"✓ {it['name']} → {it['folder']} ({nid})"); added += 1

    if a.map_out and not a.dry_run:
        json.dump(idmap, open(a.map_out, "w"), indent=1)
        print(f"map: {len(idmap)} → {a.map_out}")

    if trash and failed:
        print(f"⚠ 실패 {failed}건 — 교체 원본 {len(trash)}개는 Eagle 휴지통에 있으니 필요하면 복구하세요")

    print(f"done — added {added} · skipped {skipped} · failed {failed}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
