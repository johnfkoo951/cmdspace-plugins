#!/usr/bin/env python3
"""Regression tests for the eagle-library scripts.

Builds a fake Eagle library (an Eagle library is just a folder: metadata.json + images/<ID>.info/),
a fake Obsidian vault and a config file in a temp dir, then runs each CLI as a subprocess.
The Eagle app is not needed: eagle_import.py --dry-run talks to a tiny fake API server.

  python3 test_eagle_scripts.py
"""
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
# 1x1 transparent PNG
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
ID1, ID2, ID3, NEW1 = "KTEST00000001", "KTEST00000002", "KTEST00000003", "NTEST00000001"


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def make_library(path, folders, entries):
    os.makedirs(os.path.join(path, "images"), exist_ok=True)
    write_json(os.path.join(path, "metadata.json"), {"folders": folders})
    for e in entries:
        d = os.path.join(path, "images", f"{e['id']}.info")
        os.makedirs(d, exist_ok=True)
        meta = dict(ext="png", folders=[], tags=[], annotation="", url="", isDeleted=False,
                    btime=1736900000000, width=1, height=1)
        meta.update(e)
        write_json(os.path.join(d, "metadata.json"), meta)
        with open(os.path.join(d, f"{meta['name']}.png"), "wb") as f:
            f.write(PNG + e["id"].encode())   # different bytes per item → different md5


def file_link(lib, iid, name):
    return "file://" + urllib.parse.quote(os.path.join(lib, "images", f"{iid}.info", name))


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.design = os.path.join(self.tmp, "libs", "Team Design.library")
        self.personal = os.path.join(self.tmp, "libs", "Personal.library")
        self.vault = os.path.join(self.tmp, "Test Vault")
        folders = [{"id": "F1", "name": "Characters", "children": [
            {"id": "F2", "name": "Mascot", "children": [{"id": "F3", "name": "Scenes", "children": []}]}]}]
        make_library(self.design, folders, [
            dict(id=ID1, name="mascot-wave", folders=["F2"], tags=["character", "Mascot", "lecture"],
                 annotation="image-gen 2026-01-15 · gen: gpt-test · Scene: mascot waving"),
            dict(id=ID2, name="scene lecture (hall)", folders=["F3"], tags=["scene", "강의"]),
            dict(id=ID3, name="deleted-one", folders=["F2"], isDeleted=True),
        ])
        make_library(self.personal, [], [dict(id=NEW1, name="mascot-wave")])
        os.makedirs(os.path.join(self.vault, "Notes"))
        os.makedirs(os.path.join(self.vault, ".obsidian"))
        self.note = os.path.join(self.vault, "Notes", "linked.md")
        with open(self.note, "w") as f:
            f.write(f"# Linked\n![wave]({file_link(self.design, ID1, 'mascot-wave.png')})\n"
                    f"![hall]({file_link(self.design, ID2, 'scene lecture (hall).png')})\n"
                    f"[open](eagle://item/{ID2})\n")
        self.rules = os.path.join(self.tmp, "rules.json")
        rules = read_json(os.path.join(HERE, "..", "references", "asset-notes-rules.example.json"))
        rules.update(library="design", noteRoot="Assets/Visual Assets", overrides={},
                     folders=[{"prefix": "Characters/Mascot", "group": "Mascot", "assetKind": "Character",
                               "usage": ["slides"]}])
        write_json(self.rules, rules)
        self.config = os.path.join(self.tmp, "config.json")
        write_json(self.config, {"vault": self.vault, "vaultName": "Test Vault",
                   "libraries": {"design": self.design, "personal": self.personal},
                   "assetNotesRules": self.rules})
        self.env = dict(os.environ, EAGLE_LIBRARY_CONFIG=self.config)
        self.env.pop("EAGLE_VAULT", None)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_script(self, name, *args, env=None):
        return subprocess.run([sys.executable, os.path.join(HERE, name), *args],
                              capture_output=True, text=True, env=env or self.env, cwd=self.tmp)


