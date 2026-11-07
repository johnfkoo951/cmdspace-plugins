---
name: eagle-library
description: "Import, organize, transfer, and export files in Eagle (eagle.cool) libraries through the Eagle local API, with consistent folders, names, tags, annotations, and ratings, while keeping Obsidian notes that link to Eagle originals intact. Use when the user says '이글에 넣어줘', 'Eagle 라이브러리에 정리', '이미지 이글로', 'Eagle 메타데이터', 'file these images into Eagle', 'organize my Eagle library', 'move these to another Eagle library', or after an image-generation step produces files that should be filed. Also copies Eagle folders into project folders ('이글 에셋 가져와', 'export from Eagle'), checks and repairs Obsidian links to Eagle files, and creates one Obsidian note per Eagle asset for a Bases image gallery. NOT for generating or retouching images."
---

# Eagle Library

생성·수집한 파일을 Eagle 라이브러리에 **폴더·이름·태그·주석·별점까지 정리된 상태로** 넣고, 그 파일을 링크하는 Obsidian 노트가 깨지지 않게 지킨다.
이미지 생성은 다른 도구가 하고, 이 스킬은 그 산출물을 받아 파일링한다.

## 설정 (처음 한 번)
스크립트는 경로를 코드에 박지 않는다. 설정 파일 하나를 만든다 — `~/.config/eagle-library/config.json` (다른 위치면 환경 변수 `EAGLE_LIBRARY_CONFIG`).

```json
{
  "vault": "~/Obsidian/Your Vault",
  "vaultName": "Your Vault",
  "libraries": {
    "personal": "~/Eagle/Personal.library",
    "design": ["~/Shared/Team Design.library", "~/Library/CloudStorage/*/Shared/Team Design.library"]
  },
  "assetNotesRules": "asset-notes-rules.json",
  "taxonomy": "taxonomy.md"
}
```

| 키 | 뜻 |
|---|---|
| `vault` | Obsidian 볼트 루트. 노트 링크 검사·갱신·에셋 노트에 필요 (Eagle 만 쓰면 생략 가능) |
| `vaultName` | `obsidian://open?vault=…` 에 들어가는 볼트 이름 (생략하면 볼트 폴더 이름) |
| `libraries` | 별칭 → `.library` 경로. 스크립트의 `--library`·`--from`·`--to` 에 별칭을 쓴다 |
| `assetNotesRules` | 에셋 노트 규칙 파일 (선택). 예시: `references/asset-notes-rules.example.json` |
| `taxonomy` | **사용자 정리 규칙 문서** (선택). 예시: `references/taxonomy.example.md` |

- 경로 값은 문자열 하나 또는 **후보 목록**이다. 그 기기에 실제로 있는 첫 경로를 쓰고 `*` glob 도 된다 → 설정 파일 하나로 여러 기기를 쓴다. 상대경로는 설정 파일이 있는 폴더 기준.
- 사용자가 경로를 알려 주지 않았으면 `~/` 아래 `*.library` 폴더를 찾아 제안하고 확인받는다. 없는 라이브러리를 만들지 않는다.

## 작업 시작 전 (매번)
1. `python3 scripts/eagle_common.py` 로 해석된 설정을 본다 (✓/✗ 로 볼트·라이브러리·규칙 파일 존재 표시).
2. `taxonomy` 문서가 있으면 **먼저 끝까지 읽는다.** 그 문서의 규칙(어느 라이브러리에 무엇을, 폴더·이름·태그·주석 형식, 사용자 고유 절차)이 이 SKILL.md 의 일반 규칙보다 우선한다.
3. **사용자별 규칙은 이 SKILL.md 나 scripts/ 에 적지 않는다.** 이 폴더는 여러 사람이 함께 쓰는 공개 코드다. 사용자가 새 규칙을 말하면 `taxonomy` 문서(또는 규칙 JSON)에 적고, 코드는 버그 수정·일반 기능일 때만 고친다.

## 전제
- Eagle 앱 실행 중 (로컬 API `http://localhost:41595`, Eagle 4.x 에서 실측).
- 쓰기는 **활성 라이브러리**에만 된다 — 스크립트가 manifest 의 `library` 와 비교해 다르면 중단한다 (`--switch` 로 잠깐 전환 가능).
- `metadata.json` 을 직접 쓰지 않는다. 앱이 실행 중이면 덮어써지므로 쓰기는 항상 API 를 거친다. 읽기 전용 스크립트만 파일을 직접 읽는다.

