<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements. See the NOTICE file
distributed with this work for additional information
regarding copyright ownership. The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the
specific language governing permissions and limitations
under the License.
-->

# ABLESTACK Kubernetes ISO

Mold Europa에서 사용하는 Kubernetes 바이너리·컨테이너 이미지·설치 매니페스트를 버전별 ISO로 만드는 전용 저장소입니다. Cloud 전체 빌드와 독립적으로 ISO를 생성·검증하고, GitHub Release의 고정 URL에서 다운로드하거나 Mold에 URL로 등록할 수 있습니다. 노드 OS를 설치하는 부팅 ISO가 아니므로 Kubernetes 노드 템플릿은 별도로 준비합니다.

- 공식 소스와 Release: [ablecloud-team/ablestack-kubernetes-iso](https://github.com/ablecloud-team/ablestack-kubernetes-iso), 기본 브랜치 `main`
- Mold 소비 코드: [ablecloud-team/ablestack-cloud](https://github.com/ablecloud-team/ablestack-cloud)의 `ablestack-europa`

이 문서는 공식 저장소를 clone하거나 자신의 계정/조직으로 fork한 사용자를 위한 안내입니다. 직접 clone하면 `origin`은 공식 저장소이고, fork를 clone하면 `origin`은 자신의 저장소, `upstream`은 공식 저장소입니다. 공식 소스를 사용한 Local 빌드와 사용자 fork의 빌드 산출물은 별도의 출처로 기록합니다.

## 지원 recipe와 구성요소

profile은 `mold-cks`, 빌드 아키텍처는 `amd64`, Mold 등록 아키텍처는 `x86_64`입니다.

| Kubernetes | 내부 AutoScaler 원본 | Calico | recipe |
| --- | --- | --- | --- |
| 1.34.2 | 1.34.5 + Mold 패치 | 3.32.2 | [JSON](scripts/util/kubernetes-iso/recipes/kubernetes-1.34.2-amd64.json) |
| 1.34.9 | 1.34.5 + Mold 패치 | 3.32.2 | [JSON](scripts/util/kubernetes-iso/recipes/kubernetes-1.34.9-amd64.json) |
| 1.34.12 | 1.34.5 + Mold 패치 | 3.32.2 | [JSON](scripts/util/kubernetes-iso/recipes/kubernetes-1.34.12-amd64.json) |
| 1.35.9 | 1.35.2 + Mold 패치 | 3.33.0 | [JSON](scripts/util/kubernetes-iso/recipes/kubernetes-1.35.9-amd64.json) |
| 1.36.5 | 1.36.1 + Mold 패치 | 3.33.0 | [JSON](scripts/util/kubernetes-iso/recipes/kubernetes-1.36.5-amd64.json) |
| 1.37.1 | 고정 1.37 개발 source + Mold 패치 | 3.33.0 | [개발 시험 JSON](scripts/util/kubernetes-iso/recipes/kubernetes-1.37.1-amd64.json) |

Provider·AutoScaler에는 Mold API의 **HMAC-SHA256** 인증을 적용한 내부 컴포넌트를 사용합니다. recipe에 SDK/source SHA·이미지 digest·빌드 출처를 고정합니다. AutoScaler는 Kubernetes minor에 맞는 원본과 내부 패치를 조합합니다. CSI는 별도 SHA256 호환성 감사 전이므로 이 profile에 포함하지 않습니다.

**1.37.1은 개발 시험 후보**입니다. 해당 recipe의 AutoScaler는 stable 원본이 아니며 공식 게시가 차단됩니다. recipe가 존재하거나 ISO 검증을 통과했다는 사실은 실제 클러스터 생성·확장·업그레이드·삭제 및 Provider/AutoScaler 런타임 지원 판정을 대신하지 않습니다. 공식 Release의 qualification과 증거를 확인합니다.

## 공식 Release 다운로드

빌드 없이 ISO를 사용하려면 공식 저장소의 [Releases](https://github.com/ablecloud-team/ablestack-kubernetes-iso/releases)에서 원하는 Kubernetes 버전의 게시된 Release와 assets를 선택합니다. 해당 버전의 Release가 아직 게시되지 않았다면 아래 Local 빌드 또는 Actions 검증 산출물을 사용합니다.

tag는 `k8s-v<version>-mold-cks-amd64-<revision>-<source8>`, 파일 기본 이름은 `kubernetes-v<version>-mold-cks-amd64-<revision>-<source8>`입니다. `source8`은 ISO를 만든 commit SHA의 앞 8자리입니다. 사용하려는 Release의 실제 tag를 입력하여 다운로드합니다.

```bash
set -euo pipefail
ISO_REPOSITORY=ablecloud-team/ablestack-kubernetes-iso
read -r -p 'Releases 페이지에서 선택한 실제 tag: ' TAG
[[ "$TAG" =~ ^k8s-v[0-9]+\.[0-9]+\.[0-9]+-mold-cks-amd64-r[1-9][0-9]*-[a-f0-9]{8}$ ]]
NAME="kubernetes-${TAG#k8s-}"
BASE_URL="https://github.com/${ISO_REPOSITORY}/releases/download/${TAG}"
mkdir -p "$HOME/work/iso-download/$TAG"
cd "$HOME/work/iso-download/$TAG"
for FILE in "$NAME.iso" "$NAME.sha256" "$NAME.registration.json" SHA256SUMS; do
  curl --fail --location --retry 3 "$BASE_URL/$FILE" -o "$FILE"
done
sha256sum --check "$NAME.sha256"
sha256sum --check --ignore-missing SHA256SUMS
jq '{name, kubernetesversion, arch, download_url, checksum, mincpunumber, minmemory}' \
  "$NAME.registration.json"
```

`ISO_REPOSITORY`는 다운로드할 Release가 게시된 저장소입니다. 사용자 저장소에 별도로 게시한 Release를 받을 때는 자신의 `<owner>/ablestack-kubernetes-iso`로 변경합니다. 이름이나 현재 branch HEAD에서 다운로드 경로를 추정하지 말고 Release의 실제 tag와 `registration.json`을 확인합니다. Mold에는 영구 `releases/download/` URL을 사용하며 redirect 뒤의 만료되는 CDN 주소를 저장하지 않습니다.

## Local 환경 준비

Linux/WSL의 `x86_64` 환경에서 빌드합니다. Windows 사용자는 **WSL ext4** 작업 디렉터리를 사용하고 source·cache·산출물을 `/mnt/c`에 두지 않습니다.

- Git, curl, jq, skopeo, xorriso, Python 3 및 PyYAML
- Go **1.26.8**: Actions와 같은 버전으로 설치하고 `go`가 PATH에 있도록 설정
- setup 스크립트가 checksum을 검증하여 설치하는 cosign **2.4.3**, containerd/ctr **1.7.28**
- Actions 제어와 PR 생성 시 GitHub CLI `gh` 및 GitHub 인증

OS 패키지는 Linux 배포판의 패키지 관리자로 준비합니다. setup 스크립트는 Go와 OS 패키지를 설치하지 않습니다. 빌드 중 공식 바이너리·이미지·서명 검증 서비스에 접근할 수 있어야 합니다.

### 공식 저장소를 직접 clone

```bash
set -euo pipefail
mkdir -p "$HOME/work"
cd "$HOME/work"
git clone --branch main https://github.com/ablecloud-team/ablestack-kubernetes-iso.git
cd ablestack-kubernetes-iso
export GITHUB_REPOSITORY=ablecloud-team/ablestack-kubernetes-iso
git remote -v
```

업데이트할 때는 자신의 변경을 먼저 보존한 뒤 `main`에서 `git pull --ff-only origin main`을 실행합니다. 특정 공식 Release와 같은 소스를 사용할 때는 그 Release의 tag를 fetch한 뒤 checkout합니다.

### 자신의 저장소로 fork한 뒤 clone

GitHub 공식 저장소 화면에서 **Fork**로 자신의 계정 또는 조직에 `ablestack-kubernetes-iso`를 생성합니다. 아래 `FORK_OWNER`에는 실제 fork 소유자를 입력합니다.

```bash
set -euo pipefail
read -r -p '자신의 fork GitHub 계정/조직명: ' FORK_OWNER
: "${FORK_OWNER:?fork 소유자를 입력하세요}"
mkdir -p "$HOME/work"
cd "$HOME/work"
git clone --branch main "https://github.com/${FORK_OWNER}/ablestack-kubernetes-iso.git"
cd ablestack-kubernetes-iso
git remote add upstream https://github.com/ablecloud-team/ablestack-kubernetes-iso.git
export GITHUB_REPOSITORY="${FORK_OWNER}/ablestack-kubernetes-iso"
git remote -v
```

fork의 `main`을 공식 코드와 동기화하려면 작업 변경을 먼저 보존한 뒤 다음을 실행합니다. fast-forward가 불가능하면 로컬 commit/branch 상태를 확인해 통합합니다.

```bash
git fetch upstream
git switch main
git merge --ff-only upstream/main
git push origin main
```

빌드 결과의 `source_repository`는 **실제로 빌드하는 저장소**여야 합니다. Local 실행에서는 위 `GITHUB_REPOSITORY`를 명시적으로 설정하고 새 셸에서도 다시 설정합니다. Actions에서는 GitHub가 실행 저장소 값을 제공합니다. 현재 builder는 이 환경 변수가 없으면 지정된 시험 저장소를 기본값으로 사용하므로 공식 clone/fork 모두 이 값을 설정해야 출처가 정확히 기록됩니다.

두 방식 중 하나로 clone한 다음, 저장소 루트에서 도구를 준비합니다.

```bash
set -euo pipefail
: "${GITHUB_REPOSITORY:?clone한 저장소의 owner/name을 먼저 설정하세요}"
go version
python3 -c 'import yaml; print(yaml.__version__)'
scripts/util/kubernetes-iso/setup-tools.sh "$HOME/work/mold-iso-tools"
export PATH="$HOME/work/mold-iso-tools:$HOME/work/mold-iso-tools/bin:$PATH"
sudo install -d -m 0711 /run/containerd
python3 -m unittest discover -s scripts/util/kubernetes-iso/tests -v
```

`/run/containerd` 준비는 현재 Linux 세션에서 필요합니다. 검증기는 임시 root/state/socket을 가진 격리 daemon으로 이미지를 import하며 기존 containerd 서비스·socket을 사용하지 않습니다.

## ISO 생성과 독립 재검증

저장소 루트에서 실행합니다. Release용 빌드는 추적 파일의 변경을 먼저 commit해야 합니다. 현재 HEAD와 `GITHUB_REPOSITORY`가 산출물 provenance에 기록됩니다. AutoScaler manifest는 실제 ServiceAccount에 연결된 storage·DRA informer의 get/list/watch 권한도 검사합니다. DRA 3종(ResourceClaim, ResourceSlice, DeviceClass)과 VolumeAttachment는 명시적인 읽기 전용 권한을 요구하며, 쓰기·wildcard 권한은 거부합니다.

```bash
set -euo pipefail
: "${GITHUB_REPOSITORY:?clone한 저장소의 owner/name을 먼저 설정하세요}"
VERSION=1.34.12
REVISION=r1
SOURCE8=$(git rev-parse --short=8 HEAD)
RECIPE="scripts/util/kubernetes-iso/recipes/kubernetes-${VERSION}-amd64.json"
OUTPUT="$HOME/work/iso-output/${VERSION}/${REVISION}-${SOURCE8}"
scripts/util/create-kubernetes-binaries-iso.sh \
  --recipe "$RECIPE" --output "$OUTPUT" --revision "$REVISION"
NAME="kubernetes-v${VERSION}-mold-cks-amd64-${REVISION}-${SOURCE8}"
(
  cd "$OUTPUT"
  sha256sum --check "$NAME.sha256"
)
python3 scripts/util/kubernetes-iso/validate.py \
  --iso "$OUTPUT/$NAME.iso" --recipe "$RECIPE" \
  --report "$OUTPUT/independent-validation.json"
jq '{status, containerd_import, iso_sha256, bytes}' "$OUTPUT/independent-validation.json"
jq '{source_repository, source_sha, release_eligible}' "$OUTPUT/$NAME.registration.json"
```

생성기는 빌드 후 ISO를 다시 추출하여 독립 검증을 자동 실행합니다. 위 `validate.py` 명령은 산출물을 다시 검사하는 방법입니다. CDROM label·필수 payload·파일 checksum·실제 Kubernetes 실행 버전/amd64 ELF·공식 바이너리 서명·YAML·OCI blob/layer digest·내부 Go 바이너리 source/SDK 및 격리 containerd import를 검사합니다. `status=PASS`와 `containerd_import.status=PASS`를 모두 확인합니다.

다운로드 cache 기본 위치는 `$XDG_CACHE_HOME/mold-kubernetes-iso`, 환경 변수가 없으면 `~/.cache/mold-kubernetes-iso`입니다. `--cache <ext4 디렉터리>`로 변경할 수 있습니다. 이미 같은 출력 파일이 존재하면 덮어쓰지 않습니다. 기존 산출물을 재사용하거나 새 revision(`r2` 등)/별도 출력 디렉터리를 사용합니다.

미커밋 소스의 사전 확인은 같은 빌드 명령에 `--development`를 추가합니다. 이때 파일명에는 `-local`이 붙고 `release_eligible=false`가 기록되므로 publisher가 Release 게시를 거부합니다. 임의 버전 문자열만 바꿔 빌드할 수 없으며 새 버전은 공식 바이너리 checksum·이미지 digest·minor별 내부 컴포넌트가 고정된 recipe부터 추가해야 합니다.

## GitHub Actions로 빌드·검증

공식 저장소 또는 자신의 fork에서 **Actions → Mold Kubernetes ISO → Run workflow**를 선택합니다. fork에서 Actions가 비활성 상태라면 Actions 탭에서 먼저 활성화합니다. 수동 실행에는 저장소의 실행 권한과 기본 브랜치의 `workflow_dispatch` 정의가 필요합니다. [GitHub 수동 실행 안내](https://docs.github.com/actions/managing-workflow-runs/manually-running-a-workflow), [fork의 workflow 동작](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)을 참고합니다.

- `version`: recipe에 포함된 Kubernetes patch 버전 한 개
- `revision`: `r1`, `r2` 등 산출물 revision
- `publish`: 일반 clone/fork 사용자는 **false**로 빌드·검증 산출물을 생성

GitHub CLI 예시입니다. 공식 저장소에 실행 권한이 없으면 `ISO_REPOSITORY`를 자신의 fork로 변경하고 해당 저장소에서 실행합니다. 작업 브랜치를 검사할 때는 `--ref`를 그 브랜치명으로 바꿉니다.

```bash
ISO_REPOSITORY=ablecloud-team/ablestack-kubernetes-iso
gh workflow run kubernetes-iso.yml \
  --repo "$ISO_REPOSITORY" --ref main \
  -f version=1.34.12 -f revision=r1 -f publish=false
gh run list --repo "$ISO_REPOSITORY" --workflow kubernetes-iso.yml --limit 5
read -r -p '확인할 실제 Actions run ID: ' RUN_ID
gh run watch "$RUN_ID" --repo "$ISO_REPOSITORY" --exit-status
gh run download "$RUN_ID" --repo "$ISO_REPOSITORY" \
  --name kubernetes-1.34.12-amd64 \
  --dir "$HOME/work/iso-artifacts/$RUN_ID/1.34.12"
```

각 버전의 artifact 이름은 `kubernetes-<version>-amd64`이며 보존 기간은 **7일**입니다. artifact ZIP/Actions 페이지 URL은 Mold에 등록할 ISO 직접 다운로드 주소가 아닙니다. Local 또는 Actions 산출물은 검증한 ISO 파일을 사용하고, URL 등록에는 공개 Release나 접근 가능한 다운로드 서버의 고정 ISO 주소를 준비합니다.

빌드 관련 경로를 변경한 PR은 여섯 버전 matrix를 검증하며 Release를 게시하지 않습니다. 일반 branch push 자동 실행은 [workflow](.github/workflows/kubernetes-iso.yml)의 `on.push.branches`/`paths` 필터를 따르므로 임의 fork 브랜치에서 자동 실행된다고 가정하지 않습니다.

현재 `publish=true`의 trial 자동 게시와 `publish.py --mode origin-trial`은 코드에 지정된 검증 저장소만 지원합니다. **임의 사용자 fork의 Release 자동 게시를 지원하는 옵션이 아닙니다.** 자신의 fork에서는 `publish=false`로 검증하고 artifact를 받습니다. 공식 게이트를 통과하는 tag 게시와 publisher 권한은 아래 유지관리 절차를 따릅니다.

## 산출물

기본 이름은 `kubernetes-v<version>-mold-cks-amd64-<revision>-<source8>`입니다.

| 파일 | 용도 |
| --- | --- |
| `<name>.iso` | Mold에 등록할 바이너리 ISO, CDROM label, 2 GiB 미만 |
| `<name>.sha256` | ISO 파일 SHA256 확인 |
| `<name>.manifest.json` | recipe/source SHA, 내부 컴포넌트, 이미지 및 payload provenance |
| `<name>.sbom.cdx.json` | CycloneDX payload 구성 목록 |
| `<name>.validation.json` | 독립 검증 결과와 ISO hash/크기 |
| `<name>.registration.json` | Mold 등록용 URL·버전·아키텍처·checksum·최소 리소스 |
| `<name>.notes.ko.md`, `SHA256SUMS` | publisher가 생성하는 Release 설명과 assets 전체 체크섬 |

게시 전 `registration.json.download_url`은 `null`입니다. 공식 publisher는 게시 시 실제 URL을 기록합니다. 별도 다운로드 서버를 사용한다면 게시한 ISO 파일의 실제 URL과 검증한 checksum을 Mold에 입력합니다. SBOM은 payload 구성 목록으로, 모든 컨테이너의 OS/전이 패키지 취약점 검사 결과를 뜻하지 않습니다. 도구 버전·OCI archive envelope가 다르면 환경 사이의 ISO 전체 hash가 달라질 수 있으므로 각 산출물의 실제 checksum으로 검증합니다.

## Mold에 등록

관리자 계정으로 **이미지 → 쿠버네티스 ISO → 쿠버네티스 버전 추가**에서 등록합니다. Kubernetes 지원 버전 등록 경로(`addKubernetesSupportedVersion`)를 사용합니다. 대상 zone과 아래 값을 확인합니다.

| Mold 입력 / API 필드 | `registration.json` 값 |
| --- | --- |
| 이름 / `name` | `name` (개발 시험은 DEV 등 식별 가능한 이름 사용) |
| Kubernetes 버전 / `semanticversion` | `kubernetesversion`, 예: `1.34.12` |
| ISO URL / `url` | 게시된 `download_url` 또는 자신이 제공하는 실제 고정 ISO URL |
| 체크섬 / `checksum` | `{SHA-256}` + ISO SHA256 hex |
| 아키텍처 / `arch` | `x86_64` |
| 최소 CPU / `mincpunumber` | `2` |
| 최소 메모리 / `minmemory` | `2048` MiB |

CPU 2/RAM 2048 MiB는 지원 버전 API 등록 최소값입니다. 실제 control-plane/worker/etcd 노드 offering은 별도 용량 설계가 필요합니다. secondary storage 다운로드 방식으로 등록할 때는 `directdownload=false`를 사용합니다. Local 파일은 UI의 **로컬에서 Kubernetes 버전 추가** 업로드 경로로 등록할 수도 있습니다.

GitHub asset 주소는 **HTTP 302 redirect**를 반환합니다. 다운로드 전 Mold 전역 설정의 기존 `store.download.follow.redirects` 값을 기록하고, GitHub URL 다운로드 기간에는 `true`로 설정합니다. 이 설정은 전체 store 다운로드에 영향을 줍니다. 다운로드 완료 후 운영 정책에 맞게 기존 값을 복원하고 재조회합니다.

등록 요청 후 ISO 다운로드 **Ready/100%**, 버전의 사용 가능 상태 및 secondary 실제 파일의 SHA256을 함께 확인합니다. ISO 파일 checksum은 API 인증의 HMAC-SHA256과 별개입니다. ISO Ready는 클러스터 생성 및 Provider/AutoScaler 동작 검증을 대신하지 않습니다.

클러스터 배포 전에는 노드 템플릿의 커널 **5.10 이상** 및 CNI 모듈/네트워크 준비를 확인합니다. 설치·확장·업그레이드에서 내부 매니페스트와 digest 이미지 참조를 유지하는 계약은 [상세 빌드·소비 절차](scripts/util/kubernetes-iso/README.ko.md)를 참고합니다.

## 유지관리자: 공식 Release 게시

공식 게이트는 [publisher](scripts/util/kubernetes-iso/publish.py)가 검사합니다.

1. SDK·Provider·AutoScaler의 공식 source/릴리즈와 이미지 digest를 recipe에 반영합니다. 후보 SDK와 시험 컴포넌트 출처를 제거합니다.
2. minor별 stable AutoScaler를 확보하고 Provider LB/VPC·AutoScaler·노드 생명주기 실환경 검증을 완료합니다. recipe의 `runtime_qualification`에 `PASS`와 증거 URL을 기록합니다.
3. ISO 구현과 recipe를 공식 저장소 `main`에 병합합니다. Mold 소비 변경의 최종 브랜치는 Cloud `ablestack-europa`입니다.
4. 병합된 source에 `k8s-v<version>-mold-cks-amd64-<revision>-<source8>` tag를 만들고 **공식 저장소에 tag를 push**합니다. tag Actions가 일치 버전을 빌드·검증하고 공식 publisher로 게시합니다.

publisher는 ISO 한 개, 독립 검증 PASS, producer 저장소·현재 HEAD·정확한 tag 일치, `upstream/main` ancestry와 위 승격 조건을 요구합니다. 직접 publisher를 실행하는 유지관리자는 `upstream` remote를 공식 저장소로 설정하고 `GITHUB_REPOSITORY=ablecloud-team/ablestack-kubernetes-iso`로 생성한 산출물과 해당 source checkout을 사용해야 합니다. Actions의 공식 게시 경로가 이 설정을 수행합니다.

기존 Release/tag/asset을 교체하지 않으며 `latest`를 변경하지 않습니다. 게시 후 인증 없는 전체 ISO GET과 SHA256 대조까지 수행합니다. recipe의 qualification이 `pending`이거나 development AutoScaler/후보 SDK가 남아 있으면 공식 게시가 차단됩니다.

## 기여와 문제 해결

fork의 작업 브랜치에서 변경하고 검증한 뒤 자신의 `origin`에 push하고 공식 저장소의 `main`으로 PR을 만듭니다. 새 Kubernetes 버전은 바이너리 checksum·이미지 digest·minor별 내부 컴포넌트 provenance와 검증 증거를 함께 추가합니다.

| 증상 | 확인 및 처리 |
| --- | --- |
| `source_repository`가 자신의 저장소와 다름 | Local 빌드 전 `GITHUB_REPOSITORY=<실제 owner>/ablestack-kubernetes-iso` 설정 |
| `missing build tool` / PyYAML import 오류 | OS 패키지·Go 설치, setup 스크립트 실행, PATH 확인 |
| `Release build requires committed source` | 추적 파일 변경을 commit하거나 Local 사전 확인에 `--development` 사용 |
| checksum·서명·digest 검증 실패 | 다운로드 상태와 고정 recipe를 조사하고 실패 원인 해결 후 재시도 |
| `immutable output already exists` / `immutable Release already exists` | 기존 산출물 사용 또는 새 revision/출력 디렉터리 선택 |
| `source HEAD mismatch` | 빌드한 commit과 게시 checkout의 HEAD 일치 여부 확인 |
| fork Actions가 실행되지 않음 | Actions 활성화·기본 브랜치의 workflow·branch/path 필터·실행 권한 확인 |
| fork에서 `publish=true`로 Release가 생기지 않음 | 일반 fork는 자동 게시 대상이 아님; `publish=false` 검증 artifact 사용 |
| Mold 다운로드에서 302 거부 | 영구 URL 사용 및 다운로드 중 `store.download.follow.redirects=true` 확인 |
| 공식 qualification/component gate 실패 | stable 원본·공식 컴포넌트·실환경 PASS·공식 main 병합 조건 충족 후 재빌드 |

구현 계약은 [상세 문서](scripts/util/kubernetes-iso/README.ko.md), 설계는 [ISO 이슈 #1228](https://github.com/ablecloud-team/ablestack-cloud/issues/1228) 및 [생명주기 Epic #1227](https://github.com/ablecloud-team/ablestack-cloud/issues/1227)을 참고합니다. 특정 시험 저장소·시험 Release·31번 환경의 검증 이력은 [별도 검증 보고서](docs/validation/iso-registration-20261006.md)에 보관합니다. Provider runtime 결과는 [실행 보고서](docs/validation/runtime-provider-20261006.md), 발견한 워커 복구 준비 절차는 [유지보수 검증 문서](docs/validation/worker-maintenance-20261006.md)를 참고합니다.

## 선택형 CSI ISO 프로파일

기본 `mold-cks` 프로파일과 GFS2 Primary/KVM 시험용 `mold-cks-csi` 프로파일을 각각 빌드합니다. Actions의 `profile` 입력으로 선택하며, Origin 변경 검증은 지원 버전 6개와 두 프로파일의 조합으로 진행합니다. CSI 프로파일은 SHA256 내부 드라이버·sidecar 이미지 8개·snapshot CRD·프로파일 체크섬을 함께 포함합니다. 기본 ISO의 CSI 활성화 여부는 바뀌지 않습니다.

Upstream을 clone하거나 fork한 저장소에서는 아래 recipe를 사용해 CSI ISO를 빌드할 수 있습니다. `--revision`과 source SHA가 산출물 식별자에 포함되므로 이미 등록한 ISO를 덮어쓰지 않습니다.

```bash
scripts/util/create-kubernetes-binaries-iso.sh \
  --recipe scripts/util/kubernetes-iso/recipes/kubernetes-1.34.12-mold-cks-csi-amd64.json \
  --output /home/ablecloud/work/iso-output --revision r1
```

새 Provider의 `ownership-v1` 기능은 ISO에 포함된 component provenance와 이미지/source 검증을 통과한 경우에만 표시됩니다. Mold backend에는 public IP `allocationgeneration`과 조건부 IP 반환 기능이 필요합니다. 구버전 ISO의 장기 시험 클러스터는 재등록·업그레이드하지 않고, 새 ISO는 별도 클러스터에서 시험합니다.

CSI 프로파일의 ISO 파일 검증과 실제 스토리지 검증은 각각 수행합니다. 해당 Kubernetes minor에서 생성·attach·확장·이동·snapshot/restore·Retain/Delete·실패 후 재시도를 통과하고 이슈 증거를 기록하기 전에는 공식 Release의 CSI qualification을 PASS로 올릴 수 없습니다. StorageClass에는 대상 Mold GFS2 Primary에 연결된 disk offering을 지정해야 합니다. 1.37 AutoScaler의 DEV baseline 제한과 Upstream 공식 Release 게이트도 계속 적용됩니다.
