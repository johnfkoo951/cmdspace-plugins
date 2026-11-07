# Changelog

Versions are per plugin (each plugin's `.claude-plugin/plugin.json`). The marketplace index has its own version in `.claude-plugin/marketplace.json`.

## 2026-11-07 · eagle-library 1.1.0

### Added
- Config paths may be a list of candidates (first existing wins, `*` globs allowed), so one config file serves several machines. Relative paths resolve next to the real config file.
- `taxonomy` config key: the user's own filing rules. SKILL.md now has the agent print the resolved config (`python3 scripts/eagle_common.py`) and read the taxonomy first; user-specific rules belong there, not in the skill.
- Asset-note rules without code changes: `category` (value from tags, folder or keywords, with per-value properties, body lines and fallback scene), `lang` (`en`/`ko` headings), `fieldOrder`, `descriptionTemplate` + `kindLabels`, `titlePatterns`, `titleTagPattern`, `commandFields`. Every key is documented in `asset-notes-rules.example.json` (`_docKeys`).
- `eagle_asset_notes.py --preview <name>` prints one note without writing it.
- 5 more regression tests (19 total).

### Fixed
- Folder rule `prefix` is a plain string prefix again, as in the original private skill. 1.0.0 required a `/` boundary, which silently skipped folders such as `01 Characters · Mascot` under a `01 Characters` rule.

### Verified
- Against the author's real libraries and vault, read-only: 653/653 asset notes identical to the private edition (properties, order, body); link check, export list, contact-sheet index, transfer and import dry runs identical.

## 2026-11-07 · eagle-library 1.0.0 · marketplace 1.2.0

### Added
- **eagle-library** plugin: a skill for filing assets into Eagle (eagle.cool) libraries through the local API while keeping Obsidian notes that link to Eagle originals intact.
  - `eagle_import.py`: manifest import with MD5 duplicate skip, trash-before-add replacement, new-ID verification, optional `--switch` that returns to the library you were viewing.
  - `eagle_transfer.py`, `eagle_relink.py`: move items between libraries and rewrite `file:///` and `eagle://` links in the vault (notes backed up first).
  - `eagle_linkcheck.py`: read-only check of every Eagle link in the vault; `--ids` residue check; `--fix-moved` repair after a library folder moves.
  - `eagle_export.py`: copy an Eagle folder into a project folder; re-runs copy only changed files.
  - `eagle_asset_notes.py`: one `type: visual-asset` note per Eagle item for a Bases image gallery (`assets/Visual Assets.base`); existing notes are never overwritten.
  - `eagle_sheet.py`: numbered contact sheets for sorting uncategorized items.
  - Paths come from `~/.config/eagle-library/config.json` (`EAGLE_LIBRARY_CONFIG`, `EAGLE_VAULT`, `EAGLE_API` override). Vault search falls back to pure Python when ripgrep is missing.
  - Templates: `taxonomy.example.md`, `asset-notes-rules.example.json`, `examples/config.example.json`, `examples/manifest.example.json`.
  - `test_eagle_scripts.py`: 14 regression tests on a fake library and vault, including an import dry run against a stub API.

### Changed
- Root READMEs list eagle-library.

## 2026-10-23 · lecture-asset 1.0.0 · marketplace 1.1.0

### Added
- **lecture-asset** plugin: a post-lecture skill that turns a talk transcript into Obsidian knowledge assets.
  - Hub note per talk (one-line thesis, card table of contents with timecodes) and one Bases view for all talks (`assets/Lecture.base`).
  - Raw transcript kept byte-for-byte, with `sourceBodySha256`.
  - 8 to 16 atomic claim cards per talk; repeated claims accumulate into the existing card.
  - Retrospective that records what worked before what to change.
  - `scripts/check_asset_run.py`: read-only closing gate (skill changed mid-run, isolated cards, ambiguous links, broken `obsidian://` paths, missing retrospective, edited transcript).
  - `scripts/check_table_wikilinks.py`: checks escaped wikilink aliases inside Markdown tables.
  - Fictional sample vault under `examples/sample-vault/`, regression tests for both checkers.
- Korean root README (`README.ko.md`), this changelog, and a LICENSE file for the MIT license the README already stated.

### Changed
- Root README lists lecture-asset, uses `/plugin` install commands, and links https://cmdspace.work.

## 2026-02-10 · dev-orchestrator 1.0.0

- Initial release.

## 2026-02-10 · research-pipeline 1.0.0

- Initial release. Phase 6 web deployment option added later; see the git history.
