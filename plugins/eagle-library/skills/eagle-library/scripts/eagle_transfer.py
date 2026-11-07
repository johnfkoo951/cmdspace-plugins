#!/usr/bin/env python3
"""
eagle_transfer.py — Eagle 항목을 다른 라이브러리로 이전하면서 볼트 노트 링크를 유지한다.

  python3 eagle_transfer.py --from design --to personal --ids ID [ID ...] --folder "10. Obsidian/13. Daily"
                            [--ids-file ids.txt] [--add-tags daily obsidian-linked] [--vault <볼트>] [--dry-run]

순서 (손으로 여러 번 반복하던 절차를 묶은 것):
 1. 원본 파일을 스테이징 폴더에 복사, 메타데이터(이름·태그·주석·url·별점) 보존 + 주석에 `이전: A → B (날짜, 원본 ID)`
    노트에 연결된 항목은 url 이 비어 있으면 obsidian:// 링크를 채운다.
 2. 대상 라이브러리로 전환 → eagle_import.py --map-out (중복 건너뜀·새 ID 검증)
 3. eagle_relink.py --apply 로 노트 링크를 새 ID·경로로 (수정 전 노트 백업)
 4. eagle_linkcheck.py --ids 로 옛 ID 잔존 검사
 5. 원래 라이브러리로 전환 → 이전된 원본만 휴지통 (대상에 이미 같은 파일이 있어 건너뛴 항목도 휴지통 — 중복 정리)
 6. 처음에 열려 있던 라이브러리로 복귀
실패하면 원본을 휴지통으로 보내지 않는다. 이름은 바꾸지 않는다 (노트 링크 파일명 보존).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eagle_common import VAULT, VAULT_NAME, active, call, folder_paths, lib_path, require_vault, switch, vault_refs  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", required=True)
    ap.add_argument("--to", dest="dst", required=True)
    ap.add_argument("--ids", nargs="*", default=[])
    ap.add_argument("--ids-file")
    ap.add_argument("--folder", required=True, help="대상 라이브러리 안의 폴더 경로 ('/' 구분, 없으면 생성)")
    ap.add_argument("--add-tags", nargs="*", default=[])
    ap.add_argument("--vault", default=VAULT)
    ap.add_argument("--work", help="스테이징·manifest·백업 폴더 (기본: 임시 폴더/eagle-transfer-<시각>)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    ids = list(a.ids) + ([l.strip() for l in open(a.ids_file) if l.strip()] if a.ids_file else [])
    if not ids:
        sys.exit("✗ --ids 또는 --ids-file")
    src, dst = lib_path(a.src), lib_path(a.dst)
    require_vault(a.vault)
    vault_name = VAULT_NAME if os.path.realpath(a.vault) == os.path.realpath(VAULT or a.vault) else os.path.basename(a.vault.rstrip("/"))
    work = a.work or os.path.join(tempfile.gettempdir(), f"eagle-transfer-{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(os.path.join(work, "stage"), exist_ok=True)
    refs = vault_refs(a.vault)
    fpaths = folder_paths(src)
    today = time.strftime("%Y-%m-%d")
    lname = lambda p: os.path.basename(p).replace(".library", "")

    items = []
    for iid in ids:
        d = os.path.join(src, "images", f"{iid}.info")
        m = json.load(open(os.path.join(d, "metadata.json")))
        if m.get("isDeleted"):
            print(f"  - 휴지통 항목 건너뜀: {iid}")
            continue
        stage = os.path.join(work, "stage", f"{iid}.{m['ext']}")
        shutil.copy2(os.path.join(d, f"{m['name']}.{m['ext']}"), stage)
        notes = sorted(refs.get(iid, []))
        ann = (m.get("annotation") or "")
        if notes and "연결 노트" not in ann:
            ann += "\n연결 노트: " + " / ".join(os.path.basename(n)[:-3] for n in notes)
        ann = (ann + f"\n이전: {lname(src)} → {lname(dst)} ({today}, 원본 ID {iid})").strip()
        url = m.get("url") or ("obsidian://open?vault=" + urllib.parse.quote(vault_name) + "&file="
                               + urllib.parse.quote(notes[0][:-3]) if notes else "")
        tags = list(dict.fromkeys(m.get("tags", []) + a.add_tags))
        it = dict(path=stage, folder=a.folder, name=m["name"], tags=tags, annotation=ann, url=url, source_id=iid)
        if m.get("star"):
            it["star"] = m["star"]
        items.append(it)
        print(f"  · {m['name'][:50]}  [{', '.join(fpaths.get(f, '?') for f in m.get('folders', [])) or '미분류'}]"
              f"  노트 {len(notes)}")
    manifest = os.path.join(work, "manifest.json")
    json.dump(dict(library=dst, items=items), open(manifest, "w"), ensure_ascii=False, indent=1)
    print(f"대상 {len(items)}개 → {lname(dst)} / {a.folder}   (작업 폴더 {work})")
    if a.dry_run:
        return

    start = active()
    idmap_path = os.path.join(work, "idmap.json")
    try:
        switch(dst)
        r = subprocess.run([sys.executable, os.path.join(HERE, "eagle_import.py"), manifest, "--map-out", idmap_path],
                           capture_output=True, text=True)
        print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-500:])
        if r.returncode != 0:
            raise SystemExit("✗ 가져오기 실패 — 원본은 그대로 둠\n" + r.stdout[-1500:])
        idmap = json.load(open(idmap_path))
        subprocess.run([sys.executable, os.path.join(HERE, "eagle_relink.py"), "--map", idmap_path, "--to", dst,
                        "--vault", a.vault, "--apply", "--backup-dir", os.path.join(work, "note-backup")])
        chk = subprocess.run([sys.executable, os.path.join(HERE, "eagle_linkcheck.py"), "--vault", a.vault,
                              "--ids", *idmap.keys()], capture_output=True, text=True)
        print(chk.stdout.strip())
        if chk.returncode != 0:
            raise SystemExit("✗ 옛 ID 가 볼트에 남음 — 원본은 휴지통으로 보내지 않음")
        skipped = [i["source_id"] for i in items if i["source_id"] not in idmap]
        switch(src)
        trash = list(idmap) + skipped
        call("item/moveToTrash", {"itemIds": trash})
        print(f"🗑 원본 {len(trash)}개 휴지통 ({lname(src)})" + (f" — 이 중 {len(skipped)}개는 대상에 같은 파일이 이미 있어 중복 정리" if skipped else ""))
    finally:
        try:
            switch(start)
            print(f"활성 라이브러리 복귀: {lname(start)}")
        except SystemExit as e:
            print(e)


if __name__ == "__main__":
    main()
