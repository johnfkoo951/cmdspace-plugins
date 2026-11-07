# Eagle 라이브러리 정리 규칙 (예시 템플릿)

> 이 파일은 **예시**다. 자기 라이브러리에 맞게 고쳐 `taxonomy.md` 로 저장하거나, 볼트의 에이전트 설정 파일(`CLAUDE.md` 등)에 경로를 적어 둔다. 에이전트는 가져오기 전에 이 규칙과 라이브러리의 기존 항목을 먼저 읽고, 새 규칙을 발명하지 않는다.

## 라이브러리 역할 지도 (어디에 넣을지 먼저 정한다)

| 별칭 | 라이브러리 | 넣는 것 |
|---|---|---|
| `personal` (기본) | `~/Eagle/Personal.library` | 공유가 필요 없는 개인 노트에 연결된 이미지, 테스트·플러그인 생성물 |
| `design` (공유) | `~/Shared/Team Design.library` | 팀이 함께 쓰는 에셋: 캐릭터, 로고, 교육·홍보 이미지, 레퍼런스 |
| `photo` (공유) | `~/Shared/Team Photo.library` | 행사·프로그램 사진 (연도 → 행사) |

- 판단 기준 예: 개인 일상·데일리·테스트 = `personal` / 발행·강의·브랜드·행사·고객·공유 에셋 = `design`.
- 별칭은 설정 파일(`~/.config/eagle-library/config.json`)의 `libraries` 와 같아야 스크립트에서 쓸 수 있다.

## 폴더 트리 (personal 예시)
```
00. Inbox                         미분류 수집 (자동 생성물 기본 목적지)
10. Obsidian                      볼트 노트에 연결된 이미지 (file:/// 원본 링크 — 이름 변경 금지)
  11. Research                    리서치 노트
  12. Meetings                    회의 노트
  13. Daily                       데일리 노트
  19. Unlinked                    어떤 노트도 참조하지 않는 생성물·캡처 (정리 후보)
20. Assets                        시각 자산
  21. Icons                       아이콘
  22. Characters
    01 Mascot                     마스코트
  23. Props                       단독 소품 스티커
  24. Scenes                      장면 일러스트
```
새 범주는 `20. Assets` 아래 다음 번호로, 하위는 `01 이름` 형식.

## 이름
⚠ 노트에 연결된 항목(`10. Obsidian` 계열)은 이름을 바꾸지 않는다 — Eagle 에서 이름을 바꾸면 실제 파일명이 바뀌어 노트의 `file:///` 링크가 깨진다.
그 외 새로 넣는 항목은 영문 kebab-case 슬러그. 한글 설명은 태그·주석에.
- 캐릭터: `{character}-{pose}` (예: `mascot-wave`)
- 장면: `scene-{name}` (예: `scene-lecture-hall`)
- 소품: `prop-{name}` · 아이콘: `{target}-icon-v{n}`

## 태그 (영문 = 유형·시스템, 한글/고유명 = 대상·장면)

| 역할 | 태그 |
|------|------|
| 유형 | `character` · `icon` · `avatar` · `scene` · `prop` · `draft` |
| 대상 | 캐릭터 이름, 인물 이름 |
| 장면·소품 | 한 단어 (`강의`, `lecture`, `compass` …) |
| 생성 모델 | 정확한 모델 ID (예: `gpt-…`, `gemini-…`) |
| 형식 | `transparent` (알파 배경일 때만) · 종횡비 `16:9` 등 필요 시 |
| 연결 상태 | `obsidian-linked` / `obsidian-unlinked` |

## 주석 (annotation)
```
{출처 도구} {생성일} · gen: {모델} · {추가 정보}
prompt: {생성에 쓴 프롬프트 전문}
```
- 생성 이미지는 마지막 줄에 프롬프트 전문을 남긴다. 볼트를 볼 수 없는 팀원도 Eagle 주석만으로 무엇을 그렸고 어떻게 다시 만드는지 알 수 있어야 한다.
- 업스케일 등 같은 그림의 큰 판은 이름 뒤에 `-hd`, 태그 `hd`·`upscaled`, 주석에 원본 ID. 에셋 노트는 원본 것을 함께 쓴다 (`variantSuffixes`).

## URL
노트에 연결된 항목은 `url` = `obsidian://open?vault=<볼트 이름>&file=<URL 인코딩된 노트 경로, .md 없이>` (Eagle 에서 클릭하면 노트로 이동).

## 별점
사용자가 직접 매긴 별점은 교체 시에도 유지한다 (manifest `star`). 에이전트가 임의로 새 별점을 매기지 않는다.

## 음악·오디오 라이브러리 (선택)
- 폴더는 용도별 (예: `01. Narration Bed` · `02. Demo Groove` · `03. Shorts & Promo` · `04. Intro` · `05. Stings`).
- 이름: `코드 · 곡 이름 — 테이크 A (3′49″)` (`/`·`:` 는 파일명에 쓰지 않는다).
- 태그: 장르, `NN BPM`, 키, `용도:…`. 별점: 5 = 실제로 쓴 곡. url = 생성 서비스의 곡 페이지.
- 동기화 라이브러리에는 MP3 를 권장한다 (WAV 는 크기가 수 배).