## 절차 (가져오기)
1. **현황 읽기**: `curl -s localhost:41595/api/folder/list`, 대상 폴더의 `item/list` 로 기존 폴더·태그·주석 형식을 확인한다. 새 규칙을 발명하지 말고 `{taxonomy}` 와 기존 항목에 맞춘다.
2. **manifest 작성** (JSON): 항목마다 `path · folder('/' 경로) · name · tags · annotation · url? · star?`. 교체할 기존 항목은 `trash` 에 id 로. 형식은 `scripts/eagle_import.py` docstring, 예시는 플러그인의 `examples/manifest.example.json`.
3. **dry-run**: `python3 scripts/eagle_import.py manifest.json --dry-run` → 폴더 생성·추가·휴지통 목록을 사용자에게 보인다.
4. **실행**: `--dry-run` 없이. 스크립트는 ① 활성 라이브러리 확인 ② 라이브러리 전체 MD5 로 중복 건너뜀 ③ 교체 대상 먼저 휴지통 ④ 폴더 경로 자동 생성 ⑤ 추가 후 **새 id 생성 검증** ⑥ 별점 적용.
5. **검증**: 폴더별 `item/list` 개수와 이름을 확인하고 결과를 보고한다 (추가·건너뜀·실패·휴지통 수).
6. **노트에 연결된 항목 정리**: 항목 ID 로 볼트를 검색해 연결 노트를 찾는다. 이런 항목은 **폴더 이동만** 하고 이름은 바꾸지 않는다. `url` 이 비어 있으면 `obsidian://open?vault={vaultName}&file=<노트 경로>` 를, 주석이 비어 있으면 `연결 노트: …` 를 채운다. 끝나면 `eagle_linkcheck.py` 를 돌린다.
7. **에셋 노트 (선택)**: 에셋마다 볼트 노트를 두는 경우 `python3 scripts/eagle_asset_notes.py --check` → 노트 없는 에셋이 있으면 `--apply`. 새 Eagle 폴더를 만들었으면 먼저 규칙 파일의 `folders` 에 추가한다 (규칙이 없는 폴더는 대상에서 빠진다; `prefix` 는 문자열 앞부분 일치). 한 개만 미리 보려면 `--preview <Eagle 이름>`. 보고에 `--check` 결과(노트 없음 0)를 넣는다.

## 스크립트 한눈에 (`scripts/`)

| 스크립트 | 하는 일 | 앱 필요 |
|---|---|---|
| `eagle_import.py` | manifest 로 가져오기 (중복 건너뜀·교체 먼저·새 ID 검증·`--map-out`, `--switch` 로 대상 전환 후 원래 라이브러리 복귀) | ✅ |
| `eagle_transfer.py` | **라이브러리 간 이전** 한 번에: 스테이징 → 대상 전환·가져오기 → 노트 링크 갱신 → 옛 ID 검사 → 원본 휴지통 → 처음 라이브러리로 복귀. 실패하면 원본 유지 | ✅ (자동 전환) |
| `eagle_relink.py` | ID 매핑으로 볼트 노트의 `file:///`·`eagle://` 링크 갱신 (미리보기 기본, `--apply` 는 노트 백업) | ❌ |
| `eagle_linkcheck.py` | 볼트의 모든 Eagle 링크 검사, `--ids` 옛 ID 잔존 검사, `--fix-moved` 라이브러리 폴더 이동으로 깨진 링크 복구 | ❌ |
| `eagle_sheet.py` | 폴더·미분류를 번호 붙인 모아보기 시트(PNG) + 목록 JSON (분류 작업용, 📝 = 노트 연결). Pillow 필요 | ❌ |
| `eagle_asset_notes.py` | Eagle 에셋 ↔ 볼트 에셋 노트 점검(`--check`)·생성(`--apply`), 빈 Eagle url 을 노트로 채움. 기존 노트는 덮어쓰지 않음 | ✅ (`--apply` 의 url 기록만) |
| `eagle_export.py` | Eagle 폴더 → 작업 폴더 복사 (정본은 Eagle) | ❌ |
| `eagle_common.py` | 공통: 설정 읽기·API·전환·폴더 트리·볼트 참조·링크 정규식 | |

```bash
S=<이 스킬 폴더>/scripts
python3 $S/eagle_transfer.py --from design --to personal --ids <ID…> --folder "10. Obsidian/13. Daily" --add-tags daily --dry-run
python3 $S/eagle_linkcheck.py                      # 링크를 건드린 작업 뒤 항상
python3 $S/eagle_sheet.py --library design --uncategorized --out /tmp/uncat
```
- 분류 작업(미분류 정리): `eagle_sheet.py` 시트를 보고 번호별 폴더를 정한다 → 같은 라이브러리 안은 v2 `item/update` 의 `folders` 로 이동, 다른 라이브러리로 보낼 것은 `eagle_transfer.py`.
- 링크 정규식은 파일명에 공백·괄호가 있어도 확장자까지 한 링크로 읽는다.
- 볼트 검색은 `rg`(ripgrep)가 있으면 쓰고, 없으면 Python 으로 훑는다.