class TestExport(Fixture):
    def test_list_counts_live_items_only(self):
        r = self.run_script("eagle_export.py", "--library", "design", "--list", "Characters")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1  Characters/Mascot", r.stdout)        # deleted item not counted
        self.assertIn("1  Characters/Mascot/Scenes", r.stdout)

    def test_recursive_export_then_rerun_is_unchanged(self):
        dest = os.path.join(self.tmp, "out")
        r = self.run_script("eagle_export.py", "--library", "design", "--folder", "Characters/Mascot",
                            "--recursive", "--dest", dest)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(dest, "mascot-wave.png")))
        self.assertTrue(os.path.exists(os.path.join(dest, "Scenes", "scene-lecture-(hall).png")))
        r = self.run_script("eagle_export.py", "--library", "design", "--folder", "Characters/Mascot",
                            "--recursive", "--dest", dest)
        self.assertIn("new 0 · changed 0 · unchanged 2", r.stdout)

    def test_unknown_alias_fails_with_hint(self):
        r = self.run_script("eagle_export.py", "--library", "nope", "--list")
        self.assertNotEqual(r.returncode, 0)


class TestLinks(Fixture):
    def test_linkcheck_ok_with_and_without_ripgrep(self):
        r = self.run_script("eagle_linkcheck.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("깨짐: 0", r.stdout)
        no_rg = dict(self.env, PATH="/usr/bin:/bin")              # forces the pure-Python search
        r = self.run_script("eagle_linkcheck.py", env=no_rg)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("깨짐: 0", r.stdout)

    def test_linkcheck_reports_broken(self):
        with open(os.path.join(self.vault, "Notes", "broken.md"), "w") as f:
            f.write(f"eagle://item/KTEST00000099\n![x]({file_link(self.design, ID1, 'gone.png')})\n")
        r = self.run_script("eagle_linkcheck.py")
        self.assertEqual(r.returncode, 1)
        self.assertIn("깨짐: 2", r.stdout)

    def test_ids_residue_check(self):
        r = self.run_script("eagle_linkcheck.py", "--ids", ID1)
        self.assertEqual(r.returncode, 1)
        r = self.run_script("eagle_linkcheck.py", "--ids", "ZZZZZZZZZZZZZ")
        self.assertEqual(r.returncode, 0)

    def test_fix_moved_library(self):
        old = os.path.join(self.tmp, "old place", "Team Design.library")
        with open(os.path.join(self.vault, "Notes", "moved.md"), "w") as f:
            f.write(f"![m]({file_link(old, ID1, 'mascot-wave.png')})\n")
        self.assertEqual(self.run_script("eagle_linkcheck.py").returncode, 1)
        r = self.run_script("eagle_linkcheck.py", "--fix-moved", "--apply")
        self.assertIn("옛 라이브러리 경로 링크 1개", r.stdout)
        self.assertEqual(self.run_script("eagle_linkcheck.py").returncode, 0)

    def test_relink_to_new_library(self):
        idmap = os.path.join(self.tmp, "idmap.json")
        write_json(idmap, {ID1: NEW1})
        before = read(self.note)
        r = self.run_script("eagle_relink.py", "--map", idmap, "--to", "personal")
        self.assertIn("[dry] 바뀔 곳 1", r.stdout)
        self.assertEqual(read(self.note), before)          # dry-run writes nothing
        r = self.run_script("eagle_relink.py", "--map", idmap, "--to", "personal", "--apply",
                            "--backup-dir", os.path.join(self.tmp, "bak"))
        self.assertEqual(r.returncode, 0, r.stderr)
        after = read(self.note)
        self.assertNotIn(ID1, after)
        self.assertIn(file_link(self.personal, NEW1, "mascot-wave.png"), after)
        self.assertIn(ID2, after)                                 # unrelated links untouched
        self.assertEqual(self.run_script("eagle_linkcheck.py").returncode, 0)

    def test_vault_required(self):
        env = dict(self.env)
        write_json(self.config, {"libraries": {"design": self.design}})
        r = self.run_script("eagle_linkcheck.py", env=env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("볼트 경로가 없음", r.stdout + r.stderr)


class TestAssetNotes(Fixture):
    def test_check_apply_check(self):
        r = self.run_script("eagle_asset_notes.py", "--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("노트 없음 2", r.stdout)
        r = self.run_script("eagle_asset_notes.py", "--apply", "--no-url")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("노트 생성 2", r.stdout)
        note = read(os.path.join(self.vault, "Assets", "Visual Assets", "Mascot", "mascot-wave.md"))
        self.assertIn("type: visual-asset", note)
        self.assertIn(f"eagleId: {ID1}", note)
        self.assertIn('scene: "Teaching"', note)                   # sceneKeywords: lecture
        self.assertIn('genModel: "gpt-test"', note)
        self.assertIn('  - "[[Your Name]]"', note)
        self.assertIn('image: "' + file_link(self.design, ID1, "mascot-wave.png") + '"', note)
        r = self.run_script("eagle_asset_notes.py", "--check")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_existing_note_not_overwritten(self):
        self.run_script("eagle_asset_notes.py", "--apply", "--no-url")
        p = os.path.join(self.vault, "Assets", "Visual Assets", "Mascot", "mascot-wave.md")
        with open(p, "a") as f:
            f.write("hand edit\n")
        self.run_script("eagle_asset_notes.py", "--apply", "--no-url")
        self.assertTrue(read(p).endswith("hand edit\n"))

    def test_missing_rules_points_to_example(self):
        r = self.run_script("eagle_asset_notes.py", "--check", "--rules", os.path.join(self.tmp, "none.json"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("asset-notes-rules.example.json", r.stdout + r.stderr)


class TestSheet(Fixture):
    def test_sheet_and_index(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow not installed")
        out = os.path.join(self.tmp, "sheet")
        r = self.run_script("eagle_sheet.py", "--library", "design", "--folder", "Characters/Mascot", "--out", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(out + "-0.png"))
        index = read_json(out + ".json")
        self.assertEqual(index[0]["notes"], ["Notes/linked.md"])


class TestConfig(Fixture):
    def test_candidates_glob_and_relative_paths(self):
        cfg_dir = os.path.join(self.tmp, "cfg")
        os.makedirs(cfg_dir)
        shutil.copy(self.rules, os.path.join(cfg_dir, "my-rules.json"))
        self.config = os.path.join(cfg_dir, "config.json")
        write_json(self.config, {
            "vault": [os.path.join(self.tmp, "missing vault"), self.vault],
            "libraries": {"design": [os.path.join(self.tmp, "nope", "Team Design.library"),
                                     os.path.join(self.tmp, "l*s", "Team Design.library")],
                          "personal": self.personal},
            "assetNotesRules": "my-rules.json", "taxonomy": "taxonomy.md"})
        env = dict(self.env, EAGLE_LIBRARY_CONFIG=self.config)
        r = self.run_script("eagle_common.py", env=env)
        self.assertIn(f"vault     ✓ {self.vault}", r.stdout)
        self.assertIn(f"design: {self.design}", r.stdout)                     # glob candidate resolved
        real_cfg = os.path.realpath(cfg_dir)                                   # relative paths follow the real config location
        self.assertIn(f"rules     ✓ {os.path.join(real_cfg, 'my-rules.json')}", r.stdout)
        self.assertIn("taxonomy  ✗", r.stdout)
        r = self.run_script("eagle_asset_notes.py", "--check", env=env)      # rules found through config
        self.assertIn("노트 없음 2", r.stdout)


class TestAssetNoteRules(Fixture):
    def setUp(self):
        super().setUp()
        folders = [{"id": "F1", "name": "Characters", "children": [
            {"id": "F2", "name": "Mascot", "children": [{"id": "F3", "name": "Scenes", "children": []}]},
            {"id": "F4", "name": "Mascot · extra", "children": []}]}]
        make_library(self.design, folders, [
            dict(id="KTEST00000004", name="persona-901", folders=["F4"], tags=["character", "team.a"],
                 annotation="image-gen 2026-02-01 · Persona 901 Kepler, the mapper")])
        rules = read_json(self.rules)
        rules.update(
            lang="ko", titleKeys=["Scene:"], titlePatterns=[{"pattern": r"Persona (\d{3}) (\w+)", "format": "{1} {2}"}],
            descriptionTemplate="{kindLabel} '{name}' for {usage}.", kindLabels={"Character": "Character art"},
            commandFields={"source-link": [sys.executable, "-c", "print('app://test')"]},
            extraFrontmatter={"status": "completed"},
            fieldOrder=["type", "aliases", "description", "team", "status", "scene"],
            folders=[{"prefix": "Characters/Mascot", "group": "Mascot", "assetKind": "Character", "usage": ["slides"],
                      "categoryFromTags": True}],
            category={"fromTags": {"team.a": "a"}, "keywords": [["b", ["lecture"]]], "default": "c",
                      "values": {k: {"frontmatter": {"team": f"[[Team {k.upper()}]]"}, "scene": f"Scene {k.upper()}",
                                     "body": [f"## 담당", f"- 팀 {k.upper()} · 장면 {{scene}}"]} for k in "abc"}})
        rules["sceneKeywords"] = []
        write_json(self.rules, rules)

    def preview(self, name):
        r = self.run_script("eagle_asset_notes.py", "--preview", name)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_prefix_is_plain_string_prefix(self):
        r = self.run_script("eagle_asset_notes.py", "--check")
        self.assertIn("대상 에셋 3", r.stdout)                                # 'Mascot · extra' matches 'Characters/Mascot'

    def test_category_from_tags_and_keywords_and_default(self):
        a, b, c = self.preview("persona-901"), self.preview("mascot-wave"), self.preview("scene lecture (hall)")
        self.assertIn('team: "[[Team A]]"', a)                                # fromTags
        self.assertIn('team: "[[Team B]]"', b)                                # keyword 'lecture' in tags
        self.assertIn('team: "[[Team B]]"', c)                                # keyword in name
        self.assertIn('scene: "Scene A"', a)                                  # category scene fallback
        self.assertIn("- 팀 A · 장면 Scene A", a)                              # body line with {scene}

    def test_lang_order_template_title_and_command(self):
        a = self.preview("persona-901")
        self.assertIn("## 장면\n", a)
        self.assertIn("## 사용처\n", a)
        self.assertIn("- 파일: `", a)
        self.assertIn('description: "Character art \'persona-901\' for slides."', a)
        self.assertIn('  - "901 Kepler"', a)                                  # title from titlePatterns → alias
        self.assertIn('source-link: "app://test"', a)
        keys = [ln.split(":")[0] for ln in a.split("---\n")[1].splitlines() if not ln.startswith("  ")]
        self.assertEqual(keys[:6], ["type", "aliases", "description", "team", "status", "scene"])

    def test_preview_unknown_name(self):
        r = self.run_script("eagle_asset_notes.py", "--preview", "nope")
        self.assertNotEqual(r.returncode, 0)


class FakeEagle(BaseHTTPRequestHandler):
    lib = ""

    def do_GET(self):
        if self.path.startswith("/api/library/info"):
            data = {"library": {"path": FakeEagle.lib}}
        elif self.path.startswith("/api/folder/list"):
            data = []
        else:
            self.send_response(404); self.end_headers(); return
        body = json.dumps({"status": "success", "data": data}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


class TestImportDryRun(Fixture):
    def test_dry_run_skips_duplicates_and_plans_folders(self):
        FakeEagle.lib = self.design
        srv = HTTPServer(("127.0.0.1", 0), FakeEagle)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            new = os.path.join(self.tmp, "new.png")
            with open(new, "wb") as f:
                f.write(PNG + b"new")
            dup = os.path.join(self.design, "images", f"{ID1}.info", "mascot-wave.png")
            manifest = os.path.join(self.tmp, "manifest.json")
            write_json(manifest, {"library": self.design, "items": [
                {"path": new, "folder": "Characters/New", "name": "new-one", "tags": ["x"]},
                {"path": dup, "folder": "Characters/New", "name": "dup"}]})
            env = dict(self.env, EAGLE_API=f"http://127.0.0.1:{srv.server_port}/api")
            r = self.run_script("eagle_import.py", manifest, "--dry-run", env=env)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("[dry] create folder: Characters/New", r.stdout)
            self.assertIn("이미 있음: dup", r.stdout)
            self.assertIn("added 1 · skipped 1 · failed 0", r.stdout)
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
