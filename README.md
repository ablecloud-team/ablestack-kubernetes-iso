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

## 저장소와 현재 작업 경로

| 용도 | 저장소 / 브랜치 |
| --- | --- |
| Local 빌드·GitHub Actions 시험·공개 trial Release | [dhslove/ablestack-kubernetes-iso](https://github.com/dhslove/ablestack-kubernetes-iso) / `codex/kubernetes-iso-1228` |
| 최종 PR·공식 ISO source 및 Release | [ablecloud-team/ablestack-kubernetes-iso](https://github.com/ablecloud-team/ablestack-kubernetes-iso) / `main` / [PR #1](https://github.com/ablecloud-team/ablestack-kubernetes-iso/pull/1) |
| ISO를 소비하는 Mold 코드 | [ablecloud-team/ablestack-cloud](https://github.com/ablecloud-team/ablestack-cloud) / `ablestack-europa` / [PR #1229](https://github.com/ablecloud-team/ablestack-cloud/pull/1229) |
| 기능 설계·전체 생명주기 | [ISO 이슈 #1228](https://github.com/ablecloud-team/ablestack-cloud/issues/1228) / [Epic #1227](https://github.com/ablecloud-team/ablestack-cloud/issues/1227) |

2026-10-06 기준 ISO 구현은 Origin의 `codex/kubernetes-iso-1228`에 있습니다. 두 ISO 저장소의 기본 브랜치 `main`에는 아직 구현이 병합되지 않았으므로 아래 clone 명령에서 작업 브랜치를 지정합니다. 기존 Cloud 시험 Release는 검증 이력이며, 신규 ISO 생성·게시 경로는 이 전용 저장소입니다.

## 제공하는 ISO

profile은 `mold-cks`, 빌드 아키텍처는 `amd64`, Mold 등록 아키텍처는 `x86_64`입니다. 다음 여섯 버전의 recipe가 포함됩니다.

| Kubernetes | 내부 AutoScaler 원본 | Calico | 현재 Origin trial |
| --- | --- | --- | --- |
| 1.34.2 | 1.34.5 + Mold 패치 | 3.32.2 | [Release](https://github.com/dhslove/ablestack-kubernetes-iso/releases/tag/k8s-v1.34.2-mold-cks-amd64-r1-f6b6cd62) |
| 1.34.9 | 1.34.5 + Mold 패치 | 3.32.2 | [Release](https://github.com/dhslove/ablestack-kubernetes-iso/releases/tag/k8s-v1.34.9-mold-cks-amd64-r1-f6b6cd62) |
| 1.34.12 | 1.34.5 + Mold 패치 | 3.32.2 | [Release](https://github.com/dhslove/ablestack-kubernetes-iso/releases/tag/k8s-v1.34.12-mold-cks-amd64-r1-f6b6cd62) |
| 1.35.9 | 1.35.2 + Mold 패치 | 3.33.0 | [Release](https://github.com/dhslove/ablestack-kubernetes-iso/releases/tag/k8s-v1.35.9-mold-cks-amd64-r1-f6b6cd62) |
| 1.36.5 | 1.36.1 + Mold 패치 | 3.33.0 | [Release](https://github.com/dhslove/ablestack-kubernetes-iso/releases/tag/k8s-v1.36.5-mold-cks-amd64-r1-f6b6cd62) |
| 1.37.1 | 고정 1.37 개발 source + Mold 패치 | 3.33.0 | [개발 시험 Release](https://github.com/dhslove/ablestack-kubernetes-iso/releases/tag/k8s-v1.37.1-mold-cks-amd64-r1-f6b6cd62) |

Provider·AutoScaler에는 Mold API의 **HMAC-SHA256** 인증을 적용한 내부 컴포넌트를 사용합니다. recipe에 SDK/source SHA·이미지 digest·빌드 출처를 고정합니다. AutoScaler는 Kubernetes minor에 맞는 원본과 내부 패치를 조합합니다. CSI는 별도 SHA256 호환성 감사 전이므로 이 profile에 포함하지 않습니다.

위 Release는 모두 생성·독립 검증·비로그인 전체 다운로드 검사를 통과했습니다. 31번 환경에서는 기존 사용자 ISO 3개를 보존하고 신규 6개를 등록하여 Ready/100% 및 secondary 실제 파일 SHA256 일치를 확인했습니다. [빌드·등록 검증 보고서](docs/validation/iso-registration-20261006.md)에 producer SHA, 체크섬, 등록 식별자와 검증 범위가 있습니다.

**1.37.1은 개발 시험 후보**입니다. 현재 recipe의 AutoScaler는 stable 원본이 아니며 공식 게시가 차단됩니다. 모든 버전의 클러스터 생성·확장·업그레이드·삭제와 Provider LB/VPC·AutoScaler 런타임 검증은 별도 진행 대상입니다.

## 기존 Release 다운로드와 체크섬 확인

시험용 ISO를 바로 사용하려면 위 표의 Release에서 assets를 받습니다. 고정 다운로드 주소는 다음 구조입니다.

```text
https://github.com/<owner>/ablestack-kubernetes-iso/releases/download/<tag>/<filename>
```

다음은 이미 검증한 1.34.12 Origin trial을 받는 Bash 예시입니다. `VERSION`을 표의 다른 버전으로 변경해도 동일한 `r1-f6b6cd62` trial 경로를 사용할 수 있습니다.

```bash
set -euo pipefail
VERSION=1.34.12
REVISION=r1
SOURCE8=f6b6cd62
NAME="kubernetes-v${VERSION}-mold-cks-amd64-${REVISION}-${SOURCE8}"
TAG="k8s-v${VERSION}-mold-cks-amd64-${REVISION}-${SOURCE8}"
BASE_URL="https://github.com/dhslove/ablestack-kubernetes-iso/releases/download/${TAG}"
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

`SOURCE8`는 ISO를 만든 commit의 앞 8자리입니다. 현재 공개 trial의 producer 전체 SHA는 `f6b6cd6274e8be3c0a679c0bf622428bd7d111c0`이며 후속 문서 commit과 구분합니다. 새로운 빌드의 SHA·tag·파일명은 해당 Release의 `registration.json`과 `manifest.json`에서 확인합니다. Mold에는 GitHub의 영구 `releases/download/` URL을 사용하며, redirect 뒤에 나오는 만료되는 CDN 주소를 저장하지 않습니다.

## Local 빌드 준비

Windows 환경에서는 **WSL ext4** 작업 디렉터리를 사용합니다. source·cache·산출물을 `/mnt/c`에 두지 않습니다. Linux/WSL의 `x86_64` 환경에 다음 도구를 준비합니다.

- Git, curl, jq, skopeo, xorriso, Python 3 및 PyYAML
- Go **1.26.8**: 현재 Actions와 같은 버전으로 설치하고 `go`가 PATH에 있도록 설정
- 아래 setup 스크립트가 checksum을 검증하여 설치하는 cosign **2.4.3**, containerd/ctr **1.7.28**

빌드 중 공식 바이너리·이미지·서명 검증 서비스에 접근할 수 있어야 합니다. 설치 패키지는 Linux 배포판의 패키지 관리자로 준비합니다. setup 스크립트는 Go와 OS 패키지를 설치하지 않습니다.

```bash
set -euo pipefail
mkdir -p "$HOME/work/dhslove"
cd "$HOME/work/dhslove"
git clone --branch codex/kubernetes-iso-1228 \
  https://github.com/dhslove/ablestack-kubernetes-iso.git
cd ablestack-kubernetes-iso
go version
python3 -c 'import yaml; print(yaml.__version__)'
scripts/util/kubernetes-iso/setup-tools.sh "$HOME/work/mold-iso-tools"
export PATH="$HOME/work/mold-iso-tools:$HOME/work/mold-iso-tools/bin:$PATH"
sudo install -d -m 0711 /run/containerd
python3 -m unittest discover -s scripts/util/kubernetes-iso/tests -v
```

이미 clone한 경우에는 해당 디렉터리에서 작업 상태를 확인한 후 `git fetch origin` 및 `git pull --ff-only`로 동기화합니다. `/run/containerd` 준비는 현재 Linux 세션에서 필요합니다. 검증기는 임시 root/state/socket을 가진 격리 daemon으로 이미지를 import하며 기존 containerd 서비스·socket을 사용하지 않습니다.

## ISO 생성과 독립 재검증

저장소 루트에서 실행합니다. Release용 빌드는 추적 파일의 변경을 먼저 commit해야 합니다. 현재 HEAD가 산출물 provenance와 파일명에 기록됩니다.

```bash
set -euo pipefail
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
```

생성기는 빌드 후 ISO를 다시 추출하여 독립 검증을 자동 실행합니다. 위 `validate.py` 명령은 산출물을 다시 검사하는 방법입니다. 검증에는 CDROM label·필수 payload·파일 checksum·실제 Kubernetes 실행 버전/amd64 ELF·공식 바이너리 서명·YAML·OCI blob/layer digest·내부 Go 바이너리 source/SDK 및 격리 containerd import가 포함됩니다. `PASS`와 `containerd_import.status=PASS`를 모두 확인합니다.

다운로드 cache 기본 위치는 `$XDG_CACHE_HOME/mold-kubernetes-iso`, 환경 변수가 없으면 `~/.cache/mold-kubernetes-iso`입니다. `--cache <ext4 디렉터리>`로 변경할 수 있습니다. 이미 같은 파일이 존재하면 덮어쓰지 않습니다. 검증된 기존 파일을 재사용하거나 새 revision(`r2` 등)/별도 출력 디렉터리를 사용합니다.

미커밋 소스의 사전 확인은 같은 빌드 명령에 `--development`를 추가합니다. 이때 파일명에는 `-local`이 붙고 `release_eligible=false`가 기록되므로 Release 게시가 거부됩니다. 임의 버전 문자열만 바꿔 빌드할 수 없으며 새 버전은 공식 바이너리 checksum·이미지 digest·minor별 내부 컴포넌트가 고정된 recipe부터 추가해야 합니다.

## GitHub Actions 사용

[워크플로 파일](.github/workflows/kubernetes-iso.yml)은 다음 경로로 실행됩니다.

| 이벤트 | 빌드·게시 동작 |
| --- | --- |
| Origin `codex/kubernetes-iso-1228`의 빌드 관련 경로 변경 push | 여섯 버전 matrix 빌드·검증 후 각각 공개 trial Release 게시 |
| 빌드 관련 경로를 변경한 PR | 여섯 버전 빌드·검증, Release 게시 없음 |
| `workflow_dispatch` | 지정한 `version` 한 개 빌드·검증, `publish=true`일 때 Origin trial 게시 |
| Upstream의 `k8s-v*-mold-cks-amd64-r*` tag push | 일치 버전 빌드 후 공식 승격 게이트를 통과해야 게시 |

push/PR 대상 경로는 `scripts/util/kubernetes-iso/**`, `scripts/util/create-kubernetes-binaries-iso.sh`, `.github/workflows/kubernetes-iso.yml`입니다. 루트 `README.md`만 변경한 push는 ISO 재빌드를 시작하지 않습니다. 임의 이름의 새 브랜치는 현재 push 필터의 대상이 아닙니다.

현재 검증된 경로는 [Origin push run 37336050374](https://github.com/dhslove/ablestack-kubernetes-iso/actions/runs/37336050374)입니다. **수동 실행은 workflow가 기본 브랜치 `main`에 준비된 뒤 사용하는 절차**로 안내합니다. 현재 `main`에는 workflow가 아직 없으며, GitHub의 [수동 실행 전제조건](https://docs.github.com/actions/managing-workflow-runs/manually-running-a-workflow)을 확인해야 합니다.

기본 브랜치에 workflow가 준비되면 Actions → **Mold Kubernetes ISO** → **Run workflow**에서 작업 브랜치와 `version`, `revision`, `publish`를 선택합니다. GitHub CLI 예시는 다음과 같습니다. `publish=false`가 기본이며 검증 산출물만 생성합니다.

```bash
gh workflow run kubernetes-iso.yml \
  --repo dhslove/ablestack-kubernetes-iso \
  --ref codex/kubernetes-iso-1228 \
  -f version=1.34.12 -f revision=r2 -f publish=false
gh run list --repo dhslove/ablestack-kubernetes-iso \
  --workflow kubernetes-iso.yml --limit 5
```

게시를 포함한 시험은 `publish=true`를 지정합니다. 같은 source/version/revision의 Release가 이미 있으면 게시가 거부되므로 새 revision을 선택합니다. 각 버전의 Actions artifact 이름은 `kubernetes-<version>-amd64`이며 보존 기간은 **7일**입니다. 계속 다운로드하거나 Mold에 등록할 파일은 공개 Release assets를 사용합니다.

## 산출물과 Release 관리

기본 이름은 `kubernetes-v<version>-mold-cks-amd64-<revision>-<source8>`입니다.

| 파일 | 용도 |
| --- | --- |
| `<name>.iso` | Mold에 등록할 바이너리 ISO, CDROM label, 2 GiB 미만 |
| `<name>.sha256` | ISO 파일 SHA256 확인 |
| `<name>.manifest.json` | recipe/source SHA, 내부 컴포넌트, 이미지 및 payload provenance |
| `<name>.sbom.cdx.json` | CycloneDX payload 구성 목록 |
| `<name>.validation.json` | 독립 검증 결과와 ISO hash/크기 |
| `<name>.registration.json` | Mold 등록용 URL·버전·아키텍처·checksum·최소 리소스 |
| `<name>.notes.ko.md`, `SHA256SUMS` | 게시 시 생성하는 Release 설명과 assets 전체 체크섬 |

Local 빌드의 `registration.json.download_url`은 `null`이며 게시할 때 고정 Release URL이 채워집니다. SBOM은 payload 구성 목록으로, 모든 컨테이너의 OS/전이 패키지 취약점 검사 결과를 뜻하지 않습니다. 도구 버전·OCI archive envelope가 다르면 Local/Actions ISO 전체 hash가 달라질 수 있으므로 각 채널의 실제 산출물 checksum으로 검증합니다.

publisher는 한 디렉터리의 ISO 한 개, 독립 검증 PASS, producer 저장소 및 현재 HEAD 일치를 요구합니다. Origin 게시 대상은 `dhslove/ablestack-kubernetes-iso`로 제한됩니다. 기존 Release/tag/asset을 교체하지 않으며 Origin trial은 prerelease로 게시하고 `latest`를 변경하지 않습니다. 게시 후 인증 없는 전체 ISO GET과 SHA256 대조까지 수행합니다.

## Mold에 URL로 등록

관리자 계정으로 **이미지 → 쿠버네티스 ISO → 쿠버네티스 버전 추가**에서 등록합니다. 일반 OS ISO 등록 대신 Kubernetes 지원 버전 등록 경로(`addKubernetesSupportedVersion`)를 사용합니다. 대상 zone과 아래 값을 확인합니다.

| Mold 입력 / API 필드 | Release `registration.json` 값 |
| --- | --- |
| 이름 / `name` | `name` (개발 시험은 DEV 등 식별 가능한 이름 사용) |
| Kubernetes 버전 / `semanticversion` | `kubernetesversion`, 예: `1.34.12` |
| ISO URL / `url` | `download_url`, 영구 GitHub Release asset URL |
| 체크섬 / `checksum` | `{SHA-256}` + ISO SHA256 hex |
| 아키텍처 / `arch` | `x86_64` |
| 최소 CPU / `mincpunumber` | `2` |
| 최소 메모리 / `minmemory` | `2048` MiB |

CPU 2/RAM 2048 MiB는 지원 버전 API 등록 최소값입니다. 실제 control-plane/worker/etcd 노드 offering은 별도 용량 설계가 필요합니다. 31번 검증은 secondary storage 다운로드 방식(`directdownload=false`)으로 수행했습니다.

GitHub asset 주소는 **HTTP 302 redirect**를 반환합니다. 다운로드 전 Mold 전역 설정의 기존 `store.download.follow.redirects` 값을 기록하고, GitHub URL 다운로드 기간에는 `true`로 설정합니다. 이 설정은 전체 store 다운로드에 영향을 줍니다. 다운로드 완료 후 운영 정책에 맞게 기존 값을 복원하고 재조회합니다. 31번 시험에서는 `false → true → false`로 처리했습니다.

등록 요청 후 ISO 다운로드 **Ready/100%**, 버전의 사용 가능 상태 및 secondary 실제 파일의 SHA256을 함께 확인합니다. 실패하면 다운로드 로그와 redirect 설정·URL·checksum을 확인합니다. ISO 파일 checksum은 API 인증의 HMAC-SHA256과 별개입니다. ISO Ready는 클러스터 생성 및 Provider/AutoScaler 동작 검증을 대신하지 않습니다.

클러스터 배포 전에는 노드 템플릿의 커널 **5.10 이상** 및 CNI 모듈/네트워크 준비를 확인합니다. 설치·확장·업그레이드 시 ISO의 내부 매니페스트와 digest 이미지 참조를 유지하는 소비자 계약은 [상세 빌드·소비 절차](scripts/util/kubernetes-iso/README.ko.md)를 참고합니다.

## 공식 Release 승격

현재 공개 파일은 Origin 시험 산출물이며 공식 승격에는 다음 조건이 필요합니다.

1. 내부 SDK·Provider·AutoScaler의 Upstream PR/릴리즈를 완료하고 공식 source/image digest를 recipe에 반영합니다. Origin SDK 후보와 컴포넌트 source를 제거합니다.
2. minor별 stable AutoScaler를 확보하고 Provider LB/VPC·AutoScaler·노드 생명주기 실환경 검증을 완료합니다. recipe의 `runtime_qualification`에 `PASS`와 증거 URL을 기록합니다.
3. ISO 구현 및 recipe를 ISO 전용 Upstream `main`에 병합합니다. Mold 소비 변경의 최종 브랜치는 Cloud `ablestack-europa`입니다.
4. 병합된 source의 SHA를 포함한 고정 tag를 만들고 Upstream Actions에서 다시 빌드·검증·게시합니다. publisher가 저장소·tag·`upstream/main` ancestry 및 위 승격 조건을 검사합니다.

현재 recipe는 `runtime_qualification=pending`이고 1.37 AutoScaler는 개발 후보입니다. Origin assets를 공식 Release로 재명명하거나 이 게이트를 우회하지 않습니다.

## 자주 발생하는 문제

| 증상 | 확인 및 처리 |
| --- | --- |
| 기본 clone에 빌드 파일이 없음 | 현재 구현 브랜치 `codex/kubernetes-iso-1228` checkout |
| `missing build tool` / PyYAML import 오류 | OS 패키지·Go 설치, setup 스크립트 실행, PATH 확인 |
| `Release build requires committed source` | 추적 파일 변경을 commit하거나 Local 사전 확인에 `--development` 사용 |
| checksum·서명·digest 검증 실패 | 다운로드 상태와 고정 recipe를 조사하고 해당 검증 실패를 해결한 뒤 재시도 |
| `immutable output already exists` / `immutable Release already exists` | 기존 검증 산출물 사용 또는 새 revision/출력 디렉터리 선택 |
| `source HEAD mismatch` | 빌드한 commit과 게시하는 checkout의 HEAD 일치 여부 확인 |
| 수동 실행 버튼이 없음 | 기본 브랜치의 workflow와 `workflow_dispatch` 설정 확인 |
| Mold 다운로드에서 302 거부 | 영구 URL 사용 및 다운로드 중 `store.download.follow.redirects=true` 확인 |
| 공식 게시의 qualification/component gate 실패 | stable 원본·공식 컴포넌트·실환경 PASS·Upstream main 병합 조건 충족 후 재빌드 |

상세 구현 계약은 [scripts/util/kubernetes-iso/README.ko.md](scripts/util/kubernetes-iso/README.ko.md), 실제 시험 결과는 [2026-10-06 검증 보고서](docs/validation/iso-registration-20261006.md)에 기록합니다.
