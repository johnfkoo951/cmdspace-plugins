---
name: lit-review
description: "문헌 분석 및 문헌 리뷰를 작성합니다. 논문 목록이나 검색 결과를 받아 주제별 합성 매트릭스를 구축하고 체계적인 문헌 리뷰를 작성합니다. '문헌 리뷰 써줘', '선행연구 분석', '논문 합성해줘', 'synthesize papers', 'literature review', '논문 정리해줘' 등의 요청 시 사용하세요."
---

# Literature Review (독립 스킬)

연구 파이프라인의 Phase 2를 독립적으로 실행하는 스킬입니다.
검색 결과 파일이나 논문 목록을 받아 합성 매트릭스와 문헌 리뷰를 작성합니다.

## 워크플로우

### 1. 입력 자료 확인

사용자가 제공하는 입력 형태:
- **파일 경로**: `01-search-results.md` 또는 논문 목록 파일
- **논문 목록**: 대화에서 직접 제공한 논문 제목/DOI 목록
- **주제**: 주제만 제공 시 먼저 `/lit-search`를 제안

### 2. 사용자 옵션 확인

`AskUserQuestion`으로 확인:

```json
{
  "questions": [
    {
      "header": "분석 깊이",
      "question": "어떤 수준의 문헌 리뷰를 원하시나요?",
      "options": [
        {"label": "전체 리뷰 (Recommended)", "description": "합성 매트릭스 + 주제별 리뷰 + 갭 분석 + 이론 프레임워크"},
        {"label": "합성 매트릭스만", "description": "논문 비교표만 생성"},
        {"label": "요약 정리", "description": "각 논문 요약 + 간단한 비교"}
      ],
      "multiSelect": false
    },
    {
      "header": "문헌 노트",
      "question": "개별 논문 노트도 생성할까요?",
      "options": [
        {"label": "생성 (Recommended)", "description": "20. Literature Notes/21./ 에 @citekey.md 노트 생성"},
        {"label": "생성 안함", "description": "합성 매트릭스와 리뷰만 생성"}
      ],
      "multiSelect": false
    }
  ]
}
```

### 3. 서브에이전트 디스패치

`Task` 도구로 `literature-analyst` 에이전트를 디스패치한다.

프롬프트에 포함할 정보:
- 논문 목록 또는 검색 결과 파일 내용
- 연구 주제와 핵심 질문
- 분석 깊이 선택
- 문헌 노트 생성 여부
- 출력 경로

### 4. 결과 보고

에이전트 완료 후:
- 합성 매트릭스 요약 (분석한 논문 수, 주제 클러스터)
- 주요 연구 갭 요약
- 이론 프레임워크 제안 요약
- 생성된 파일 목록 안내
