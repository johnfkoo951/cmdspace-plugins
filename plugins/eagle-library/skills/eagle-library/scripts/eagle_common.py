"""eagle_common — eagle-library 스크립트 공통 함수 (Eagle 4.x 로컬 API + 라이브러리 파일 읽기).

설정은 JSON 파일 하나에서 읽는다 (경로를 코드에 박지 않는다):

  1. 환경 변수 EAGLE_LIBRARY_CONFIG 가 가리키는 파일
  2. 없으면 ~/.config/eagle-library/config.json

  {
    "vault": "/path/to/Your Vault",            # Obsidian 볼트 루트 (노트 링크 검사·갱신에 사용)
    "vaultName": "Your Vault",                 # obsidian://open?vault=… 에 쓰는 이름 (생략하면 vault 폴더 이름)
    "libraries": {                             # 별칭 → .library 경로. 스크립트의 --library/--from/--to 에 별칭을 쓴다
      "personal": "~/Eagle/Personal.library",
      "design": ["~/Shared/Design.library", "~/Library/CloudStorage/*/Shared/Design.library"]
    },
    "assetNotesRules": "~/.config/eagle-library/asset-notes-rules.json",  # 선택 (eagle_asset_notes.py)
    "taxonomy": "~/.config/eagle-library/taxonomy.md"                     # 선택: 사용자 정리 규칙 문서 (에이전트가 먼저 읽는다)
  }

경로 값은 문자열 하나 또는 후보 목록이다. 후보는 앞에서부터 실제로 있는 첫 경로를 쓰고, `*` 같은 glob 도 된다.
기기마다 경로가 다를 때(동기화 폴더 위치 등) 설정 파일 하나로 여러 기기를 쓸 수 있다.
상대경로는 설정 파일이 있는 폴더 기준이다.

환경 변수 EAGLE_VAULT 는 vault 를, EAGLE_API 는 API 주소(기본 http://localhost:41595/api)를 덮어쓴다.
설정이 없어도 --library 에 .library 절대경로를 직접 주면 동작한다.
지금 해석된 설정 보기: python3 eagle_common.py
"""
import glob
import json
import os
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request

CONFIG_PATH = os.path.expanduser(os.environ.get("EAGLE_LIBRARY_CONFIG") or "~/.config/eagle-library/config.json")


def _load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def resolve_path(value):
    """설정의 경로 값(문자열 또는 후보 목록) → 실제로 있는 첫 경로. 하나도 없으면 첫 후보를 그대로 돌려준다."""
    if not value:
        return ""
    cands = value if isinstance(value, list) else [value]
    base = os.path.dirname(os.path.realpath(CONFIG_PATH))
    full = [os.path.join(base, os.path.expanduser(c)) for c in cands]   # 절대경로면 join 이 base 를 무시한다
    for c in full:
        hits = sorted(glob.glob(c)) if any(ch in c for ch in "*?[") else ([c] if os.path.exists(c) else [])
        if hits:
            return hits[0]
    return full[0]


CONFIG = _load_config()
API = (os.environ.get("EAGLE_API") or CONFIG.get("api") or "http://localhost:41595/api").rstrip("/")
VAULT = os.path.expanduser(os.environ["EAGLE_VAULT"]) if os.environ.get("EAGLE_VAULT") else resolve_path(CONFIG.get("vault"))
VAULT_NAME = CONFIG.get("vaultName") or (os.path.basename(VAULT.rstrip("/")) if VAULT else "")
LIBS = {k: resolve_path(v) for k, v in (CONFIG.get("libraries") or {}).items()}
TAXONOMY = resolve_path(CONFIG.get("taxonomy"))
ASSET_NOTES_RULES = resolve_path(CONFIG.get("assetNotesRules"))


def lib_path(name):
    p = os.path.expanduser(LIBS.get(name, name))
    if not os.path.exists(os.path.join(p, "metadata.json")):
        hint = f" (설정 파일 {CONFIG_PATH} 의 libraries 에 별칭을 넣거나 .library 절대경로를 주세요)" if name not in LIBS else ""
        raise SystemExit(f"✗ 라이브러리를 찾을 수 없음: {p}{hint}")
    return p


def require_vault(vault):
    """볼트가 필요한 작업에서 호출. 설정·--vault 둘 다 없으면 멈춘다."""
    if not vault or not os.path.isdir(vault):
        raise SystemExit(f"✗ 볼트 경로가 없음: {vault or '(비어 있음)'} — --vault 를 주거나 {CONFIG_PATH} 에 \"vault\" 를 넣으세요")
    return vault


def call(path, body=None, v2=False):
    url = f"{API}/{'v2/' if v2 else ''}{path}"
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 method="POST" if body is not None else "GET",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.loads(r.read().decode())
    if res.get("status") != "success":
        raise RuntimeError(f"{path}: {res}")
    return res.get("data")


def active():
    return call("library/info")["library"]["path"]


def switch(path, timeout=40):
    """활성 라이브러리 전환 후 반영될 때까지 기다린다. Eagle 은 활성 라이브러리에만 쓸 수 있다."""
    if os.path.realpath(active()) == os.path.realpath(path):
        return
    call("library/switch", {"libraryPath": path})
    for _ in range(timeout):
        time.sleep(1)
        try:
            if os.path.realpath(active()) == os.path.realpath(path):
                time.sleep(2)   # 목록 로딩 여유
                return
        except Exception:
            pass
    raise SystemExit(f"✗ 라이브러리 전환 실패: {path}")


