# CMDSPACE Plugins

[![한국어](https://img.shields.io/badge/lang-한국어-green)](README.ko.md) [![English](https://img.shields.io/badge/lang-English-blue)](README.md)

[CMDSPACE](https://cmdspace.work)(구요한)가 만든 Claude Code 플러그인 모음입니다.

## 플러그인

| 플러그인 | 하는 일 |
|---|---|
| [lecture-asset](plugins/lecture-asset/README.ko.md) | 끝난 강의의 전사본을 옵시디언 지식 자산으로 바꿉니다: 허브 노트, 원문 보존 전사본, 주장 카드(원소화), Bases 인덱스, 마감 게이트 |
| [research-pipeline](plugins/research-pipeline/) | 서브 에이전트 5개로 문헌 탐색부터 학술지 투고까지 잇는 연구 파이프라인 |
| [dev-orchestrator](plugins/dev-orchestrator/) | 3계층 에이전트로 기획부터 문서화까지 다루는 개발 오케스트레이터 |

### lecture-asset

끝난 강의를 다시 꺼내 쓰는 노트로 바꿉니다. 강의 하나가 요약·인덱스 역할을 하는 허브 노트, 바이트 그대로 보존한 전사본, 볼트의 다른 노트와 연결된 주장 카드 8~16장(카드 하나에 주장 하나, 제목은 문장), 모든 강의를 한 번에 보는 Obsidian Bases 표가 됩니다. 읽기 전용 마감 게이트가 빠진 단계를 잡습니다. 옵시디언 기본 기능만 씁니다.

| 스킬 | 사용 |
|-------|-------|
| `lecture-asset` | 전사본과 함께 "강의 자산화해줘"라고 말합니다 |

가상의 [샘플 볼트](plugins/lecture-asset/examples/sample-vault/)가 들어 있습니다. 자세한 내용: [plugins/lecture-asset](plugins/lecture-asset/README.ko.md)

---

### research-pipeline

CMDS Process(Connect - Merge - Develop - Share)를 따르는 연구-출판 파이프라인입니다. 문헌 탐색부터 학술지 투고까지 전문 서브 에이전트 5개가 나눠 맡습니다.

| 단계 | 에이전트 | 모델 | 역할 |
|-------|-------|-------|------|
| 1. Connect | literature-scout | haiku | PubMed/Scholar/Pinecone 문헌 검색 |
| 2. Merge | literature-analyst | sonnet | 논문 분석, 합성 매트릭스, 문헌 리뷰 |
| 3. Develop | manuscript-architect | opus | 원고 구조 설계와 초안 |
| 4. Edit | manuscript-editor | sonnet | 5단계 검토와 수정 |
| 5. Share | publication-formatter | sonnet | 학술지별 서식과 투고 준비 |

**포함 스킬:**

| 스킬 | 용도 |
|-------|-------|
| `/research-pipeline` | 메인 오케스트레이터 (5단계 전체) |
| `/lit-search` | 문헌 검색만 |
| `/lit-review` | 문헌 리뷰만 |
| `/citation-manager` | 인용 서식과 점검 |
| `/journal-formatter` | 학술지별 투고 서식 |

**MCP 연동:** PubMed, Firecrawl, Pinecone

---

### dev-orchestrator

3계층(Opus/Sonnet/Haiku) 에이전트 시스템으로 움직이는 개발 오케스트레이터입니다. 전문 에이전트 13개와 스킬 12개가 기획, 설계, 구현, 테스트, 리뷰, 문서화를 나눠 맡습니다.

| 계층 | 에이전트 | 모델 | 역할 |
|------|--------|-------|------|
| 1. Brain | planner, architect, critic, security-reviewer | opus | 전략 기획, 설계, 보안 |
| 2. Hand | executor, code-reviewer, designer, researcher, build-fixer | sonnet | 구현, 리뷰, 디자인 |
| 3. Eye | explorer, tdd-guide, qa-tester, writer | haiku | 탐색, 테스트, 문서화 |

**포함 스킬:**

| 분류 | 스킬 |
|----------|--------|
| 실행 모드 | `/autopilot`, `/focus`, `/pipeline` |
| 기획 | `/plan`, `/decompose`, `/estimate` |
| 품질 | `/code-review`, `/security-review`, `/tdd` |
| 탐색 | `/deepsearch`, `/deepinit`, `/hud` |

## 설치

```bash
# 마켓플레이스 추가
/plugin marketplace add johnfkoo951/cmdspace-plugins

# 플러그인 설치
/plugin install lecture-asset@cmdspace-plugins
/plugin install research-pipeline@cmdspace-plugins
/plugin install dev-orchestrator@cmdspace-plugins
```

Claude Code 2.1.275 이상에서는 플러그인마다 한 줄로도 됩니다: `/plugin install lecture-asset --marketplace johnfkoo951/cmdspace-plugins`

## 변경 이력

[CHANGELOG.md](CHANGELOG.md)를 보세요.

## 만든 사람

Yohan Koo (CMDSPACE) · <https://cmdspace.work>

## 라이선스

MIT
