---
name: lit-search
description: "학술 문헌 검색을 수행합니다. PubMed, Google Scholar, 볼트 내부 Pinecone 벡터 검색을 사용해 관련 논문을 체계적으로 탐색합니다. '문헌 검색해줘', '논문 찾아줘', '선행연구 조사', 'literature search', 'find papers on', '관련 논문 탐색' 등의 요청 시 사용하세요."
---

# Literature Search (독립 스킬)

연구 파이프라인의 Phase 1을 독립적으로 실행하는 스킬입니다.
전체 파이프라인(`/research`) 없이도 단독으로 문헌 검색을 수행할 수 있습니다.

## 워크플로우

### 1. 사용자 입력 확인

`AskUserQuestion`으로 검색 옵션을 확인한다:

```json
{
  "questions": [
    {
      "header": "검색 범위",
      "question": "어디에서 검색할까요?",
      "options": [
        {"label": "전체 (Recommended)", "description": "PubMed + Google Scholar + 볼트 내부 모두 검색"},
        {"label": "PubMed만", "description": "의학/생명과학/사회과학 학술 DB"},
        {"label": "웹 검색만", "description": "Google Scholar, ERIC, SSRN 등"},
        {"label": "볼트만", "description": "기존 볼트 내 노트에서만 검색"}
      ],
      "multiSelect": false
    },
    {
      "header": "출력 위치",
      "question": "결과를 어디에 저장할까요?",
      "options": [
        {"label": "AI Agent 폴더 (Recommended)", "description": "03-1. Claude Code (MBP)/ 에 저장"},
        {"label": "현재 대화만", "description": "파일 생성 없이 대화에서만 결과 표시"}
      ],
      "multiSelect": false
    }
  ]
}
```

### 2. 서브에이전트 디스패치

`Task` 도구로 `literature-scout` 에이전트를 디스패치한다.

프롬프트에 포함할 정보:
- 사용자가 제공한 연구 주제/키워드
- 검색 범위 선택 결과
- 출력 위치
- Zotero 레퍼런스 경로: `80. References/84. References (Zotero)/`
- Literature Notes 경로: `20. Literature Notes/`

### 3. 결과 보고

에이전트 완료 후:
- 검색 결과 요약 (총 논문 수, A/B/C-tier 비율)
- 주요 연구 갭 요약
- 파일 저장 경로 안내

### 4. 추가 검색 제안

검색 결과가 부족하면:
- 키워드 확장 제안
- 추가 데이터베이스 제안
- 시간 범위 조정 제안