class keep_active:
    """작업이 끝나면(오류가 나도) 시작할 때 사용자가 보고 있던 라이브러리로 되돌린다.
    특정 라이브러리로 고정 복귀하지 않는다 — 사용자가 마지막으로 보던 화면을 유지한다.

        with keep_active():
            switch(target)
            ...                     # 쓰기 작업
    """
    def __enter__(self):
        self.start = active()
        return self

    def __exit__(self, *exc):
        try:
            switch(self.start)
            print(f"활성 라이브러리 복귀: {os.path.basename(self.start).replace('.library', '')}")
        except SystemExit as e:
            print(e)
        return False


def folder_paths(lib):
    """{folder_id: 'A/B/C'} — 라이브러리 metadata.json 에서 읽기 (앱 불필요)."""
    with open(os.path.join(lib, "metadata.json"), encoding="utf-8") as f:
        meta = json.load(f)
    out = {}

    def walk(nodes, prefix):
        for n in nodes:
            k = f"{prefix}/{n['name']}" if prefix else n["name"]
            out[n["id"]] = k
            walk(n.get("children", []), k)
    walk(meta.get("folders", []), "")
    return out


def items(lib, include_deleted=False):
    d = os.path.join(lib, "images")
    for x in os.listdir(d):
        if not x.endswith(".info"):
            continue
        try:
            with open(os.path.join(d, x, "metadata.json"), encoding="utf-8") as f:
                m = json.load(f)
        except Exception:
            continue
        if m.get("isDeleted") and not include_deleted:
            continue
        m["_dir"] = os.path.join(d, x)
        m["_file"] = os.path.join(d, x, f"{m['name']}.{m['ext']}")
        yield m


def find_notes(vault, pattern=None, fixed=None):
    """볼트에서 내용이 맞는 .md 파일 목록 (절대경로). pattern = 정규식, fixed = 고정 문자열 목록(하나라도 있으면).
    ripgrep(rg)이 있으면 쓰고, 없으면 Python 으로 훑는다. 숨김 폴더(.obsidian, .trash 등)는 건너뛴다."""
    if shutil.which("rg"):
        cmd = ["rg", "-l", "-g", "*.md"]
        if fixed:
            cmd += ["--fixed-strings"] + [x for s in fixed for x in ("-e", s)]
        else:
            cmd += ["-e", pattern]
        return subprocess.run(cmd + [vault], capture_output=True, text=True).stdout.splitlines()
    rx = re.compile(pattern) if pattern else None
    out = []
    for dp, dns, fs in os.walk(vault):
        dns[:] = [d for d in dns if not d.startswith(".")]
        for fn in fs:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(dp, fn)
            try:
                with open(p, encoding="utf-8") as f:
                    text = f.read()
            except Exception:
                continue
            if (fixed and any(s in text for s in fixed)) or (rx and rx.search(text)):
                out.append(p)
    return out


EAGLE_REF = r"\.library/images/|eagle://item/|41595/item\?id="


def vault_refs(vault=VAULT):
    """볼트 md 가 참조하는 Eagle 항목: {id: {notes}} (file:///…/images/{ID}.info/…, eagle://item/{ID}, 41595/item?id={ID}).
    볼트가 설정되지 않았으면 빈 dict."""
    if not vault or not os.path.isdir(vault):
        return {}
    refs = {}
    rx = re.compile(r"(?:\.library/images/|eagle://item/|41595/item\?id=)([A-Z0-9]{13})")
    for f in find_notes(vault, pattern=EAGLE_REF):
        try:
            with open(f, encoding="utf-8") as fh:
                text = fh.read()
        except Exception:
            continue
        for iid in set(rx.findall(text)):
            refs.setdefault(iid, set()).add(os.path.relpath(f, vault))
    return refs


# 파일명에 공백(<...> 형식)·괄호가 들어가도 확장자 + 닫는 괄호/꺾쇠까지를 한 링크로 본다.
# 그룹: 1=라이브러리 경로(…/X.library), 2=ID, 3=파일명(URL 인코딩 그대로)
FILE_LINK = re.compile(r"file://(/[^\n]+?\.library)/images/([A-Z0-9]{13})\.info/"
                       r"([^\n]+?\.(?:png|jpe?g|webp|gif|svg|mp4))(?=[)>\s]|$)", re.IGNORECASE)
# 라이브러리 폴더 이름 → 현재 위치 (라이브러리 폴더를 옮겨 깨진 옛 경로 링크를 복구할 때 쓴다).
# 설정의 libraries 에 등록한 라이브러리만 복구 대상이 된다.
LIB_BY_NAME = {os.path.basename(v.rstrip("/")): v for v in LIBS.values()}


def unquote(p):
    return urllib.parse.unquote(p)


def show_config():
    """해석된 설정을 사람이 읽게 출력한다 (에이전트가 작업 전에 확인용으로 돌린다)."""
    ok = lambda p: "✓" if p and os.path.exists(p) else "✗"
    print(f"config    {ok(CONFIG_PATH)} {CONFIG_PATH}")
    print(f"vault     {ok(VAULT)} {VAULT or '(없음)'}   name: {VAULT_NAME or '(없음)'}")
    for k, v in LIBS.items():
        print(f"library   {ok(os.path.join(v, 'metadata.json'))} {k}: {v}")
    print(f"taxonomy  {ok(TAXONOMY)} {TAXONOMY or '(없음 — references/taxonomy.example.md 를 참고)'}")
    print(f"rules     {ok(ASSET_NOTES_RULES)} {ASSET_NOTES_RULES or '(없음)'}")
    print(f"api       {API}")


if __name__ == "__main__":
    show_config()
