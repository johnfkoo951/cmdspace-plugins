# eagle-library

[![한국어](https://img.shields.io/badge/lang-한국어-green)](README.ko.md) [![English](https://img.shields.io/badge/lang-English-blue)](README.md)

**Let an agent file your images into Eagle without breaking the notes that link to them.**

[Eagle](https://eagle.cool) is a good home for generated images, screenshots and design assets. Once Obsidian notes link straight to Eagle's original files, though, small slips have big effects: renaming an item renames the file on disk, moving a library folder breaks every link, and re-adding an existing file silently merges into the old item. `eagle-library` is a Claude Code skill plus eight small Python scripts that handle these cases.

| Job | What it does |
|---|---|
| **File** | Imports from a JSON manifest with folders, names, tags, annotations and ratings. Skips duplicates by MD5, trashes replaced items *before* adding, and confirms a new item was really created |
| **Move** | Transfers items between libraries, rewrites `file:///` and `eagle://` links in your vault, checks no old ID is left, and only then trashes the originals |
| **Check** | Finds every Eagle link in the vault that no longer points to a file, and repairs links broken by moving a library folder |
| **Export** | Copies an Eagle folder into a project folder (video, web, docs). Re-runs only copy what changed; Eagle stays the source of truth |
| **Catalog** | Keeps one Obsidian note per asset (`type: visual-asset`) whose `image` is the Eagle original, so one Bases card view shows the whole library |

Write operations use the Eagle API and return to the library you were viewing when they finish. Read-only scripts never touch the app.

## Install

```text
/plugin marketplace add johnfkoo951/cmdspace-plugins
/plugin install eagle-library@cmdspace-plugins
```

On Claude Code 2.1.275 or later, one line also works: `/plugin install eagle-library --marketplace johnfkoo951/cmdspace-plugins`.

Manual install: copy `skills/eagle-library/` into `~/.claude/skills/` (Claude Code) or your agent's skills folder. A ZIP of the skill folder is attached to each [release](https://github.com/johnfkoo951/cmdspace-plugins/releases).

Requirements: Eagle 4.x running (local API on port 41595) for write operations, Python 3.9+. Optional: [ripgrep](https://github.com/BurntSushi/ripgrep) for faster vault search, [Pillow](https://pypi.org/project/pillow/) for `eagle_sheet.py`.

## Set up

Create `~/.config/eagle-library/config.json` (or point `EAGLE_LIBRARY_CONFIG` at another file). A template is in [`examples/config.example.json`](examples/config.example.json).

```json
{
  "vault": "~/Obsidian/Your Vault",
  "vaultName": "Your Vault",
  "libraries": {
    "personal": "~/Eagle/Personal.library",
    "design": "~/Shared/Team Design.library"
  },
  "assetNotesRules": "~/.config/eagle-library/asset-notes-rules.json"
}
```

| Key | Purpose |
|---|---|
| `vault` | Obsidian vault root. Needed for link checks, link rewrites and asset notes; leave it out if you only use Eagle |
| `vaultName` | Vault name used in `obsidian://open?vault=…` links (defaults to the folder name) |
| `libraries` | Short names for your `.library` folders. Scripts accept these names or a full path |
| `assetNotesRules` | Rules for asset notes (optional). Start from [`asset-notes-rules.example.json`](skills/eagle-library/references/asset-notes-rules.example.json) |

Then write down how you organize each library. [`taxonomy.example.md`](skills/eagle-library/references/taxonomy.example.md) is a template covering library roles, a folder tree, naming, tags, annotations, URLs and ratings. The agent reads it, and your existing items, before filing anything.

## Use

Open Claude Code and ask in plain words.

```text
Put these 12 generated images into the design library under Characters/Mascot.
이 이미지들 이글에 넣어줘. 태그랑 주석까지 정리해서.
Move these items from design to personal and keep my note links working.
Copy the Mascot Motion Kit folder from Eagle into ./public/assets/mascot.
Check that every Eagle link in my vault still works.
```

The agent writes a manifest, shows a dry run, imports, then verifies the result. You can also run the scripts directly:

```bash
S=skills/eagle-library/scripts
python3 $S/eagle_import.py manifest.json --dry-run          # then without --dry-run
python3 $S/eagle_transfer.py --from design --to personal --ids <ID…> --folder "10. Obsidian/13. Daily" --dry-run
python3 $S/eagle_linkcheck.py                               # exit 1 if any link is broken
python3 $S/eagle_export.py --library design --folder "Characters/Mascot" --recursive --dest ./assets
python3 $S/eagle_asset_notes.py --check                     # then --apply
python3 $S/eagle_sheet.py --library design --uncategorized --out /tmp/uncat
```

| Script | Needs the Eagle app |
|---|---|
| `eagle_import.py` · `eagle_transfer.py` | Yes |
| `eagle_asset_notes.py --apply` | Only to write the note link back into Eagle (`--no-url` skips it) |
| `eagle_linkcheck.py` · `eagle_relink.py` · `eagle_export.py` · `eagle_sheet.py` · `--check` | No, they read the library folder directly |

## Eagle pitfalls it guards against

Measured on Eagle 4.0.0:

- Adding a file identical to a live item does **not** create a new item; Eagle adds a folder to the old one and still reports success. Trash the old item first, then add, then confirm the new ID.
- The v1 `item/update` endpoint accepts `name` and `folders` and silently ignores them. Use `/api/v2/item/update`.
- Renaming an item renames the real file (`images/{ID}.info/{name}.png`), which breaks notes that link to it. Never rename linked items; moving between folders is safe.
- Writes only work on the active library. The scripts switch when needed and switch back to whatever you were looking at.
- In a smart-folder rule, several tags in one `value` means *all* tags. Use one rule per tag with `match: "OR"`.

## Asset notes and the Bases gallery

`eagle_asset_notes.py` creates one note per Eagle item in the folders you list in the rules file. Each note's `image` property is the URL-encoded `file:///` path of the Eagle original, so a Bases card view renders it without copying the image into the vault. A sample Base is in [`skills/eagle-library/assets/Visual Assets.base`](skills/eagle-library/assets/Visual%20Assets.base). Notes you have already edited are never overwritten.

## Companion

[CMDS Eagle](https://github.com/johnfkoo951/cmds-eagle) is an Obsidian plugin for searching and embedding Eagle items inside Obsidian. Links it creates are covered by the checks above.

## Tests

```bash
python3 skills/eagle-library/scripts/test_eagle_scripts.py
```

The tests build a fake Eagle library and vault in a temp folder and run every script, including `eagle_import.py --dry-run` against a stub API. The Eagle app is not needed.

## Language

The skill instructions and script messages are in Korean because the workflow was built for a Korean vault. Claude follows them in English conversations too; notes generated by `eagle_asset_notes.py` use English headings.

## Author

Yohan Koo (CMDSPACE) · <https://cmdspace.work>

MIT License.