## 에셋 사용 — 작업 폴더로 복사 (`scripts/eagle_export.py`)
**정본은 항상 Eagle.** 영상·웹·문서 프로젝트에서 쓸 때만 필요한 폴더를 복사해 간다. 복사본을 고쳐도 Eagle 에 반영되지 않으니, 수정은 Eagle 에서 하고 다시 가져온다.
- 라이브러리를 **읽기만** 한다 (metadata.json 파싱, 앱·API 미사용) → 활성 라이브러리가 아니어도 되고 사용자 화면이 바뀌지 않는다.
- 폴더 확인: `python3 scripts/eagle_export.py --library design --list "Characters"`
- 복사: `python3 scripts/eagle_export.py --library design --folder "Characters/Mascot Motion Kit" --recursive --dest <프로젝트>/public/assets/mascot`
	- `--library <별칭>|<.library 경로>` · `--recursive` 하위 폴더 포함(구조 유지) · `--flatten` 한 폴더로 · `--tag transparent` 태그 필터(반복=AND) · `--ext png,jpg` · `--dry-run`
- 파일·폴더 이름은 번들러 친화 슬러그(공백·`·`·`@` → `-`, 한글 유지). dest 에 `eagle-export.json` (Eagle id·원본 폴더·태그·크기·md5) 이 남는다.
- **재실행**: 같은 항목은 파일명을 고정하고 내용이 바뀐 것만 덮어쓴다 (md5). Eagle 에서 빠진 항목의 복사본은 지우지 않고 보고만 한다.
- 무거운 프로젝트(node_modules 등)는 볼트 밖에 두고, 볼트 안으로 복사하지 않는다.

## Bases 에서 Eagle 원본 직접 표시
- 에셋 노트의 `image`(또는 `cover`)에 **Eagle 실제 원본의 URL 인코딩한 `file:///…/images/{ID}.info/{name}.{ext}`** 를 넣는다. Base 는 카드 뷰의 `image: note.image` 로 직접 렌더한다. `eagleUrl: "eagle://item/{ID}"` 는 항목을 여는 별도 링크다. 예시 Base: `assets/Visual Assets.base`.
- `eagle://` 가 이미지 바이트 URL 이 아니라는 사실에서 "Eagle 이미지는 Bases 에 표시할 수 없다"고 결론 내리지 않는다. 표시를 위해 볼트에 이미지 사본을 만들지 않는다. 사용자가 명시적으로 사본·내보내기를 원할 때만 복사한다.
- 실제 항목 metadata·원본 존재·비삭제를 확인하고 `Path.as_uri()` 등으로 **한 번만** 인코딩한다. 공백, 한글, 괄호, `%` 가 있는 경로도 원본으로 decode 되는지 확인한다. 파일명·썸네일 경로를 추측하지 않는다.
- 개발자 도구에서 `new Image().src = "file:///…"` 만 시험하면 Electron 보안 제한으로 실패할 수 있다. 실제 Base 카드 표시로 검증한다. 카드 뷰의 `image` 속성 누락도 먼저 확인한다.
- 여러 기기에서 쓰면 기기마다 라이브러리 경로가 같은지 확인한다. 한 기기에서 확인한 것을 다른 기기 보증으로 확대하지 않는다.

