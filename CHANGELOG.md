# Changelog

Versions are per plugin (each plugin's `.claude-plugin/plugin.json`). The marketplace index has its own version in `.claude-plugin/marketplace.json`.

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
