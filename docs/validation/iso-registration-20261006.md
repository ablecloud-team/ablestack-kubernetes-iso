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

# ISO 전용 저장소 생성·Release·31번 등록 검증 — 2026-10-06

## 소유권과 최종 경로

ISO Actions·recipe·builder·독립 validator·publisher를 Cloud에서 분리했습니다.

| 책임 | 저장소 / branch / PR |
|---|---|
| 공식 ISO source·Actions·Release | [ablecloud-team/ablestack-kubernetes-iso](https://github.com/ablecloud-team/ablestack-kubernetes-iso) / `main` / [PR #1](https://github.com/ablecloud-team/ablestack-kubernetes-iso/pull/1) |
| Local·Origin ISO 시험 및 공개 trial Release | [dhslove/ablestack-kubernetes-iso](https://github.com/dhslove/ablestack-kubernetes-iso) / `codex/kubernetes-iso-1228` |
| Mold ISO 소비·설치/확장/업그레이드·CIDR API | [Cloud PR #1229](https://github.com/ablecloud-team/ablestack-cloud/pull/1229) / `ablestack-europa` |
| 내부 SDK·Provider·AutoScaler source/image | [SDK #3](https://github.com/ablecloud-team/ablestack-mold-go/pull/3), [Provider #2](https://github.com/ablecloud-team/ablestack-kubernetes-provider/pull/2), [AutoScaler #3](https://github.com/ablecloud-team/autoscaler/pull/3) |

새 ISO 전용 두 저장소는 public이며 default branch는 main입니다. Cloud 제품 branch는 Europa를 유지합니다. Cloud에는 ISO workflow/recipe/publisher를 남기지 않았고 기존 스크립트는 전용 경로 안내 후 종료합니다. ISO workflow는 Cloud 전체 빌드를 호출하지 않습니다.

## 실제 빌드와 다운로드 결과

- producer repository: `dhslove/ablestack-kubernetes-iso`
- producer/recipe SHA: `f6b6cd6274e8be3c0a679c0bf622428bd7d111c0`
- [Origin run 37336050374](https://github.com/dhslove/ablestack-kubernetes-iso/actions/runs/37336050374): **6개 ISO 생성·독립 검증·공개 trial 게시·비로그인 full GET/hash 전부 성공**.
- profile `mold-cks`, `amd64`/Mold `x86_64`, revision r1. 모든 ISO가 2 GiB 미만입니다.
- 각 Release에 ISO·checksum·manifest·CycloneDX SBOM·validation·registration JSON·한글 notes가 존재합니다. Actions artifact 7일 보존과 공개 Release 영구 주소를 구분합니다.
- 보고서/NOTICE/ignore license 후속 commit은 producer/recipe를 변경하지 않습니다. PR head와 ISO producer SHA를 구분해 기록합니다.

| Kubernetes | 공개 ISO / Release | bytes | Origin 검사 | 31번 |
|---|---|---:|---|---|
| 1.34.2 | [ISO](https://github.com/dhslove/ablestack-kubernetes-iso/releases/download/k8s-v1.34.2-mold-cks-amd64-r1-f6b6cd62/kubernetes-v1.34.2-mold-cks-amd64-r1-f6b6cd62.iso) · [Release](https://github.com/dhslove/ablestack-kubernetes-iso/releases/tag/k8s-v1.34.2-mold-cks-amd64-r1-f6b6cd62) | 827795456 | PASS | 100% Ready / 실파일 SHA256 일치 |
| 1.34.9 | [ISO](https://github.com/dhslove/ablestack-kubernetes-iso/releases/download/k8s-v1.34.9-mold-cks-amd64-r1-f6b6cd62/kubernetes-v1.34.9-mold-cks-amd64-r1-f6b6cd62.iso) · [Release](https://github.com/dhslove/ablestack-kubernetes-iso/releases/tag/k8s-v1.34.9-mold-cks-amd64-r1-f6b6cd62) | 828563456 | PASS | 100% Ready / 실파일 SHA256 일치 |
| 1.34.12 | [ISO](https://github.com/dhslove/ablestack-kubernetes-iso/releases/download/k8s-v1.34.12-mold-cks-amd64-r1-f6b6cd62/kubernetes-v1.34.12-mold-cks-amd64-r1-f6b6cd62.iso) · [Release](https://github.com/dhslove/ablestack-kubernetes-iso/releases/tag/k8s-v1.34.12-mold-cks-amd64-r1-f6b6cd62) | 832880640 | PASS | 100% Ready / 실파일 SHA256 일치 |
| 1.35.9 | [ISO](https://github.com/dhslove/ablestack-kubernetes-iso/releases/download/k8s-v1.35.9-mold-cks-amd64-r1-f6b6cd62/kubernetes-v1.35.9-mold-cks-amd64-r1-f6b6cd62.iso) · [Release](https://github.com/dhslove/ablestack-kubernetes-iso/releases/tag/k8s-v1.35.9-mold-cks-amd64-r1-f6b6cd62) | 826480640 | PASS | 100% Ready / 실파일 SHA256 일치 |
| 1.36.5 | [ISO](https://github.com/dhslove/ablestack-kubernetes-iso/releases/download/k8s-v1.36.5-mold-cks-amd64-r1-f6b6cd62/kubernetes-v1.36.5-mold-cks-amd64-r1-f6b6cd62.iso) · [Release](https://github.com/dhslove/ablestack-kubernetes-iso/releases/tag/k8s-v1.36.5-mold-cks-amd64-r1-f6b6cd62) | 840015872 | PASS | 100% Ready / 실파일 SHA256 일치 |
| 1.37.1 | [ISO](https://github.com/dhslove/ablestack-kubernetes-iso/releases/download/k8s-v1.37.1-mold-cks-amd64-r1-f6b6cd62/kubernetes-v1.37.1-mold-cks-amd64-r1-f6b6cd62.iso) · [Release](https://github.com/dhslove/ablestack-kubernetes-iso/releases/tag/k8s-v1.37.1-mold-cks-amd64-r1-f6b6cd62) | 848939008 | PASS | 100% Ready / 실파일 SHA256 일치 |

### Origin 및 31번 실파일 SHA256

| 버전 | SHA256 |
|---|---|
| 1.34.2 | `314dc1720be2921adf9cfd71190af4992eff899146b5ba2226d1cfa0137bc846` |
| 1.34.9 | `41a9616f22b0bce53db9dbba74e81bb6b93a9632702869776cd5b6e51a031744` |
| 1.34.12 | `6df3473ee30509b6f50dc5afcf8e9202435ee209e5dcbe7c15bed3be3a2210ad` |
| 1.35.9 | `00bfb9f41a0618ec8da5551f3e66a9eb6b11cb89ec2b7747b606a69d4a24075c` |
| 1.36.5 | `026e803df12c8a7c9003a03d983895e7e1f3dcae4701ee3904adf16b3685a5e6` |
| 1.37.1 | `989b09d889d2b633dd338235ae1c69a70ebcc768d454b15e9a5206773cafd96a` |

### 현재 31번 등록 식별자

| 버전 | supported-version UUID | ISO UUID |
|---|---|---|
| 1.34.2 | `f62ac063-1b9d-43ea-af7a-7c6354c56f27` | `2dc1db29-9741-4ee4-bcc5-0427d8421954` |
| 1.34.9 | `b7cdc646-7f75-4d54-83f4-34008439434c` | `48c7f40b-a037-4fcf-bdbf-d99be7fa3d4a` |
| 1.34.12 | `5aed7e49-faba-4c1f-ac7b-d4fa38b237e0` | `8ce0ecf3-5fa4-4998-8efe-813ddc025fdd` |
| 1.35.9 | `902e0c83-e34f-43d8-929d-1873225fb70e` | `4f432f0f-25e5-4127-b4a4-9864af908928` |
| 1.36.5 | `f72ebfca-8868-47be-8090-4a3521b69d72` | `4b6580f0-749b-43c3-a05a-c01ffd1b4a21` |
| 1.37.1 | `2415d0c6-66aa-4d95-bed9-67de0dbf2310` | `d73cffab-2d04-4425-9ffd-cfb42a531c6d` |

## Local 및 독립 검사 범위

추가 요청한 4개도 새 전용 저장소의 동일 f6b6cd62 소스로 WSL ext4에서 직접 빌드하고 독립 검증을 통과했습니다.

| 추가 버전 | Local ISO SHA256 |
|---|---|
| 1.34.12 | `25a7f6ea0469520da8df0263c78dd05522b73723485ec922a6c3a5ea590d1f13` |
| 1.35.9 | `96c62277049778e93f43b007d421cb0f571ab649fac03326e4a97336f9870476` |
| 1.36.5 | `9d3a021f9c6f698af5a92c2ab3dda247e5a0fa0c4bfc528fcee7e5f830e7001d` |
| 1.37.1 | `ae48709801e820984f597d420f6e00b0736c4ee6396873b9b98fd5ff8b020377` |

ISO를 staging과 별도로 재추출하여 필수 payload/checksum, 실제 kubeadm/kubelet/kubectl 버전·amd64 ELF 및 공식 keyless 서명, CNI/crictl/etcd, Kubernetes YAML, OCI manifest/config/compressed·uncompressed layer hash, 실제 포함 Go binary source/SDK를 검사했습니다. 격리 containerd 1.7.28에 모든 archive를 import하여 kubeadm tag와 digest 참조를 확인했습니다. workload를 실행한 검증은 아닙니다.

Local xorriso 1.5.4와 Origin 1.5.6 및 OCI archive envelope의 차이로 ISO hash는 채널 사이에 다릅니다. 공식 바이너리·image blob digest·source/recipe는 고정하지만 cross-toolchain 바이트 동일성을 선언하지 않습니다. 분리 전 동일 Local 도구/cache의 1.37.1 반복 빌드는 동일 hash를 확인했으며 [이전 검증 이력](cloud-origin-before-extraction-20261006.md)에 남겼습니다.

recipe/거부 계약 11개·actionlint·shell/Python 검사가 통과했습니다. 분리 전 실제 변조 ISO를 checksum 단계에서 거부했고 6개 실제 kubeadm으로 external-etcd config를 검증했습니다. 새 recipe의 바이너리와 image digest는 이전 검증 구성과 동일합니다. 1.31 이상 kubeadm v1beta4·실제 Kubernetes version·unix CRI endpoint 규칙을 소비 코드에 반영했습니다.

## Provider·AutoScaler 및 Mold SHA256

Provider는 Apache main `2a46b8e43382bbd1564db7a9bfa56f9caa872d13`의 최신 VPC ACL/CIDR·ProxyProtocol/fixed IP 소유권/providerID·zone·region/pagination 변경과 내부 SHA256 SDK를 포함합니다. 내부 이미지 source `34fe8294cd8c2337fbf6934eb75e4684cf3a9d85`, [Origin 검사](https://github.com/dhslove/ablestack-kubernetes-provider/actions/runs/37329464966)가 성공했습니다.

SDK v2.19.1을 내부 module에 병합했고 ISO 후보 SDK tag `v2.19.2-mold-test.1`의 source는 `7f1863866bc605456eb15c52bcde214c9ad9240c`입니다. 후속 문서/test license 보완의 SDK PR head는 `049fcf9`이며 client 구현은 동일합니다. [Origin contract](https://github.com/dhslove/ablestack-mold-go/actions/runs/37320794073) 및 [Upstream RAT 보완 검사](https://github.com/ablecloud-team/ablestack-mold-go/actions/runs/37336051006)가 성공했습니다.

AutoScaler는 내부 patch `b297d2ed89f67ea66da4dcde67abeade971fea01`을 각 minor의 전체 원본 checkout에 적용합니다. [4개 minor Origin 빌드](https://github.com/dhslove/autoscaler/actions/runs/37329451678)와 [Verify Go](https://github.com/dhslove/autoscaler/actions/runs/37329451460)가 성공했습니다.

| Kubernetes minor | AutoScaler 원본 | 원본 binary source SHA | 구분 |
|---|---|---|---|
| 1.34 | 1.34.5 | `cb2123ed13148c38fbdb1ede42d8e99761ee2909` | stable 원본 + 내부 패치 |
| 1.35 | 1.35.2 | `2d42588803c71fe9b35dcd9e3669ac6bb550ca22` | stable 원본 + 내부 패치 |
| 1.36 | 1.36.1 | `35e8a280425c76a4040f57ae0fa232a952c02024` | stable 원본 + 내부 패치 |
| 1.37 | 고정 development main | `22575f5c8af3edd9a10ca10d7d9edef68d2982cd` | stable 미확보 / 공식 게시 금지 |

1.37.1은 ISO 생성·등록 PASS인 **개발 시험 후보**이며 31번 이름에 DEV를 포함했습니다. stable AutoScaler 및 minor별 실제 runtime qualification을 확보해야 공식 지원/공식 Release로 승격할 수 있습니다.

SDK와 AutoScaler의 별도 client에 Java 값 인코딩·정렬/소문자 canonicalization·HMAC-SHA256 공통 vector를 적용했습니다. SDK GET/POST·만료와 AutoScaler 잘못된 map/list/async 응답 처리를 검사했습니다. 31번 실제 SDK capabilities/CKS 조회·제한 권한·A/B 키 회전/폐기·만료 및 SHA1 거부, AutoScaler 실제 조회/폐기 키 거부를 확인했습니다. 시험 키는 폐기했고 비밀 값은 공개 파일/ISO에 포함하지 않습니다.

각 recipe/manifest에는 실제 source/SDK/build run/image digest가 있습니다. AS binary baseline SHA와 내부 patch SHA/client 파일 hash를 분리하고 Go metadata가 없으면 게시를 거부합니다. 원본 stock SHA1 이미지/manifest fallback을 제거했으며 CSI는 별도 SHA256 감사 전 기본 profile에서 제외합니다.

## 31번 URL 전환과 보존

분리 전 Cloud trial에서 이 작업이 만든 ISO 6개만 API/async 삭제 완료 후 새 전용 저장소의 영구 URL로 다시 등록했습니다. 해당 ISO를 참조하는 활성 클러스터가 없음을 먼저 확인했습니다. 기존 사용자 ISO 3개(1.34.2, 1.35.9, 1.35.10)의 UUID·Enabled/Ready 메타데이터는 그대로 보존했습니다. 최종 supported-version 수는 **9개**입니다.

새 6개 모두 API Ready/100%, DB `DOWNLOADED`/Ready와 `/nfs/secondary`의 실제 파일 SHA256이 공개 Release와 일치합니다. 관리 `mold` active 및 `/client/` HTTP 200을 확인했습니다. 등록 CPU 2/RAM 2048 MiB는 API 최소값이며 실제 노드 offering sizing 검증을 뜻하지 않습니다.

GitHub permanent ISO URL은 HTTP 302를 사용합니다. 기존 동적 전역 설정 `store.download.follow.redirects`를 기존 false에서 다운로드 동안 true로 변경했고 6개 Ready 후 **false로 복원·재조회**했습니다. 향후 등록에도 다운로드 기간 동안 이 전제조건을 적용하거나 redirect 없는 검증 mirror를 사용합니다. 이 옵션이 전체 store 다운로드에 적용된다는 점을 운영 정책에 반영합니다.

Cloud에 남아 있는 이전 trial Release assets는 검증 이력으로 보존하고 신규 게시 경로를 안내합니다. 기존 ISO/tag/asset을 덮어쓰거나 source를 재명명하지 않았습니다.

## Cloud 검사 및 미완료 게이트

Cloud WSL ext4에서 변경 api/schema/server/kubernetes-service 모듈을 빌드하고 LB CIDR rollback 포함 18개 회귀를 통과했습니다. 최종 Cloud 코드의 후속 변경은 pipeline 분리·안내 문서이며 기능 변경은 없습니다. 전체 Cloud 빌드 완료 결과는 없고 PR에서 자동 시작된 Build는 취소했습니다. JAR/UI 배포는 수행하지 않았습니다.

Cloud의 전체 Lint/License check에는 기존 전체 저장소의 header/line-ending/spelling 및 third-party license text 6개 문제가 남아 있습니다. 새 Cloud 보고서의 canonical header는 보완했습니다. 독립 ISO 저장소의 RAT 검사는 미승인 license 0이며 새 SDK RAT도 통과했습니다. 전체 Cloud CI가 모두 green이라고 표시하지 않습니다.

실제 Service LB/VPC, pending Pod 기반 scale-up/down·PDB/quota/수동 충돌, 설치/확장/업그레이드/삭제 및 실제 Pod credential rotation은 아직 완료하지 않았습니다. `runtime_qualification`은 pending입니다. 원본 AS의 zero-size/autoprovisioning/강제 노드 삭제 stub을 지원으로 표시하지 않습니다.

공식 승격 순서는 SDK Upstream 릴리즈 → Provider candidate replacement 제거/공식 빌드 → Provider·AS 공식 source/image → recipe 및 Cloud Europa 소비 변경 병합 → minor별 runtime PASS/증거 확보 → ISO 전용 Upstream main 병합 source의 tag Release입니다. publisher는 Origin component source/SDK·development AS·runtime pending 및 잘못된 repo/tag/main ancestry를 차단합니다. #1228/#1227은 OPEN으로 유지합니다.
