# Dev Orchestrator

3-Tier 에이전트 시스템(Opus/Sonnet/Haiku) 기반 자율형 개발 오케스트레이터 플러그인.

SDLC(Software Development Life Cycle) 전 과정 — 기획, 설계, 구현, 테스트, 리뷰, 문서화 — 을 13개 전문 에이전트와 12개 스킬로 지원합니다.

## 구성 요소

### 에이전트 (13개)

| Tier | Agent | Model | Role |
|------|-------|-------|------|
| 1. Brain | planner | opus | Master orchestrator — 작업 분해, 에이전트 할당, 실행 계획 |
| 1. Brain | architect | opus | 시스템/코드 아키텍처 설계, 기술 결정 |
| 1. Brain | critic | opus | Devil's advocate — 논리적 결함, 숨은 가정, 리스크 발견 |
| 1. Brain | security-reviewer | opus | OWASP Top 10 기반 보안 취약점 분석 |
| 2. Hand | executor | sonnet | 코드 구현 — 비즈니스 로직, API, 컴포넌트 |
| 2. Hand | code-reviewer | sonnet | 코드 품질 리뷰 — 가독성, 유지보수성, 성능 |
| 2. Hand | designer | sonnet | UI/UX 컴포넌트 설계, 접근성, 디자인 시스템 |
| 2. Hand | researcher | sonnet | 기술 리서치 — 라이브러리 평가, 베스트 프랙티스 |
| 2. Hand | build-fixer | sonnet | 빌드 에러 진단 및 자동 수정 |
| 3. Eye | explorer | haiku | 코드베이스 탐색, 파일 검색, 의존성 매핑 |
| 3. Eye | tdd-guide | haiku | 테스트 주도 개발 — Red-Green-Refactor 사이클 |
| 3. Eye | qa-tester | haiku | QA 테스트 — E2E, 통합, 엣지 케이스 |
| 3. Eye | writer | haiku | 문서 작성 — README, API 문서, 아키텍처 가이드 |

### 스킬 (12개)

| Category | Skill | Usage |
|----------|-------|-------|
| 실행 모드 | `/autopilot` | 완전 자율 실행 (Plan → Implement → Test → Review) |
| 실행 모드 | `/focus` | 단일 Opus 에이전트 집중 모드 |
| 실행 모드 | `/pipeline` | 순차적 에이전트 체이닝 |
| 기획 | `/plan` | 구현 계획 수립 |
| 기획 | `/decompose` | 복잡한 작업을 서브태스크로 분해 |
| 기획 | `/estimate` | 복잡도 및 리소스 추정 |
| 품질 | `/code-review` | 심층 코드 품질 리뷰 |
| 품질 | `/security-review` | OWASP 기반 보안 감사 |
| 품질 | `/tdd` | 테스트 주도 개발 워크플로우 |
| 탐색 | `/deepsearch` | 다중 전략 코드 검색 |
| 탐색 | `/deepinit` | 프로젝트 문서 자동 생성 |
| 유틸리티 | `/hud` | 세션 상태 대시보드 |

## 3-Tier 전략

```
복잡도 1-3  → Haiku  (Eye/Foot) : 검색, 문서화, 보일러플레이트
복잡도 4-6  → Sonnet (Hand)     : 구현, 리뷰, 디자인
복잡도 7-10 → Opus   (Brain)    : 설계, 보안, 핵심 결정
```

에스컬레이션: Haiku 2회 실패 → Sonnet, Sonnet 2회 실패 → Opus

## 사용법

```bash
# 자율 모드로 기능 구현
/autopilot

# 구현 계획 수립
/plan

# 코드 리뷰
/code-review

# 보안 감사
/security-review

# 프로젝트 상태 확인
/hud
```

## MCP 연동

이 플러그인은 Claude Code 내장 도구(Bash, Read, Edit, Grep, Glob, WebSearch 등)를 활용합니다.
추가 MCP 서버 연동 시 별도 설치가 필요합니다:

| MCP Server | Purpose | Status |
|------------|---------|--------|
| Context7 | Library documentation lookup | Optional |
| Playwright | E2E browser testing | Optional |
| Chrome DevTools | Browser debugging | Optional |

## 설계 원칙

| 원칙 | 설명 |
|------|------|
| Tier 최적화 | Opus(고지능)과 Haiku(고속)를 역할별로 동적 배분 |
| 최소 변경 | 요청된 것만 변경, 불필요한 리팩토링 없음 |
| 실패 복구 | 자동 에스컬레이션, 롤백 전략 포함 |
| 비용 의식 | 기본 Haiku → 필요 시 Sonnet → 최후 Opus |
