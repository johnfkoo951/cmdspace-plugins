# Research-to-Publication Pipeline

CMDS Process(Connect - Merge - Develop - Share) 기반 연구-출판 파이프라인 플러그인.

## 구성 요소

### 에이전트 (5개)
| 에이전트 | Phase | 모델 | 역할 |
|---------|-------|------|------|
| literature-scout | 1. Connect | haiku | PubMed/Scholar/Pinecone 문헌 검색 |
| literature-analyst | 2. Merge | sonnet | 논문 분석, 합성 매트릭스, 문헌 리뷰 |
| manuscript-architect | 3. Develop | opus | 원고 구조 설계 및 초안 작성 |
| manuscript-editor | 4. Edit | sonnet | 5-pass 리뷰 및 수정 |
| publication-formatter | 5. Share | sonnet | 학술지별 포맷팅, 투고 준비 |

### 스킬 (5개)
| 스킬 | 용도 |
|------|------|
| research-pipeline | 메인 오케스트레이터 (5-Phase 전체 관리) |
| lit-search | 독립 문헌 검색 |
| lit-review | 독립 문헌 리뷰 |
| citation-manager | 인용 포맷팅 및 검증 |
| journal-formatter | 학술지별 투고 포맷팅 |

## 사용법

```
/research [연구 주제]          # 전체 파이프라인 시작
/lit-search [키워드]           # 문헌 검색만
/lit-review [파일 경로]        # 문헌 리뷰만
/cite [원고 경로]              # 인용 포맷팅
/journal-format [원고 경로]    # 학술지 포맷 변환
```

## 출력 위치

프로젝트 폴더: `00. Inbox/03. AI Agent/03-1. Claude Code (MBP)/YYYY-MM-DD-research-{slug}/`

## MCP 연동
- PubMed: 논문 검색, 메타데이터, 전문 접근
- Firecrawl: Google Scholar 검색, DOI 스크래핑, 학술지 가이드라인
- Pinecone: 볼트 내 시맨틱 검색
