#!/usr/bin/env python3
"""
eagle_asset_notes.py — Eagle 에셋마다 볼트 에셋 노트(type: visual-asset)가 있는지 점검하고 없으면 만든다.

규칙 파일: --rules, 없으면 설정 파일의 "assetNotesRules", 그것도 없으면 ~/.config/eagle-library/asset-notes-rules.json
           (예시: references/asset-notes-rules.example.json — 키 설명은 그 파일의 _doc)
노트 위치: 볼트 `{noteRoot}/{group}/{Eagle 이름}.md`
모든 노트는 type: visual-asset 이라 Bases 하나(예시: assets/Visual Assets.base)에 이미지 카드로 모인다.

  python3 eagle_asset_notes.py --check            # 노트 없는 에셋, 원본이 사라진 노트 보고 (읽기 전용, 앱 불필요)
  python3 eagle_asset_notes.py --apply            # 없는 노트 생성 + Eagle url 이 빈 항목에 노트 링크 기록
  python3 eagle_asset_notes.py --apply --no-url   # 노트만 만들고 Eagle 은 건드리지 않음
  python3 eagle_asset_notes.py --preview NAME     # 그 에셋의 노트를 만들지 않고 화면에만 출력

- 이미 있는 노트(eagleId 로 찾음)는 덮어쓰지 않는다. 사람이 고친 사용처·장면을 보존한다.
- `image` 는 URL 인코딩한 file:/// 원본 경로. 인코딩해야 Bases 카드에 보인다.
- Eagle url 이 이미 다른 노트를 가리키면 바꾸지 않고, 그 노트를 `relatedNote` 로 적는다.
- url 기록은 활성 라이브러리에만 쓸 수 있어 잠깐 전환하고, 끝나면 시작할 때 보던 라이브러리로 돌아간다.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eagle_common import (ASSET_NOTES_RULES, VAULT, VAULT_NAME, call, folder_paths, items,  # noqa: E402
                          keep_active, lib_path, require_vault, switch)

DEFAULT_RULES = ASSET_NOTES_RULES or os.path.expanduser("~/.config/eagle-library/asset-notes-rules.json")

TEXT = {
    "en": dict(scene="Scene", noAnn="(no annotation)", usage="Usage", related="Related note", source="Source",
               eagle="- Eagle: [Open in Eagle](eagle://item/{id}) · folder `{folder}`", file="- File: `{file}`",
               base="- Collection view: [[{base}]]",
               made="- Created by `eagle-library/scripts/eagle_asset_notes.py` (edits to usage and scene are never overwritten)"),
    "ko": dict(scene="장면", noAnn="(주석 없음)", usage="사용처", related="연결 노트", source="원본",
               eagle="- Eagle: [Eagle에서 열기](eagle://item/{id}) · 폴더 `{folder}`", file="- 파일: `{file}`",
               base="- 묶음 보기: [[{base}]]",
               made="- 자동 생성: `eagle-library/scripts/eagle_asset_notes.py` (사용처·담당은 직접 고쳐도 다시 덮어쓰지 않음)"),
}


def load_rules(path):
    if not os.path.exists(path):
        example = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references",
                               "asset-notes-rules.example.json")
        raise SystemExit(f"✗ 규칙 파일이 없음: {path}\n  예시를 복사해서 고치세요: cp \"{os.path.normpath(example)}\" \"{path}\"")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def rule_for(paths, rules):
    """prefix 는 문자열 앞부분 일치다. 'A/01 Characters' 규칙은 'A/01 Characters · 마스코트' 폴더에도 맞는다."""
    for r in rules["folders"]:
        for p in paths:
            if p == r["prefix"] or p.startswith(r["prefix"]):
                return r, p
    return None, None


def system_tags(rules):
    return set(rules.get("systemTags", []))


def is_gen_tag(t, rules):
    return t.startswith(tuple(rules.get("genTagPrefixes", [])))


def title_of(it, rules):
    """사람이 읽는 제목: 주석의 '장면:' 같은 머리말 뒤 문장 → titlePatterns → 고유 태그 → Eagle 이름."""
    ann = it.get("annotation") or ""
    for k in rules.get("titleKeys", []):
        if k in ann:
            t = re.split(r" · | 이전: | — |\n", ann.split(k, 1)[1])[0].strip()   # '이전:' = eagle_transfer.py 가 남기는 표식
            if " / " in t:
                t = t.split(" / ", 1)[1]                                       # '분류 / 제목' 형식이면 제목만
            if t:
                return t[:60]
    for tp in rules.get("titlePatterns", []):
        m = re.search(tp["pattern"], ann)
        if m:
            return tp.get("format", "{0}").format(m.group(0), *m.groups())
    own = [t for t in it.get("tags", []) if t not in system_tags(rules) and not is_gen_tag(t, rules)]
    if rules.get("titleTagPattern"):
        own = [t for t in own if re.search(rules["titleTagPattern"], t)]
    return " ".join(own[:3]) if own else it["name"]


def haystack(it, rules):
    # 주석 전체는 쓰지 않는다: '사용처: 강의 덱' 같은 머리말이 오분류를 만든다 (실측)
    tags = " ".join(x for x in it.get("tags", []) if x not in system_tags(rules))
    return " ".join([it["name"].replace("-", " "), tags, title_of(it, rules)]).lower()


def keyword_hit(words, hay):
    return any(w.lower().replace("-", " ") in hay for w in words)


def category_of(it, rule, rules):
    """선택 기능. 판정 순서: overrides → 폴더 categoryFromTags(태그 → 값) → 폴더 category 고정 → 키워드 → 폴더/전체 기본값."""
    cat = rules.get("category")
    if not cat:
        return None
    ov = rules.get("overrides", {}).get(it["name"], {})
    if ov.get("category") is not None:
        return str(ov["category"])
    if rule.get("categoryFromTags"):
        for tag, value in cat.get("fromTags", {}).items():
            if tag in it.get("tags", []):
                return str(value)
    if rule.get("category") is not None:
        return str(rule["category"])
    hay = haystack(it, rules)
    for value, words in cat.get("keywords", []):
        if keyword_hit(words, hay):
            return str(value)
    d = rule.get("defaultCategory", cat.get("default"))
    return None if d is None else str(d)


def scene_of(it, rule, rules, cat_value):
    """판정 순서: overrides → kindScene → sceneKeywords → 카테고리 값의 scene → 폴더 defaultScene → 전체 defaultScene."""
    ov = rules.get("overrides", {}).get(it["name"], {})
    if ov.get("scene"):
        return ov["scene"]
    if rule["assetKind"] in rules.get("kindScene", {}):
        return rules["kindScene"][rule["assetKind"]]
    hay = haystack(it, rules)
    for scene, words in rules.get("sceneKeywords", []):
        if keyword_hit(words, hay):
            return scene
    if cat_value and cat_value.get("scene"):
        return cat_value["scene"]
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


def yaml_lines(key, value):
    if isinstance(value, list):
        return [f"{key}:"] + [f"  - {q(v)}" for v in value]
    return [f"{key}: {q(value)}"]


def command_fields(rules, vault):
    """commandFields: {필드: [명령, 인자…]} — 명령의 표준출력을 값으로 쓴다 (실패하거나 비면 필드를 생략)."""
    out = {}
    for key, cmd in rules.get("commandFields", {}).items():
        try:
            v = subprocess.run(cmd, capture_output=True, text=True, cwd=vault, timeout=10).stdout.strip()
        except Exception:
            v = ""
        if v:
            out[key] = v
    return out


def note_text(it, rule, rules, folder, related, libname, extra_fields=None):
    title = title_of(it, rules)
    cat_key = category_of(it, rule, rules)
    cat_value = (rules.get("category", {}).get("values", {}).get(cat_key) or {}) if cat_key else {}
    scene = scene_of(it, rule, rules, cat_value)
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
    kind = rule["assetKind"]
    fill = dict(kind=kind, kindLabel=rules.get("kindLabels", {}).get(kind, rules.get("kindLabelDefault", kind)),
                name=it["name"], title=title, library=libname, usage=", ".join(usage), scene=scene)
    if rules.get("descriptionTemplate"):
        desc = rules["descriptionTemplate"].format(**fill)
    else:
        desc = (f"{kind} image '{it['name']}' whose original lives in the Eagle library '{libname}'."
                + (f" Reference when picking an image for {fill['usage']}." if usage else ""))

    fields = [("type", "visual-asset"), ("aliases", [it["name"]] + ([title] if title != it["name"] else [])),
              ("description", desc)]
    if rules.get("author"):
        fields.append(("author", [rules["author"]]))
    fields += [("date created", created.group(0) if created else today), ("date modified", today), ("tags", tags),
               ("assetKind", kind), ("scene", scene), ("usage", usage)]
    if chars:
        fields.append(("characters", chars))
    fields += [("image", url), ("eagleId", it["id"]), ("eagleUrl", f"eagle://item/{it['id']}"), ("eagleFolder", folder)]
    if gen:
        fields.append(("genModel", gen))
    if related:
        fields.append(("relatedNote", f"[[{related}]]"))
    fields += list(cat_value.get("frontmatter", {}).items())
    fields += list(rules.get("extraFrontmatter", {}).items())
    fields += list((extra_fields or {}).items())
    order = rules.get("fieldOrder", [])
    if order:
        fields.sort(key=lambda kv: order.index(kv[0]) if kv[0] in order else len(order))   # 안정 정렬: 목록 밖은 기본 순서

    fm = ["---"]
    for k, v in fields:
        if k in ("type", "date created", "date modified", "eagleId"):
            fm.append(f"{k}: {v}")                    # 날짜는 따옴표 없이 (Obsidian 날짜 속성), type 은 볼트 관례대로
        else:
            fm += yaml_lines(k, v)
    fm.append("---")

    T = TEXT.get(rules.get("lang", "en"), TEXT["en"])
    sub = lambda line: line.replace("{scene}", scene).replace("{name}", it["name"]).replace("{title}", title)
    body = [f"![{title}]({url})", f"## {T['scene']}", (it.get("annotation") or T["noAnn"]).replace("\n", " "),
            f"## {T['usage']}"] + [f"- {u}" for u in usage] + [sub(x) for x in cat_value.get("body", [])]
    if related:
        body += [f"## {T['related']}", f"- [[{related}]]"]
    body += [f"## {T['source']}", T["eagle"].format(id=it["id"], folder=folder), T["file"].format(file=it["_file"])]
    if rules.get("baseFile"):
        body.append(T["base"].format(base=os.path.basename(rules["baseFile"])))
    body.append(T["made"])
    return "\n".join(fm + body) + "\n"


def targets_of(lib, rules):
    fp = folder_paths(lib)
    out = []
    variants = tuple(rules.get("variantSuffixes", []))
    for it in items(lib):
        if variants and it["name"].endswith(variants):
            continue  # 같은 그림의 큰 판 등 — 원본 에셋 노트를 함께 쓴다
        paths = [fp.get(f, "") for f in it.get("folders", [])]
        rule, folder = rule_for(paths, rules)
        if rule:
            out.append((it, rule, folder))
    return out


def related_of(it, rules):
    u = it.get("url") or ""
    related = ""
    if u.startswith("obsidian://open") and "file=" in u:
        related = urllib.parse.unquote(u.split("file=", 1)[1].split("&")[0])
        if related.startswith(rules["noteRoot"]):
            related, u = "", ""      # 예전 에셋 노트 링크 → 새 노트로 다시 쓴다
    return related, u


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    g.add_argument("--preview", metavar="EAGLE_NAME")
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
    targets = targets_of(lib, rules)

    if a.preview:
        hit = [t for t in targets if t[0]["name"] == a.preview]
        if not hit:
            sys.exit(f"✗ 규칙 대상 폴더에 그 이름의 에셋이 없음: {a.preview}")
        it, rule, folder = hit[0]
        print(note_text(it, rule, rules, folder, related_of(it, rules)[0], libname, command_fields(rules, vault)), end="")
        return

    have = existing_notes(root)
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
    extra = command_fields(rules, vault) if missing else {}
    names = vault_basenames(vault)
    made, url_jobs = [], []
    for it, rule, folder in missing:
        related, u = related_of(it, rules)
        base = it["name"] if it["name"] not in names else f"{it['name']} (asset)"
        d = os.path.join(root, rule["group"])
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, base + ".md")
        if os.path.exists(path):
            print("  건너뜀(같은 파일명 있음):", os.path.relpath(path, vault))
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(note_text(it, rule, rules, folder, related, libname, extra))
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
