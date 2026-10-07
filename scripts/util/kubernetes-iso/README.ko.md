<!--
 Licensed to the Apache Software Foundation (ASF) under one
 or more contributor license agreements.  See the NOTICE file
 distributed with this work for additional information
 regarding copyright ownership.  The ASF licenses this file
 to you under the Apache License, Version 2.0 (the
 "License"); you may not use this file except in compliance
 with the License.  You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing,
 software distributed under the License is distributed on an
 "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 KIND, either express or implied.  See the License for the
 specific language governing permissions and limitations
 under the License.
 -->

# Kubernetes ISO 빌드·검증 및 소비 계약

공식 저장소 `ablecloud-team/ablestack-kubernetes-iso:main`을 clone하거나 사용자 fork에서 실행합니다. clone/fork 동기화·Local 환경·Actions·다운로드·등록 방법은 [저장소 README](../../../README.md)를 따릅니다.

이 workflow는 Cloud 전체 Maven 빌드와 독립적으로 ISO를 생성합니다. 검증 profile은 `mold-cks` / `amd64`입니다. 아래 여섯 patch를 별도의 고정 recipe로 빌드합니다. arm64는 별도 검증 대상입니다.

| Kubernetes | AutoScaler baseline | Calico | 구분 |
| --- | --- | --- | --- |
| 1.34.2 / 1.34.9 / 1.34.12 | 1.34.5 | 3.32.2 | stable 원본 + 내부 패치 |
| 1.35.9 | 1.35.2 | 3.33.0 | stable 원본 + 내부 패치 |
| 1.36.5 | 1.36.1 | 3.33.0 | stable 원본 + 내부 패치 |
| 1.37.1 | 고정 1.37 commit | 3.33.0 | Mold 프로덕션 판정/실환경 PASS; 원본 출처는 development-candidate 보존 |

