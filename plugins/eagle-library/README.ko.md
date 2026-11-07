# eagle-library

[![한국어](https://img.shields.io/badge/lang-한국어-green)](README.ko.md) [![English](https://img.shields.io/badge/lang-English-blue)](README.md)

**에이전트가 이미지를 Eagle에 정리해 넣되, 그 이미지를 링크한 노트는 깨지지 않게 합니다.**

[Eagle](https://eagle.cool)은 생성 이미지, 캡처, 디자인 에셋을 모아 두기 좋은 곳입니다. 그런데 옵시디언 노트가 Eagle 원본 파일을 직접 링크하기 시작하면 작은 실수가 크게 번집니다. 항목 이름을 바꾸면 디스크의 파일 이름이 바뀌고, 라이브러리 폴더를 옮기면 링크가 전부 깨지고, 이미 있는 파일을 다시 넣으면 기존 항목에 조용히 합쳐집니다. `eagle-library`는 이런 경우를 다루는 Claude Code 스킬과 작은 Python 스크립트 8개입니다.

| 하는 일 | 내용 |
|---|---|
| **파일링** | JSON manifest로 폴더, 이름, 태그, 주석, 별점까지 정리해 넣습니다. MD5로 중복을 건너뛰고, 교체할 항목은 추가 *전에* 휴지통으로 보내고, 새 항목이 정말 생겼는지 확인합니다 |
| **이전** | 라이브러리 사이로 옮기면서 볼트의 `file:///`·`eagle://` 링크를 새 ID로 고치고, 옛 ID가 남지 않았는지 확인한 뒤에만 원본을 휴지통으로 보냅니다 |
| **점검** | 볼트에서 더 이상 파일을 가리키지 않는 Eagle 링크를 모두 찾고, 라이브러리 폴더 이동으로 깨진 링크를 복구합니다 |
| **내보내기** | Eagle 폴더를 영상·웹·문서 프로젝트 폴더로 복사합니다. 다시 실행하면 바뀐 것만 복사합니다. 정본은 계속 Eagle입니다 |
| **목록화** | 에셋마다 옵시디언 노트(`type: visual-asset`) 하나를 두고 `image`에 Eagle 원본을 연결해, Bases 카드 뷰 하나로 라이브러리 전체를 봅니다 |

쓰기 작업은 Eagle API를 거치고, 끝나면 작업 전에 보고 있던 라이브러리로 돌아갑니다. 읽기 전용 스크립트는 앱을 건드리지 않습니다.

## 설치

```text
/plugin marketplace add johnfkoo951/cmdspace-plugins
/plugin install eagle-library@cmdspace-plugins
```

Claude Code 2.1.275 이상에서는 한 줄로도 됩니다: `/plugin install eagle-library --marketplace johnfkoo951/cmdspace-plugins`

직접 설치: `skills/eagle-library/` 폴더를 `~/.claude/skills/`(Claude Code)나 쓰는 에이전트의 스킬 폴더에 복사합니다. 스킬 폴더 ZIP은 [릴리스](https://github.com/johnfkoo951/cmdspace-plugins/releases)마다 첨부되어 있습니다.

필요한 것: 쓰기 작업에는 Eagle 4.x 실행(로컬 API 포트 41595), Python 3.9 이상. 선택: 볼트 검색을 빠르게 하는 [ripgrep](https://github.com/BurntSushi/ripgrep), `eagle_sheet.py`용 [Pillow](https://pypi.org/project/pillow/).

## 설정

`~/.config/eagle-library/config.json`을 만듭니다(다른 위치라면 환경 변수 `EAGLE_LIBRARY_CONFIG`로 지정). 템플릿은 [`examples/config.example.json`](examples/config.example.json)입니다.

```json
{
  "vault": "~/Obsidian/Your Vault",
  "vaultName": "Your Vault",
  "libraries": {
    "personal": "~/Eagle/Personal.library",
    "design": "~/Shared/Team Design.library"
  },
  "assetNotesRules": "~/.config/eagle-library/asset-notes-rules.json"
}
```

| 키 | 용도 |
|---|---|
| `vault` | 옵시디언 볼트 루트. 링크 점검·갱신과 에셋 노트에 필요합니다. Eagle만 쓴다면 비워 둬도 됩니다 |
| `vaultName` | `obsidian://open?vault=…` 링크에 들어가는 볼트 이름 (기본값은 폴더 이름) |
| `libraries` | `.library` 폴더의 짧은 이름. 스크립트에 이 이름이나 전체 경로를 줍니다 |
| `assetNotesRules` | 에셋 노트 규칙 (선택). [`asset-notes-rules.example.json`](skills/eagle-library/references/asset-notes-rules.example.json)에서 시작합니다 |

그다음 라이브러리를 어떻게 정리하는지 적어 둡니다. [`taxonomy.example.md`](skills/eagle-library/references/taxonomy.example.md)는 라이브러리 역할, 폴더 트리, 이름, 태그, 주석, URL, 별점 규칙을 담은 템플릿입니다. 에이전트는 파일링 전에 이 문서와 기존 항목을 먼저 읽습니다.

## 사용

Claude Code를 열고 평소 말로 부탁합니다.

```text
이 이미지들 이글에 넣어줘. 태그랑 주석까지 정리해서.
생성한 이미지 12장을 design 라이브러리 Characters/Mascot에 넣어줘.
이 항목들 design에서 personal로 옮기고 노트 링크는 살려 줘.
Eagle의 Mascot Motion Kit 폴더를 ./public/assets/mascot으로 가져와.
볼트의 Eagle 링크가 다 살아 있는지 확인해 줘.
```

에이전트가 manifest를 쓰고, dry-run을 보여 주고, 가져온 다음 결과를 검증합니다. 스크립트를 직접 돌려도 됩니다.

```bash
S=skills/eagle-library/scripts
python3 $S/eagle_import.py manifest.json --dry-run          # 확인 후 --dry-run 없이
python3 $S/eagle_transfer.py --from design --to personal --ids <ID…> --folder "10. Obsidian/13. Daily" --dry-run
python3 $S/eagle_linkcheck.py                               # 깨진 링크가 있으면 exit 1
python3 $S/eagle_export.py --library design --folder "Characters/Mascot" --recursive --dest ./assets
python3 $S/eagle_asset_notes.py --check                     # 확인 후 --apply
python3 $S/eagle_sheet.py --library design --uncategorized --out /tmp/uncat
```

| 스크립트 | Eagle 앱 필요 |
|---|---|
| `eagle_import.py` · `eagle_transfer.py` | 필요 |
| `eagle_asset_notes.py --apply` | 노트 링크를 Eagle에 적을 때만 (`--no-url`이면 불필요) |
| `eagle_linkcheck.py` · `eagle_relink.py` · `eagle_export.py` · `eagle_sheet.py` · `--check` | 불필요 (라이브러리 폴더를 직접 읽음) |

## 막아 주는 Eagle 함정

Eagle 4.0.0에서 실측했습니다.

- 살아 있는 항목과 같은 파일을 추가하면 새 항목이 생기지 **않습니다**. Eagle은 기존 항목에 폴더만 더하고 성공이라고 답합니다. 기존 항목을 먼저 휴지통으로 보내고, 추가하고, 새 ID를 확인합니다.
- v1 `item/update`는 `name`과 `folders`를 받고도 조용히 무시합니다. `/api/v2/item/update`를 씁니다.
- 항목 이름을 바꾸면 실제 파일(`images/{ID}.info/{name}.png`) 이름이 바뀌어 그 파일을 링크한 노트가 깨집니다. 링크된 항목은 이름을 바꾸지 않습니다. 폴더 이동은 안전합니다.
- 쓰기는 활성 라이브러리에만 됩니다. 스크립트가 필요할 때 전환하고, 보고 있던 라이브러리로 되돌립니다.
- 스마트 폴더 규칙의 `value` 하나에 태그를 여러 개 넣으면 *모두 가진* 항목만 잡힙니다. 태그마다 규칙을 나누고 `match: "OR"`을 씁니다.

## 에셋 노트와 Bases 갤러리

`eagle_asset_notes.py`는 규칙 파일에 적은 폴더의 Eagle 항목마다 노트를 하나씩 만듭니다. 노트의 `image` 속성은 Eagle 원본의 URL 인코딩된 `file:///` 경로라서, 이미지를 볼트에 복사하지 않고도 Bases 카드 뷰에 보입니다. 예시 Base는 [`skills/eagle-library/assets/Visual Assets.base`](skills/eagle-library/assets/Visual%20Assets.base)입니다. 이미 고친 노트는 다시 덮어쓰지 않습니다.

## 함께 쓰기

[CMDS Eagle](https://github.com/johnfkoo951/cmds-eagle)은 옵시디언 안에서 Eagle 항목을 검색하고 임베드하는 플러그인입니다. 이 플러그인이 만든 링크도 위 점검 대상입니다.

## 테스트

```bash
python3 skills/eagle-library/scripts/test_eagle_scripts.py
```

임시 폴더에 가짜 Eagle 라이브러리와 볼트를 만들어 모든 스크립트를 실행합니다. `eagle_import.py --dry-run`은 가짜 API로 시험합니다. Eagle 앱이 없어도 됩니다.

## 언어

스킬 지침과 스크립트 메시지는 한국어 볼트에서 만들어져 한국어입니다. 영어로 대화해도 Claude가 그대로 따릅니다. `eagle_asset_notes.py`가 만드는 노트의 소제목은 영어입니다.

## 만든 사람

Yohan Koo (CMDSPACE) · <https://cmdspace.work>

MIT License.
