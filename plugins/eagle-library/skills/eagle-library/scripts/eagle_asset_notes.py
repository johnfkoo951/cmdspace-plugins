#!/usr/bin/env python3
"""
eagle_asset_notes.py — Eagle 에셋마다 볼트 에셋 노트(type: visual-asset)가 있는지 점검하고 없으면 만든다.

규칙 파일: --rules, 없으면 설정 파일의 "assetNotesRules", 그것도 없으면 ~/.config/eagle-library/asset-notes-rules.json
           (예시: references/asset-notes-rules.example.json — 복사해서 자기 폴더에 맞게 고친다)
노트 위치: 볼트 `{noteRoot}/{group}/{Eagle 이름}.md`
모든 노트는 type: visual-asset 이라 Bases 하나(예시: assets/Visual Assets.base)에 이미지 카드로 모인다.

  python3 eagle_asset_notes.py --check            # 노트 없는 에셋, 원본이 사라진 노트 보고 (읽기 전용, 앱 불필요)
  python3 eagle_asset_notes.py --apply            # 없는 노트 생성 + Eagle url 이 빈 항목에 노트 링크 기록
  python3 eagle_asset_notes.py --apply --no-url   # 노트만 만들고 Eagle 은 건드리지 않음

- 이미 있는 노트(eagleId 로 찾음)는 덮어쓰지 않는다. 사람이 고친 사용처·장면을 보존한다.
- `image` 는 URL 인코딩한 file:/// 원본 경로. 인코딩해야 Bases 카드에 보인다.
- Eagle url 이 이미 다른 노트를 가리키면 바꾸지 않고, 그 노트를 `relatedNote` 로 적는다.
- url 기록은 활성 라이브러리에만 쓸 수 있어 잠깐 전환하고, 끝나면 시작할 때 보던 라이브러리로 돌아간다.
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eagle_common import (CONFIG, VAULT, VAULT_NAME, call, folder_paths, items, keep_active,  # noqa: E402
                          lib_path, require_vault, switch)

DEFAULT_RULES = os.path.expanduser(CONFIG.get("assetNotesRules") or "~/.config/eagle-library/asset-notes-rules.json")


def load_rules(path):
    if not os.path.exists(path):
        example = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references",
                               "asset-notes-rules.example.json")
        raise SystemExit(f"✗ 규칙 파일이 없음: {path}\n  예시를 복사해서 고치세요: cp \"{os.path.normpath(example)}\" \"{path}\"")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def rule_for(paths, rules):
    for r in rules["folders"]:
        for p in paths:
            if p == r["prefix"] or p.startswith(r["prefix"].rstrip("/") + "/"):
                return r, p
    return None, None


def system_tags(rules):
    return set(rules.get("systemTags", []))


def is_gen_tag(t, rules):
    return t.startswith(tuple(rules.get("genTagPrefixes", [])))


def title_of(it, rules):
    """사람이 읽는 제목: 주석의 '장면:' 같은 머리말 뒤 문장 → 없으면 고유 태그 → 없으면 Eagle 이름."""
    ann = it.get("annotation") or ""
    for k in rules.get("titleKeys", []):
        if k in ann:
            t = re.split(r" · | — |\n", ann.split(k, 1)[1])[0].strip()
            if t:
                return t[:60]
    own = [t for t in it.get("tags", []) if t not in system_tags(rules) and not is_gen_tag(t, rules)]
    return " ".join(own[:3]) if own else it["name"]


def haystack(it, rules):
    # 주석 전체는 쓰지 않는다: '사용처: 강의 덱' 같은 머리말이 오분류를 만든다 (실측)
    tags = " ".join(x for x in it.get("tags", []) if x not in system_tags(rules))
    return " ".join([it["name"].replace("-", " "), tags, title_of(it, rules)]).lower()


def scene_of(it, rule, rules):
    """판정 순서: overrides → 종류 고정값(kindScene) → 이름·태그·제목 키워드(sceneKeywords) → 폴더 기본값 → 전체 기본값."""
    ov = rules.get("overrides", {}).get(it["name"], {})
    if ov.get("scene"):
        return ov["scene"]
    if rule["assetKind"] in rules.get("kindScene", {}):
        return rules["kindScene"][rule["assetKind"]]
    hay = haystack(it, rules)
    for scene, words in rules.get("sceneKeywords", []):
        if any(w.lower().replace("-", " ") in hay for w in words):
            return scene
    return rule.get("defaultScene") or rules.get("defaultScene", "Other")


def existing_notes(root):
    found = {}
    if not os.path.isdir(root):
        return found
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".md"):
                p = os.path.join(dp, f)
                with open(p, encoding="utf-8") as fh:
                    m = re.search(r"^eagleId: \"?(\w+)\"?$", fh.read(), re.M)
                if m:
                    found[m.group(1)] = p
    return found


def vault_basenames(vault):
    names = set()
    for dp, dns, fs in os.walk(vault):
        dns[:] = [d for d in dns if not d.startswith(".")]
        names.update(f[:-3] for f in fs if f.endswith(".md"))
    return names


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def note_text(it, rule, rules, folder, title, related, libname):
    scene = scene_of(it, rule, rules)
    usage = rules.get("overrides", {}).get(it["name"], {}).get("usage") or rule.get("usage", [])
    url = "file://" + urllib.parse.quote(it["_file"])
    sys_tags = system_tags(rules)
    chars = [c for c in rules.get("characters", []) if c in it.get("tags", [])]
    tags = ["visual-asset"] + [t for t in it.get("tags", []) if t not in sys_tags and not is_gen_tag(t, rules)
                               and not re.fullmatch(r"[\d:.]+", t)][:6]
    gen = next((t for t in it.get("tags", []) if is_gen_tag(t, rules)), "")
    if not gen:
        m = re.search(r"gen: (\S+)", it.get("annotation") or "")
        gen = m.group(1) if m else ""
    created = re.search(r"\d{4}-\d{2}-\d{2}", it.get("annotation") or "")
    today = date.today().isoformat()
    desc = (f"{rule['assetKind']} image '{it['name']}' whose original lives in the Eagle library '{libname}'."
            + (f" Reference when picking an image for {', '.join(usage)}." if usage else ""))
    author = rules.get("author")
    fm = ["---", "type: visual-asset", "aliases:", f"  - {q(it['name'])}"] + (
        [f"  - {q(title)}"] if title != it["name"] else []) + [f"description: {q(desc)}"] + (
        ["author:", f"  - {q(author)}"] if author else []) + [
        f"date created: {created.group(0) if created else today}", f"date modified: {today}",
        "tags:"] + [f"  - {q(t)}" for t in tags] + [
        f"assetKind: {q(rule['assetKind'])}", f"scene: {q(scene)}", "usage:"] + [f"  - {q(u)}" for u in usage] + (
        ["characters:"] + [f"  - {q(c)}" for c in chars] if chars else []) + [
        f"image: {q(url)}", f"eagleId: {it['id']}", f'eagleUrl: "eagle://item/{it["id"]}"', f"eagleFolder: {q(folder)}"] + (
        [f"genModel: {q(gen)}"] if gen else []) + (
        [f'relatedNote: "[[{related}]]"'] if related else []) + [
        f"{k}: {q(v)}" for k, v in rules.get("extraFrontmatter", {}).items()] + ["---"]
    base_file = rules.get("baseFile")
    body = [f"![{title}]({url})", "## Scene", (it.get("annotation") or "(no annotation)").replace("\n", " "),
            "## Usage"] + ([f"- {u}" for u in usage] or ["-"]) + (
        ["## Related note", f"- [[{related}]]"] if related else []) + [
        "## Source", f"- Eagle: [Open in Eagle](eagle://item/{it['id']}) · folder `{folder}`", f"- File: `{it['_file']}`"] + (
        [f"- Collection view: [[{os.path.basename(base_file)}]]"] if base_file else []) + [
        "- Created by `eagle-library/scripts/eagle_asset_notes.py` (edits to usage and scene are never overwritten)"]
    return "\n".join(fm + body) + "\n"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    ap.add_argument("--rules", default=DEFAULT_RULES)
    ap.add_argument("--vault", default=VAULT)
    ap.add_argument("--no-url", action="store_true", help="Eagle url 을 기록하지 않음")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    rules = load_rules(a.rules)
    vault = require_vault(a.vault)
    vault_name = VAULT_NAME if os.path.realpath(vault) == os.path.realpath(VAULT or vault) else os.path.basename(vault.rstrip("/"))
    lib = lib_path(rules["library"])
    libname = os.path.basename(lib.rstrip("/")).replace(".library", "")
    root = os.path.join(vault, rules["noteRoot"])
    fp = folder_paths(lib)
    have = existing_notes(root)
    targets = []
    variants = tuple(rules.get("variantSuffixes", []))
    for it in items(lib):
        if variants and it["name"].endswith(variants):
            continue  # 같은 그림의 큰 판 등 — 원본 에셋 노트를 함께 쓴다
        paths = [fp.get(f, "") for f in it.get("folders", [])]
        rule, folder = rule_for(paths, rules)
        if rule:
            targets.append((it, rule, folder))
    ids = {it["id"] for it, _, _ in targets}
    missing = [t for t in targets if t[0]["id"] not in have]
    orphans = [p for i, p in have.items() if i not in ids]
    print(f"대상 에셋 {len(targets)} · 노트 있음 {len(targets) - len(missing)} · 노트 없음 {len(missing)} · 원본 없는 노트 {len(orphans)}")
    for p in orphans:
        print("  원본 없음:", os.path.relpath(p, vault))
    if a.check:
        for it, rule, _ in missing[:40]:
            print(f"  노트 없음: {rule['group']} / {it['name']}")
        sys.exit(1 if missing else 0)

    if a.limit:
        missing = missing[:a.limit]
    names = vault_basenames(vault)
    made, url_jobs = [], []
    for it, rule, folder in missing:
        related = ""
        u = it.get("url") or ""
        if u.startswith("obsidian://open") and "file=" in u:
            related = urllib.parse.unquote(u.split("file=", 1)[1].split("&")[0])
            if related.startswith(rules["noteRoot"]):
                related, u = "", ""      # 예전 에셋 노트 링크 → 새 노트로 다시 쓴다
        base = it["name"] if it["name"] not in names else f"{it['name']} (asset)"
        d = os.path.join(root, rule["group"])
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, base + ".md")
        if os.path.exists(path):
            print("  건너뜀(같은 파일명 있음):", os.path.relpath(path, vault))
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(note_text(it, rule, rules, folder, title_of(it, rules), related, libname))
        names.add(base)
        made.append(path)
        if not u:
            rel = os.path.relpath(path, vault)[:-3]
            url_jobs.append((it["id"], "obsidian://open?vault=" + urllib.parse.quote(vault_name, safe="")
                             + "&file=" + urllib.parse.quote(rel, safe="")))
    print(f"노트 생성 {len(made)}")
    if url_jobs and not a.no_url:
        with keep_active():
            switch(lib)
            for iid, u in url_jobs:
                call("item/update", {"id": iid, "url": u}, v2=True)
        print(f"Eagle url 기록 {len(url_jobs)}")


if __name__ == "__main__":
    main()
