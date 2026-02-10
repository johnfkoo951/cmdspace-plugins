---
name: research-pipeline
description: "연구-출판 파이프라인을 실행합니다. 연구 주제를 받아 자료 조사, 문헌 분석, 원고 작성, 편집, 출판 포맷팅까지 5단계를 관리합니다. '연구 시작해줘', '논문 써줘', '학회 발표 준비', 'research pipeline', '연구 파이프라인 시작', '문헌 조사부터 시작해줘', '자료 조사에서 출판까지' 등의 요청 시 사용하세요."
---

# Research-to-Publication Pipeline

CMDS Process(Connect - Merge - Develop - Share) 기반 연구-출판 파이프라인 오케스트레이터입니다.

## 워크플로우 개요

```
Phase 1: Connect (자료 조사) → Phase 2: Merge (문헌 분석) → Phase 3: Develop (원고 집필) → Phase 4: Edit (편집) → Phase 5: Share (출판)
```

---

## Phase 0: 프로젝트 초기화

### 0-1. 사용자 옵션 확인

반드시 `AskUserQuestion` 도구를 사용하여 아래 질문들을 제시한다:

```json
{
  "questions": [
    {
      "header": "출력 유형",
      "question": "어떤 형태의 출력물을 만들까요?",
      "options": [
        {"label": "학술 논문 (Recommended)", "description": "IMRaD 구조의 학술지 투고용 논문"},
        {"label": "학회 발표", "description": "Conference paper + 발표 슬라이드 구조"},
        {"label": "뉴스레터", "description": "더배러 스타일 에세이"},
        {"label": "강의 자료", "description": "대학 강의용 교안"}
      ],
      "multiSelect": false
    },
    {
      "header": "언어",
      "question": "어떤 언어로 작성할까요?",
      "options": [
        {"label": "한국어 (Recommended)", "description": "국내 학술지 투고용. 영문 초록 포함"},
        {"label": "영어", "description": "국제 학술지/학회 투고용"},
        {"label": "이중 언어", "description": "한국어 본문 + 영어 전체 번역본"}
      ],
      "multiSelect": false
    },
    {
      "header": "시작 Phase",
      "question": "어디서부터 시작할까요?",
      "options": [
        {"label": "Phase 1부터 (Recommended)", "description": "자료 조사부터 전체 파이프라인 실행"},
        {"label": "Phase 2부터", "description": "이미 논문 목록이 있어서 분석부터 시작"},
        {"label": "Phase 3부터", "description": "문헌 리뷰 완료, 원고 작성부터"},
        {"label": "기존 프로젝트 재개", "description": "_pipeline-state.md가 있는 프로젝트 이어하기"}
      ],
      "multiSelect": false
    }
  ]
}
```

### 0-2. 프로젝트 폴더 생성

- 위치: `00. Inbox/03. AI Agent/03-1. Claude Code (MBP)/YYYY-MM-DD-research-{slug}/`
- `{slug}`는 연구 주제에서 생성 (예: `knowledge-sharing-ai`)

### 0-3. 파이프라인 상태 파일 생성

`references/pipeline-state-template.md` 템플릿을 사용하여 `_pipeline-state.md` 생성.
사용자 응답을 반영하여 `target_output`, `language`, `current_phase` 등 설정.

### 0-4. 기존 프로젝트 재개 시

프로젝트 폴더에서 `_pipeline-state.md`를 읽어:
- `current_phase` 확인
- `phases_completed` 확인
- 마지막 완료 Phase 다음부터 재개

---

## Phase 1: Connect (자료 조사)

### 서브에이전트 디스패치

`Task` 도구로 `literature-scout` 에이전트를 디스패치한다.

프롬프트에 반드시 포함할 정보:
- 연구 주제 및 키워드
- 프로젝트 폴더 경로
- 대상 학문 분야
- 기존 Zotero 레퍼런스 경로: `80. References/84. References (Zotero)/`
- 볼트 Literature Notes 경로: `20. Literature Notes/`

### Quality Gate 1 (QG1)

에이전트 완료 후 `01-search-results.md`를 읽어 검증:

| 항목 | 기준 |
|------|------|
| 논문 수 | 관련 논문 10건 이상 |
| 데이터베이스 | 최소 2개 소스 (PubMed + Scholar 등) |
| 최신성 | 최근 3년 이내 논문 2건 이상 |
| 검색 전략 | 쿼리와 데이터베이스 문서화 완료 |

- PASS: `_pipeline-state.md` 업데이트, Phase 2로 진행
- FAIL: 사용자에게 결과 보고, 키워드 확장 또는 추가 검색 제안

---

## Phase 2: Merge (문헌 분석)

### 서브에이전트 디스패치

`Task` 도구로 `literature-analyst` 에이전트를 디스패치한다.

프롬프트에 반드시 포함할 정보:
- `01-search-results.md` 내용 (또는 경로)
- 연구 주제와 핵심 질문
- 기존 문헌 노트 경로: `20. Literature Notes/21. Lit Notes (Zotero)/`
- 프로젝트 폴더 경로
- A-tier 논문 목록 (검색 결과에서 추출)

### Quality Gate 2 (QG2)

| 항목 | 기준 |
|------|------|
| 합성 매트릭스 | A-tier 논문 전부 포함 |
| 주제 클러스터 | 최소 3개 주제 그룹 식별 |
| 연구 갭 | 명시적 갭 진술 포함 |
| 이론 프레임워크 | 프레임워크 제안 + 근거 인용 |
| 인용 형식 | 본문 내 괄호형 인용 사용 |