## 함정 (실측)
- **Eagle 중복 병합**: 살아 있는 항목과 같은 파일을 `addFromPath` 하면 새 항목 없이 기존 항목에 폴더만 추가하고 success 를 돌려준다. 이 상태에서 "교체"한다고 기존 항목을 휴지통으로 보내면 항목이 사라진다. → 교체는 반드시 추가 **전에**, 추가 후 새 id 검증. 스크립트에 반영됨.
- **v1 vs v2 API** (Eagle 4.0.0 실측): v1 `/api/item/update` 는 `name`·`folders` 를 success 로 받고 **무시**한다. **v2 `/api/v2/item/update`** 는 `folders`(폴더 이동)·`name`·`tags`·`annotation`·`url`·`star` 모두 반영한다. 폴더 이동·메타데이터 수정은 항상 v2.
- **v2 이름 변경 = 실제 파일명 변경**: `images/{ID}.info/{name}.png` 가 바뀐다. Obsidian 노트가 이 경로를 `file:///…` 로 직접 링크하므로 **노트에 연결된 항목은 이름을 바꾸지 않는다.** 폴더 이동은 경로가 안 바뀌어 안전하다.
- **이름 변경 전 연결 검사**: `rg -l --fixed-strings {ID} -g '*.md' "{vault}"`. 결과가 있으면 이름 변경 금지.
- **라이브러리 폴더를 옮기면 옛 링크가 전부 깨진다**: 노트가 라이브러리 절대경로를 링크하기 때문이다. 되도록 옮기지 말고, 옮겼으면 설정의 `libraries` 를 새 경로로 고친 뒤 바로 `eagle_linkcheck.py --fix-moved` (미리보기) → `--apply`.
- **v2 에 더 있는 것**: `folder/update`, `smartFolder/*`, `tagGroup/*`, `tag/merge`, `library/icon`, `item/query`, `item/addComment`. 전체 목록은 앱 번들 `app.asar` 의 `app/js/api-server-v2.js`.
- **휴지통 복구 API 없음**: 휴지통 항목은 앱에서 수동 복구하거나, 원본 파일이 있으면 다시 가져온다.
- **스마트 폴더 API** (v2): `smartFolder/create {name, description, iconColor, conditions:[{rules:[{property:"tags", method:"intersection", value:[…]}], match:"OR", boolean:"TRUE"}]}`. **한 규칙의 `value` 에 태그를 여러 개 넣으면 모두 가진 항목만** 잡힌다 → 태그마다 규칙을 나누고 `match:"OR"`. 개수 확인은 `smartFolder/get` 의 `imageCount` (같은 버전의 `smartFolder/getItems` 는 500 오류).
- `addFromPath` 는 비동기라 목록 반영이 수 초 늦다 — 스크립트가 최대 30초 기다린다.
- **Eagle 은 활성 라이브러리에만 쓴다**: 전환이 필요하면 `eagle_import.py --switch` 나 `eagle_transfer.py` 를 쓴다. 둘 다 **작업을 시작할 때 사용자가 보고 있던 라이브러리로 되돌린다** (`eagle_common.keep_active`). 직접 API 를 부를 때도 시작 시 `library/info` 로 현재 라이브러리를 기억했다가 끝나면 그리로 복귀한다. 특정 라이브러리로 고정 복귀하지 않는다. 읽기 전용 스크립트(`eagle_export`·`eagle_linkcheck`·`eagle_sheet`)는 전환하지 않는다.

## 라이브러리 간 이전 (노트 링크 유지)
보통은 `eagle_transfer.py` 한 번으로 끝난다. 손으로 할 때의 순서:
1. 원본 파일을 스테이징 폴더에 복사하고, manifest 항목마다 `source_id` 를 넣는다 (이름·태그·주석·url·별점 보존, 주석에 `이전: A → B (날짜, 원본 ID …)`).
2. 대상 라이브러리로 전환 → `eagle_import.py manifest.json --map-out idmap.json` → {원본 id: 새 id}.
3. **노트 링크 갱신**: `eagle_relink.py --map idmap.json --to <대상>` (미리보기) → `--apply`. `_thumbnail.png` 링크는 새 위치에 썸네일이 없으면 원본 파일로 연결된다.
4. 검증: `eagle_linkcheck.py --ids <옛 ID…>` 로 옛 id 가 볼트에 남지 않았는지, `eagle_linkcheck.py` 로 모든 링크가 실제 파일을 가리키는지.
5. 원본 라이브러리로 전환 → 원본 항목을 휴지통으로 (새 링크가 모두 살아 있을 때만) → 처음 보던 라이브러리로 복귀.

## 이미지 외 파일 (오디오 등)
- 같은 `eagle_import.py` 로 넣는다 (MD5 중복 건너뜀 동일). Eagle 4.0.0 이 미리보기·재생하는 오디오: aac, flac, m4a, mp3, ogg, wav.
- 동기화하는 라이브러리에는 MP3 를 권장한다. 정리 규칙 예시는 `references/taxonomy.example.md` 끝.

## 함께 쓰면 좋은 것
- 이미지 생성 스킬·도구 → 생성 후 이 스킬로 파일링. 주석의 `gen:` 에 모델과 설정을, 마지막 줄에 프롬프트를 남긴다.
- [CMDS Eagle](https://github.com/johnfkoo951/cmds-eagle) Obsidian 플러그인 → Obsidian 안에서 Eagle 검색·임베드. 이 플러그인이 만든 `file:///` 링크도 이 스킬의 링크 검사·갱신 대상이다.

## References
- `references/taxonomy.example.md` — 라이브러리 역할·폴더 트리·이름·태그·주석·URL·별점 규칙 템플릿
- `references/asset-notes-rules.example.json` — 에셋 노트 규칙 템플릿: 대상 폴더, 종류(assetKind), 장면 분류(sceneKeywords·kindScene), 항목별 overrides
- `assets/Visual Assets.base` — 에셋 노트를 이미지 카드로 모아 보는 Base 예시
