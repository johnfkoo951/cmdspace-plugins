# lecture-asset

[![한국어](https://img.shields.io/badge/lang-한국어-green)](README.ko.md) [![English](https://img.shields.io/badge/lang-English-blue)](README.md)

**Turn a finished lecture into notes you will actually reuse.**

Many Obsidian users add plugin after plugin for summarizing, indexing and linking, and still cannot find what they learned three months later. `lecture-asset` is a Claude Code skill that does those jobs with a few conventions and an agent, not with more plugins.

| Job | What you get in the vault |
|---|---|
| **Summarize and index** | One hub note per talk (one-line thesis, card table of contents with timecodes), plus a single Obsidian Bases view across all talks |
| **Atomize** | 8 to 16 claim cards per talk. One claim per card, and the title is the claim written as a sentence |
| **Interconnect** | Every card has a links section. A claim that shows up again in a later talk is added to the existing card instead of becoming a duplicate |

It also keeps the raw transcript byte-for-byte (with a SHA-256), writes a retrospective that records **what worked before what to fix**, and ends with a read-only closing gate that catches missed steps.

It uses only core Obsidian features: Properties, wikilinks, callouts and Bases. No community plugin is required.

## Install

```text
/plugin marketplace add johnfkoo951/cmdspace-plugins
/plugin install lecture-asset@cmdspace-plugins
```

On Claude Code 2.1.275 or later, one line also works: `/plugin install lecture-asset --marketplace johnfkoo951/cmdspace-plugins`.

Manual install: copy `skills/lecture-asset/` into `~/.claude/skills/` (Claude Code) or into your agent's skills folder (for example `.agents/skills/` for Codex). A ZIP of the skill folder is attached to each [release](https://github.com/johnfkoo951/cmdspace-plugins/releases).

Requirements: Python 3.9+ for the checkers, and `pip install markdown-it-py` for the table link checker.

## Use

Open Claude Code in your vault and hand it a transcript.

```text
강의 자산화해줘. 어제 세미나 전사본이야. (attach or paste the transcript)
Turn this talk transcript into lecture assets.
```

On the first run the skill asks where your folders are. The paths in the skill are placeholders such as `{projects}` and `{cards}`; save your answers in your vault's `CLAUDE.md` so it does not ask again.

| Placeholder | Example | Purpose |
|---|---|---|
| `{projects}` | `Outputs/Lectures/` | Lecture prep material and lecture records |
| `{cards}` | `Assets/Lecture Cards/` | Claim card library, one subfolder per talk |
| `{shared}` | `Assets/Lecture Cards/_Shared/` | Notes that cards from many talks link to (optional) |
| `{base}` | `Bases/Lecture.base` | The one Bases file for all talks |
| `{corrections}` | `Assets/Transcription/corrections.yaml` | Speech-to-text correction list (optional) |
| `{wiki-vault}` | `My Wiki` | A second vault for concepts (optional) |

## What it produces

```text
{projects}/2026-01-15-sample-seminar/
├── 2026-01-15 Sample Seminar - Title.lecture.md   ← hub (type: lecture)
├── 2026-01-15 Sample Seminar - 전사본.md            ← raw transcript, unchanged (type: transcript)
└── 01-강의-회고와-개선.md                            ← retrospective: what worked, then what to change

{cards}/2026-01-15 Sample Seminar/
└── <claim written as a sentence>.md × 8–16          ← type: lecture-chunk

{base}                                               ← one Base, filtered by type
```

## Try the sample vault

[`examples/sample-vault/`](examples/sample-vault/) is a small fictional run: one seminar, its hub, preserved transcript, three claim cards, a shared asset, a retrospective and the Base. Open the folder as a vault in Obsidian to see how the pieces link.

Run the closing gate on it:

```bash
cd plugins/lecture-asset/examples/sample-vault
python3 ../../skills/lecture-asset/scripts/check_asset_run.py --root "$PWD" \
  --hub "Outputs/Lectures/2026-01-15-sample-seminar/2026-01-15 샘플 세미나 - 노트는 주장으로 남긴다.lecture.md" \
  --cards-dir "Assets/Lecture Cards/2026-01-15 샘플 세미나" \
  --preserve "../raw/2026-01-15-sample-transcript.txt::Outputs/Lectures/2026-01-15-sample-seminar/2026-01-15 샘플 세미나 - 전사본.md"
# summary: FAIL=0 ...
```

## The closing gate

`scripts/check_asset_run.py` only reads. It exits 1 if anything below fails.

| Check | Mistake it catches |
|---|---|
| Did SKILL.md change after the run started? | A step added mid-run gets skipped |
| Does every new card list the hub in `lectures:`, have a links section, and link outside its own talk folder? | Cards isolated inside one talk |
| Does every wikilink resolve to exactly one file? | A short link opening another talk's note of the same name |
| Does every `obsidian://` link point to a file that exists in that vault? | A hand-built path to a second vault |
| Does the hub link the retrospective and name its transcript? | Skipped retrospective |
| Is the raw transcript inside the note byte-for-byte? | A "cleaned up" original |

`scripts/check_table_wikilinks.py` checks that wikilink aliases inside Markdown tables are escaped (`[[target\|alias]]`) so tables do not grow phantom columns. Regression tests: `test_asset_run.py`, `test_table_wikilinks.py`.

## Language

The skill and the sample are written in Korean because the workflow was built for Korean lectures. Claude follows it for English transcripts as well, and the gate also accepts `## Links` as the links heading.

## Author

Yohan Koo (CMDSPACE) · <https://cmdspace.work>

MIT License.
