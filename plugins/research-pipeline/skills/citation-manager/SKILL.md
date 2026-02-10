---
name: citation-manager
description: "인용 관리 및 서지 정보를 처리합니다. APA 7th, Chicago, IEEE 등의 인용 스타일로 포맷하고, Zotero 레퍼런스와 동기화하며, 인용 정확성을 검증합니다. '인용 포맷해줘', '참고문헌 정리', 'format citations', 'APA 스타일로 변환', '서지 검증', 'citation check', '레퍼런스 정리' 등의 요청 시 사용하세요."
---

# Citation Manager (독립 스킬)

원고의 인용과 참고문헌을 관리하는 독립 스킬입니다.

## 기능

1. **인용 포맷 변환**: 인라인 인용 + 참고문헌 목록을 지정 스타일로 변환
2. **인용 감사 (Audit)**: 본문 인용과 참고문헌 목록의 일치 여부 검증
3. **DOI 검증**: DOI 링크 존재 확인 (Firecrawl 스크래핑)
4. **Zotero 교차 검증**: 볼트의 Zotero 레퍼런스와 대조

## 워크플로우

### 1. 입력 확인

사용자가 제공하는 입력:
- 원고 파일 경로 (필수)
- 인용 스타일 (기본: APA 7th)

### 2. 옵션 확인

`AskUserQuestion`으로 확인:

```json
{
  "questions": [
    {
      "header": "인용 스타일",
      "question": "어떤 인용 스타일을 적용할까요?",
      "options": [
        {"label": "APA 7th (Recommended)", "description": "사회과학 표준. (Author, Year) 형식"},
        {"label": "Chicago 17th", "description": "인문학. 각주 + 참고문헌"},
        {"label": "IEEE", "description": "공학/CS. [1] 번호 형식"},
        {"label": "기타", "description": "직접 스타일 지정"}
      ],
      "multiSelect": false
    },
    {
      "header": "작업 범위",
      "question": "어떤 작업을 수행할까요?",
      "options": [
        {"label": "전체 (Recommended)", "description": "포맷 변환 + 감사 + DOI 검증"},
        {"label": "감사만", "description": "인용-참고문헌 일치 여부만 검증"},
        {"label": "포맷만", "description": "인용 스타일 변환만 수행"}
      ],
      "multiSelect": false
    }
  ]
}
```

### 3. 인용 감사 (Citation Audit)

원고 파일을 읽어:

**A. 본문 인용 추출**:
- 패턴: `(Author, Year)`, `Author (Year)`, `(Author1 & Author2, Year)`, `(Author et al., Year)`
- 모든 인라인 인용을 목록으로 수집

**B. 참고문헌 목록 추출**:
- References 섹션에서 모든 항목 파싱
- Author, Year, Title, Journal, DOI 추출

**C. 교차 검증**:
| 상태 | 설명 |
|------|------|
| OK | 본문에 인용되고 참고문헌에도 있음 |
| Missing Reference | 본문에 인용되었으나 참고문헌 누락 |
| Orphaned Reference | 참고문헌에 있으나 본문에 인용 안 됨 |
| Year Mismatch | 본문과 참고문헌의 연도 불일치 |
| Author Mismatch | 본문과 참고문헌의 저자명 불일치 |

**D. Zotero 교차 검증**:
- `80. References/84. References (Zotero)/` 디렉토리 스캔
- `@citekey.md` 파일과 매칭
- 볼트에 있는 레퍼런스는 "Verified" 표시

### 4. DOI 검증 (선택)

각 DOI에 대해:
1. `mcp__firecrawl-mcp__firecrawl_scrape` 으로 `https://doi.org/{DOI}` 접근
2. 응답 확인 → 존재하면 "Valid", 404면 "Invalid"
3. Invalid DOI는 `[INVALID DOI]` 플래그

### 5. 포맷 변환

**APA 7th 포맷 규칙** (참조: `references/apa7-guide.md`):

본문 인용:
- 1-2 저자: (Kim & Lee, 2024)
- 3+ 저자: (Kim et al., 2024)
- 직접 인용: (Kim, 2024, p. 15)

참고문헌:
- 저자. (연도). 제목. *학술지명*, *권*(호), 페이지. https://doi.org/xxx

### 6. 결과 출력

감사 결과 테이블:

```markdown
## Citation Audit Report

### Summary
- Total in-text citations: {n}
- Total references: {n}
- OK: {n}
- Missing references: {n}
- Orphaned references: {n}
- DOI valid: {n} / DOI invalid: {n}
- Zotero verified: {n}

### Issues
| # | Type | Citation | Details | Action Required |
|---|------|----------|---------|----------------|
| 1 | Missing Reference | (Kim, 2024) | Not in reference list | Add reference |
```

## 중요 규칙

1. **절대 인용을 창작하지 않는다**: 존재 확인 불가능한 인용은 `[VERIFY]` 태그
2. **APA 7th가 기본**: 다른 스타일은 명시적 요청 시에만
3. **Zotero 우선**: 볼트의 Zotero 노트 정보가 가장 신뢰도 높음
