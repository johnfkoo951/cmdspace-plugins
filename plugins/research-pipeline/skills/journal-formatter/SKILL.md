---
name: journal-formatter
description: "학술지별 투고 규정에 맞춰 원고를 포맷합니다. 학술지 가이드라인을 자동으로 스크래핑하고, 원고 구조/인용 스타일/워드 카운트를 조정합니다. '학술지 포맷 맞춰줘', 'journal formatting', '투고 준비해줘', 'format for [journal name]', '학회 포맷으로 변환', '제출 준비' 등의 요청 시 사용하세요."
---

# Journal Formatter (독립 스킬)

원고를 특정 학술지/학회의 투고 규정에 맞춰 포맷팅하는 독립 스킬입니다.

## 워크플로우

### 1. 입력 확인

필요한 입력:
- 원고 파일 경로 (필수)
- 대상 학술지/학회명 (필수)

### 2. 학술지 가이드라인 수집

**A. 자동 스크래핑**:
1. `WebSearch`로 "[Journal Name] author guidelines instructions for authors" 검색
2. 검색 결과에서 공식 가이드라인 URL 식별
3. `mcp__firecrawl-mcp__firecrawl_scrape`로 가이드라인 페이지 스크래핑
4. 핵심 정보 추출:
   - Word/page limit
   - Required sections
   - Citation style
   - Abstract requirements (word limit, structured/unstructured)
   - Keyword requirements
   - Table/figure policies
   - Blind review requirements
   - File format requirements

**B. 사전 구성된 학술지** (빠른 적용):
- APA 7th 기반 학술지 (대부분의 사회과학/교육학 저널)
  - 참조: `references/apa7-guide.md`

### 3. 사용자 확인

`AskUserQuestion`으로 확인:

```json
{
  "questions": [
    {
      "header": "포맷 범위",
      "question": "어떤 작업을 수행할까요?",
      "options": [
        {"label": "전체 패키지 (Recommended)", "description": "원고 포맷 + 커버레터 + 초록 + 체크리스트"},
        {"label": "원고만", "description": "원고 포맷팅만 수행"},
        {"label": "커버레터만", "description": "커버레터만 작성"},
        {"label": "체크리스트만", "description": "제출 체크리스트만 생성"}
      ],
      "multiSelect": false
    }
  ]
}
```

### 4. 서브에이전트 디스패치

`Task` 도구로 `publication-formatter` 에이전트를 디스패치한다.

프롬프트에 포함할 정보:
- 원고 파일 내용
- 학술지명 및 스크래핑된 가이드라인
- 포맷 범위 선택
- 인용 스타일
- 출력 경로

### 5. 결과 보고

에이전트 완료 후:
- 포맷 적용 요약 (변경 사항)
- 분량 확인 (현재/제한)
- 미해결 항목 (있으면)
- 생성된 파일 목록

### 6. CMDS 볼트 연동

최종 제출 파일을 볼트에 연결:
- `[[📚 821 Academic Journals]]` 또는 `[[📚 822 Conference Presentations]]`에 링크 추가
- `70. Outputs/71. Published/`에 최종본 복사 (수락 후)

## 지원 학술지 목록 (확장 가능)

### 교육학/HRD
- Human Resource Development Quarterly (HRDQ)
- Human Resource Development Review (HRDR)
- Educational Technology Research and Development (ETR&D)
- Performance Improvement Quarterly (PIQ)
- 한국인력개발학회지 (KAHRD Journal)

### 지식관리/AI
- Journal of Knowledge Management (JKM)
- Knowledge Management Research & Practice (KMRP)
- Computers & Education
- International Journal of Artificial Intelligence in Education

### 기타
- 사용자가 학술지명을 제공하면 가이드라인을 실시간 스크래핑하여 적용