- PASS: Phase 3 진행
- FAIL: 분석 보완 지시 후 재실행

### 사용자 확인 포인트

Phase 2 완료 후 `AskUserQuestion`으로 확인:
- 이론적 프레임워크 선택 동의 여부
- 연구 방향/질문 수정 필요 여부
- 추가 문헌 필요 여부

---

## Phase 3: Develop (원고 집필)

### 서브에이전트 디스패치

`Task` 도구로 `manuscript-architect` 에이전트를 디스패치한다.

프롬프트에 반드시 포함할 정보:
- `02-synthesis-matrix.md` 내용
- `03-literature-review.md` 내용
- 출력 유형 (학술 논문/학회 발표/뉴스레터/강의 자료)
- 대상 학술지/학회명 (해당 시)
- 언어 설정
- 프로젝트 폴더 경로

### 출력 유형별 구조

**학술 논문 (IMRaD)**:
```
04-manuscript-outline.md
05-draft-introduction.md
05-draft-literature-review.md
05-draft-methodology.md
05-draft-results.md (데이터 분석 계획)
05-draft-discussion.md
05-draft-conclusion.md
06-manuscript-draft.md (통합본)
```

**학회 발표**:
```
04-manuscript-outline.md
06-manuscript-draft.md (축약 논문)
06-presentation-outline.md (슬라이드 구성)
```

**뉴스레터**:
```
04-manuscript-outline.md
06-manuscript-draft.md (에세이)
```

### Quality Gate 3 (QG3)

| 항목 | 기준 |
|------|------|
| 섹션 완성도 | 모든 계획 섹션 작성 완료 (placeholder 불가) |
| 분량 | 목표 분량 ±20% |
| 인용 통합 | 서론·토론 내 모든 주장에 인용 근거 |
| 방법론 | 연구 설계, 표본, 측정도구, 분석 방법 포함 |

---

## Phase 4: Edit (편집)

### 서브에이전트 디스패치

`Task` 도구로 `manuscript-editor` 에이전트를 디스패치한다.

프롬프트에 반드시 포함할 정보:
- `06-manuscript-draft.md` 내용
- 출력 유형
- 대상 학술지 (해당 시)
- 문헌 노트 경로 (인용 검증용)
- 프로젝트 폴더 경로

### Quality Gate 4 (QG4)

| 항목 | 기준 |
|------|------|
| 치명적 이슈 | 0건 |
| 주요 이슈 | 모두 해결 또는 명시적 보류 사유 |
| 인용 형식 | 전체 일관 (APA 7th 등) |
| 미인용 참고문헌 | 0건 |
| 미참조 인용 | 0건 |

---

## Phase 5: Share (출판)

### 서브에이전트 디스패치

`Task` 도구로 `publication-formatter` 에이전트를 디스패치한다.

프롬프트에 반드시 포함할 정보:
- `08-manuscript-revised.md` 내용
- 출력 유형
- 대상 학술지/학회명
- 인용 스타일 (APA 7th 기본)
- 프로젝트 폴더 경로

### Quality Gate 5 (QG5)

| 항목 | 기준 |
|------|------|
| 분량 제한 | 학술지 워드 리밋 충족 |
| 필수 섹션 | 학술지 요구 섹션 전부 포함 |
| 초록 | 워드 리밋 내, 키워드 포함 |
| 커버레터 | 범위와 기여도 명시 |
| 체크리스트 | 제출 항목 100% 완료 |

---

## CMDS 볼트 연동

### YAML Frontmatter 규칙 (모든 생성 파일 공통)

```yaml
---
type: research-pipeline    # 파이프라인 생성 파일
aliases: []
author:
  - "[[구요한]]"
date created: YYYY-MM-DD
date modified: YYYY-MM-DD
tags:
  - research-pipeline
  - {연구주제 태그}
CMDS: "[[📚 820 Research]]"
index: "[[🏷 Research Notes]]"
status: inProgress
---
```

**중요**: YAML frontmatter는 2 spaces 들여쓰기, wikilinks는 반드시 따옴표로 감싸기.

### CMDS 카테고리 연결

| Phase | CMDS 카테고리 |
|-------|-------------|
| Phase 1 | `[[📖 100 Themes]]` - 연구 주제 발굴 |
| Phase 2 | `[[📖 200 Literature]]` - 문헌 통합 |
| Phase 3 | `[[📖 400 Methodologies]]` - 방법론 적용 |
| Phase 4 | `[[📖 600 Specialties]]` - 전문 지식 |
| Phase 5 | `[[📖 800 Outputs]]` - 최종 산출물 |

---

## 에러 처리

### 논문 전문 접근 실패
PubMed OA → Firecrawl preprint 서버 → 초록만으로 분석 fallback.
접근 불가 논문은 `01-search-results.md`에 플래그 표시.

### 세션 중단 시
`_pipeline-state.md`의 `current_phase`와 `phases_completed`로 재개점 결정.
"기존 프로젝트 재개" 옵션으로 이어서 진행.

### 인용 환각 방지
1. Zotero 노트(`80. References/84. References (Zotero)/`)와 교차 검증
2. DOI 스크래핑으로 존재 확인
3. 미검증 인용은 `[VERIFY]` 태그 추가
