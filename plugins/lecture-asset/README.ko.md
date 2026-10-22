# lecture-asset

[![한국어](https://img.shields.io/badge/lang-한국어-green)](README.ko.md) [![English](https://img.shields.io/badge/lang-English-blue)](README.md)

**끝난 강의를 다시 꺼내 쓰는 노트로 바꿉니다.**

옵시디언에 요약, 인덱싱, 연결 플러그인을 여러 개 붙여도 석 달 뒤에 배운 것을 다시 찾기 어려운 경우가 많습니다. `lecture-asset`은 플러그인을 더 붙이는 대신 몇 가지 규칙과 에이전트로 그 일을 하는 Claude Code 스킬입니다.

| 하는 일 | 볼트에 생기는 것 |
|---|---|
| **요약·인덱싱** | 강의마다 허브 노트 하나(한 줄 명제, 타임코드가 붙은 카드 목차) + 모든 강의를 한 번에 보는 Obsidian Bases 표 하나 |
| **원소화** | 강의마다 주장 카드 8~16장. 카드 하나에 주장 하나, 제목은 그 주장을 문장으로 |
| **상호 연결** | 카드마다 `## 연결` 절. 다음 강의에서 같은 주장이 나오면 새 카드를 만들지 않고 기존 카드에 누적 |

여기에 전사 원문을 바이트 그대로 보존하고(SHA-256 기록), 회고는 **잘한 것을 먼저, 고칠 것을 다음에** 적고, 마지막에 읽기 전용 마감 게이트로 빠진 단계를 잡습니다.

옵시디언 기본 기능(Properties, 위키링크, 콜아웃, Bases)만 씁니다. 커뮤니티 플러그인은 필요 없습니다.

## 설치

```text
/plugin marketplace add johnfkoo951/cmdspace-plugins
/plugin install lecture-asset@cmdspace-plugins
```

Claude Code 2.1.275 이상에서는 한 줄로도 됩니다: `/plugin install lecture-asset --marketplace johnfkoo951/cmdspace-plugins`

직접 설치: `skills/lecture-asset/` 폴더를 `~/.claude/skills/`(Claude Code)나 쓰는 에이전트의 스킬 폴더(Codex는 `.agents/skills/` 등)에 복사합니다. 스킬 폴더 ZIP은 [릴리스](https://github.com/johnfkoo951/cmdspace-plugins/releases)에 첨부되어 있습니다.

필요한 것: 검사기용 Python 3.9 이상, 표 링크 검사기용 `pip install markdown-it-py`.

## 사용

볼트에서 Claude Code를 열고 전사본을 건넵니다.

```text
강의 자산화해줘. 어제 세미나 전사본이야. (전사본 첨부 또는 붙여 넣기)
```

처음 실행하면 폴더 위치를 묻습니다. 스킬 안의 경로는 `{projects}`, `{cards}` 같은 자리표시자입니다. 답한 값을 볼트의 `CLAUDE.md`에 적어 두면 다음부터 묻지 않습니다.

| 자리표시자 | 예시 | 용도 |
|---|---|---|
| `{projects}` | `Outputs/Lectures/` | 강의 준비 자료와 강의 기록 |
| `{cards}` | `Assets/Lecture Cards/` | 주장 카드 라이브러리, 강의마다 하위 폴더 하나 |
| `{shared}` | `Assets/Lecture Cards/_Shared/` | 여러 강의 카드가 함께 가리키는 공통 노트 (선택) |
| `{base}` | `Bases/Lecture.base` | 모든 강의를 보는 Base 파일 하나 |
| `{corrections}` | `Assets/Transcription/corrections.yaml` | STT 오인식 교정 목록 (선택) |
| `{wiki-vault}` | `My Wiki` | 개념을 따로 정리하는 두 번째 볼트 (선택) |

## 결과물

```text
{projects}/2026-01-15-sample-seminar/
├── 2026-01-15 샘플 세미나 - 제목.lecture.md     ← 허브 (type: lecture)
├── 2026-01-15 샘플 세미나 - 전사본.md            ← 원문 그대로 (type: transcript)
└── 01-강의-회고와-개선.md                        ← 회고: 잘한 것, 그다음 바꿀 것

{cards}/2026-01-15 샘플 세미나/
└── <문장으로 쓴 주장>.md × 8~16장               ← type: lecture-chunk

{base}                                           ← Base 하나, type으로 필터
```

## 샘플 볼트

[`examples/sample-vault/`](examples/sample-vault/)는 가상의 세미나 하나를 처리한 결과입니다. 허브, 보존된 전사본, 주장 카드 3장, 공통 자산, 회고, Base가 들어 있습니다. 폴더를 옵시디언에서 볼트로 열면 서로 어떻게 연결되는지 볼 수 있습니다.

마감 게이트 실행:

```bash
cd plugins/lecture-asset/examples/sample-vault
python3 ../../skills/lecture-asset/scripts/check_asset_run.py --root "$PWD" \
  --hub "Outputs/Lectures/2026-01-15-sample-seminar/2026-01-15 샘플 세미나 - 노트는 주장으로 남긴다.lecture.md" \
  --cards-dir "Assets/Lecture Cards/2026-01-15 샘플 세미나" \
  --preserve "../raw/2026-01-15-sample-transcript.txt::Outputs/Lectures/2026-01-15-sample-seminar/2026-01-15 샘플 세미나 - 전사본.md"
# summary: FAIL=0 ...
```

## 마감 게이트

`scripts/check_asset_run.py`는 읽기만 합니다. 아래 중 하나라도 실패하면 종료 코드 1을 냅니다.

| 검사 | 잡는 실수 |
|---|---|
| 작업 시작 뒤 SKILL.md가 바뀌었나 | 작업 중 추가된 단계를 건너뜀 |
| 새 카드마다 `lectures:`에 허브, `## 연결` 절, 자기 강의 폴더 밖으로 가는 링크가 있나 | 한 강의 안에 고립된 카드 |
| 위키링크가 파일 하나로 정확히 풀리나 | 같은 이름의 다른 강의 노트가 열림 |
| `obsidian://` 링크 대상이 그 볼트에 실제로 있나 | 두 번째 볼트 경로를 손으로 조립한 실수 |
| 허브가 회고를 링크하고 전사본을 지정했나 | 회고 단계 누락 |
| 전사 원문이 노트 안에 바이트 그대로 있나 | "읽기 좋게" 고친 원문 |

`scripts/check_table_wikilinks.py`는 표 안 위키링크의 별칭 구분자가 `[[대상\|표시명]]`으로 이스케이프됐는지 검사해서 표에 빈 열이 생기는 것을 막습니다. 회귀 시험: `test_asset_run.py`, `test_table_wikilinks.py`.

## 만든 사람

Yohan Koo (CMDSPACE) · <https://cmdspace.work>

MIT License.
