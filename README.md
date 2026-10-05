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

Mold Europa를 위한 버전별 Kubernetes 바이너리 ISO 전용 저장소입니다. Cloud 소스·RPM 빌드와 독립적으로 ISO를 생성·검증하고 공개 GitHub Release의 고정 주소로 배포합니다.

- 공식 저장소/최종 PR·Release: [ablecloud-team/ablestack-kubernetes-iso](https://github.com/ablecloud-team/ablestack-kubernetes-iso), 기본 브랜치 `main`
- Local/Actions 시험·trial Release: [dhslove/ablestack-kubernetes-iso](https://github.com/dhslove/ablestack-kubernetes-iso)
- Mold 소비자: `ablecloud-team/ablestack-cloud:ablestack-europa` / [Cloud PR #1229](https://github.com/ablecloud-team/ablestack-cloud/pull/1229)
- 설계/생명주기: [#1228](https://github.com/ablecloud-team/ablestack-cloud/issues/1228), [Epic #1227](https://github.com/ablecloud-team/ablestack-cloud/issues/1227)

지원 recipe: **1.34.2, 1.34.9, 1.34.12, 1.35.9, 1.36.5, 1.37.1**, `mold-cks`/amd64. 1.37용 AutoScaler는 stable 미확보 개발 후보이므로 공식 게시가 차단됩니다. ISO PASS와 실제 클러스터 런타임 지원은 별도 판정입니다.

[빌드·검증·배포 절차](scripts/util/kubernetes-iso/README.ko.md)를 따릅니다. GitHub ISO asset URL 등록 시 HTTP 302를 처리하려면 Mold의 기존 동적 설정 `store.download.follow.redirects=true`가 다운로드 중 필요합니다. checksum은 Release의 `registration.json`에 있는 `{SHA-256}` 값을 사용합니다.

Provider·SDK·AutoScaler는 각각 내부 저장소에서 유지하며 source/image digest·서명 계약·provenance를 recipe에 고정합니다. Origin trial과 공식 게시 권한/소스를 분리하고 공개 ISO/tag를 덮어쓰지 않습니다. Cloud 저장소의 기존 시험 Release는 이전 경로의 검증 이력이며 신규 ISO 게시 경로는 이 저장소입니다.