AutoScaler는 minor별 원본 인터페이스를 유지하면서 내부 SHA256 client를 적용합니다. 원본 SHA, 커스터마이징 SHA 및 파일 해시를 각각 기록합니다. 원본 고정 commit의 `development-candidate` 출처를 stable로 바꾸지 않습니다. 별도의 `features.autoscaler_qualification`에1.37.1의 Mold production/PASS 판정과 source·binary baseline·image digest·커스터마이징 해시·정확한 Kubernetes patch/minor·architecture·증거 URL을 기록합니다. [사용자 프로덕션 판정](https://github.com/ablecloud-team/ablestack-cloud/issues/1228#issuecomment-6038989411)은 정확히 검증한 빌드에 적용하며 source/digest 변경 시 재판정합니다.

## 생성 및 독립 검증

Linux ext4 작업 디렉터리에 curl, skopeo, xorriso, Python 3/PyYAML, Go 1.26.8을 준비합니다. 설치된 containerd 서비스는 사용하거나 변경하지 않습니다. containerd 1.7의 공통 런타임 디렉터리(`/run/containerd`, 0711)가 필요하며, 그 아래 daemon 상태는 공유하지 않습니다.

```bash
: "${GITHUB_REPOSITORY:?공식 clone 또는 자신의 fork owner/name을 설정하세요}"
scripts/util/kubernetes-iso/setup-tools.sh "$HOME/work/mold-iso-tools"
sudo install -d -m 0711 /run/containerd
export PATH="$HOME/work/mold-iso-tools:$HOME/work/mold-iso-tools/bin:$PATH"
python3 -m unittest discover -s scripts/util/kubernetes-iso/tests -v
scripts/util/create-kubernetes-binaries-iso.sh \
  --recipe scripts/util/kubernetes-iso/recipes/kubernetes-1.34.2-amd64.json \
  --output "$HOME/work/iso-output/1.34.2" --revision r1
```

Local 빌드 전에는 `GITHUB_REPOSITORY=ablecloud-team/ablestack-kubernetes-iso`(공식 clone) 또는 자신의 `<owner>/ablestack-kubernetes-iso`(fork)를 export합니다. 새 셸에서도 이 값을 다시 설정합니다. Actions는 실제 실행 저장소 값을 제공합니다. 이 값은 manifest/검증/등록 JSON의 producer 출처이며, Local builder의 시험 저장소 기본값에 의존하지 않습니다.

소스는 커밋한 상태여야 합니다. 로컬 개발용 `--development` 산출물은 Release 대상으로 사용할 수 없습니다. positional 인자 방식은 변동 가능한 다운로드와 호스트 containerd 변경을 유발했으므로 고정 recipe 방식으로 대체했습니다.

recipe에는 공식 다운로드 URL/SHA256, 매니페스트의 source commit, 실제 amd64 이미지 digest, 내부 Provider/AutoScaler/SDK의 source SHA와 Actions 출처가 들어갑니다. 빌드 중 `latest`/`main`/`master`를 조회하지 않습니다. Headlamp 원본 매니페스트의 이미지도 해당 버전의 실제 digest로 치환합니다. core image 목록은 해당 patch의 kubeadm 출력과 대조합니다.

ISO를 CDROM label로 생성한 뒤 staging 디렉터리를 버리고 별도 검증기가 ISO를 추출합니다. 모든 파일 해시, Kubernetes 실행 버전 및 공식 keyless 바이너리 서명, CNI/crictl/etcd ELF, Kubernetes YAML, OCI manifest/config/compressed-layer와 uncompressed-layer digest, 내부 바이너리의 Go source/SDK 정보를 확인합니다. 격리 containerd daemon에 전체 archive를 import하여 kubeadm tag와 매니페스트 digest 참조가 모두 유지되는지 검사합니다.

ISO 파일과 manifest, CycloneDX 구성 목록, 독립 검증 보고서, checksum, Mold 등록 JSON을 함께 출력합니다. 구성 목록은 배포 payload 목록이며 모든 컨테이너의 OS/전이 패키지를 분석한 취약점 보고서는 아닙니다.

## Actions 산출물 및 공식 Release

공식 저장소 또는 사용자 fork에서 `workflow_dispatch`의 `version`/`revision`을 지정하고 `publish=false`로 빌드·검증합니다. fork의 Actions를 활성화하고 기본 브랜치에 workflow를 준비해야 합니다. `kubernetes-<version>-amd64` artifact는 7일 보존됩니다. 일반 branch push의 자동 실행은 workflow branch/path 필터를 따릅니다.

trial 자동 게시와 publisher의 `origin-trial` 모드는 코드에 지정된 검증 저장소만 지원합니다. 임의 fork의 Release 자동 게시를 제공하는 옵션이 아니므로 일반 fork는 검증 artifact를 사용합니다.

Release tag는 `k8s-v<version>-mold-cks-amd64-<revision>-<source8>`입니다. 기존 tag/파일을 덮어쓰지 않으며 `latest` 및 `branch-dev`를 변경하지 않습니다. publisher는 게시 후 인증 없는 GET으로 ISO를 다시 받아 SHA256을 대조합니다.

Mold 등록의 checksum은 파일 SHA256의 hex에 `{SHA-256}` prefix를 붙입니다. manifest의 API `HMAC-SHA256`은 API 요청 인증 규칙이며 ISO 파일 checksum과 다른 항목입니다.

공식 Release는 **ISO 전용 Upstream 저장소의 `main`에 포함된 commit**의 전용 tag를 공식 저장소에 push할 때 실행합니다. Mold 소비 코드의 최종 대상은 Cloud `ablestack-europa`입니다. 시험 후보 컴포넌트를 공식 Release로 재명명하지 않습니다. SDK·Provider·AutoScaler Upstream PR을 병합·릴리즈한 뒤 동일한 검증 절차로 공식 source/image digest를 recipe에 반영해야 합니다. Provider/AutoScaler·노드 생명주기 실환경 검증을 완료하고 recipe의 `runtime_qualification`에 PASS와 증거 URL을 기록해야 공식 게시가 가능합니다. 전체 lifecycle/CSI qualification이 pending이거나 공식 컴포넌트 조건을 만족하지 않으면 공식 게시가 차단됩니다. AutoScaler 조건은 stable 원본 또는 정확한 빌드에 대한 Mold 프로덕션 판정으로 충족할 수 있습니다. 원본의 development-candidate 표기만으로1.37.1 공식 게시를 금지하지 않습니다.

## 소비자 계약과 검증 범위

root payload의 `provider.yaml`, `autoscaler.yaml`은 필수입니다. Provider는 내부 SDK의 SHA256 인증을 사용하며 AutoScaler는 자체 SHA256 client를 유지합니다. ISO의 `docker/images.list`를 확인하고 import에 `--digests --base-name <repository>`를 사용하여 실제 digest 주소가 보존되도록 합니다. 설치/확장의 내부 매니페스트를 배포하고 업그레이드는 Headlamp와 legacy Dashboard의 파일을 명시적으로 구분합니다. Secret 적용은 기존 Secret 갱신으로 APIKeyPair rotation을 지원합니다.

CSI는 데이터 볼륨 관리가 필요한 클러스터에서 선택하는 `mold-cks-csi` 전용 프로파일로 분리합니다. 내부 SHA256/GFS2 실환경 시험은 진행했으며 공식 component/SDK 승격·프로파일별 qualification/게시 단계는 기본 ISO와 별도입니다. 노드 ROOT의 GFS2 Primary 배치는 CSI 설치와 별개입니다. 설치 UI·StorageClass/PVC 및 데이터 보존 정책은 [CSI 사용 절차](../../../README.md#선택형-csi-iso-프로파일)를 따릅니다. AutoScaler 활성화는 선택이며 zero-size/autoprovisioning을 지원한다고 표시하지 않습니다. 실제 LB/VPC, 각 minor의 클러스터 생성/확장/축소/업그레이드 및 arm64, Headlamp 연결 UI(#1208)는 각 생명주기 이슈의 런타임 검증 대상입니다. ISO PASS를 전체 클러스터 생명주기 PASS로 해석하지 않습니다.

CNI 조합은 [Calico 3.32 요구사항](https://docs.tigera.io/calico/3.32/getting-started/kubernetes/requirements)과 [3.33 요구사항](https://docs.tigera.io/calico/latest/getting-started/kubernetes/requirements)의 시험 minor를 기준으로 선택합니다. 노드 커널 5.10 이상과 CNI 모듈/네트워크 준비는 클러스터 배포 전 확인해야 합니다.

GitHub ISO URL은 HTTP 302 redirect를 사용하므로 Mold의 기존 동적 전역 설정 `store.download.follow.redirects=true`가 다운로드 중 필요합니다. 기존 값을 기록하고 다운로드 완료 후 운영 정책에 맞게 복원합니다. 등록 Ready와 secondary 실파일 SHA256을 모두 확인합니다.

특정 시험 저장소의 Release 주소·producer SHA·31번 등록 결과는 [별도 검증 보고서](../../../docs/validation/iso-registration-20261006.md)에 기록합니다. 일반 clone/fork 사용법과 공식 Release 다운로드 주소는 저장소 README를 기준으로 합니다.
