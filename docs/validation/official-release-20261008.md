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

# 기본 ISO 공식 릴리즈 승격 — 2026-10-08

기본 `mold-cks` ISO 6종: 1.34.2, 1.34.9, 1.34.12, 1.35.9, 1.36.5, 1.37.1. 공식 producer는 `ablecloud-team/ablestack-kubernetes-iso/main`, 소비 branch는 Mold `ablestack-europa`다. 선택형 CSI qualification은 별도 pending 상태로 유지한다.

## 실제 빌드/게시 출처

- SDK 공식 [v2.19.2-mold.1](https://github.com/ablecloud-team/ablestack-mold-go/releases/tag/v2.19.2-mold.1), source `06c94ac6637fe03b795cef10ba1afde1d1e8ef8c`.
- Provider 공식 [릴리즈](https://github.com/ablecloud-team/ablestack-kubernetes-provider/releases/tag/mold-v1.2.1-r1-5dee69546c4e), source `5dee69546c4e1eeee5828c126b5282c603384f4a`, 실제 [빌드](https://github.com/dhslove/ablestack-kubernetes-provider/actions/runs/37652039471). 공식 SDK 모듈을 링크했고 candidate replace가 없다.
- AutoScaler 4개 minor의 기존 검증 image/binary/assets를 동일 checksum으로 공식 Release에 승격한다. 1.37.1 Mold production/PASS 판정도 유지한다. 원본 개발 commit의 provenance는 그대로 보존한다.
- image digest, source SHA, manifest SHA, SDK source/version, 공식 component Release asset URL/hash를 recipe에 함께 고정한다. `build_source_repository`와 provenance의 Origin build_run은 실제 빌드 출처를 보존한다.

## 실환경 qualification의 적용 경계

[기존 31번 GFS2 실행 증거](https://github.com/ablecloud-team/ablestack-cloud/blob/c169d9a203f49ce07e038297873bc3c24cd8ffb4/docs/operations/kubernetes-lifecycle/qualification-20261007.md)와 [공식 승격 증거](https://github.com/ablecloud-team/ablestack-cloud/issues/1228#issuecomment-6042200472)를 사용한다. Provider의 실검증 source `95e66eaff4d17f0e072f019e9c82c196ec10980e`에서 변경된 파일은 `go.mod/go.sum`뿐이다. SDK의 실검증 source `25574a288d86e638c058721c919bb43e33c4485f`와 공식 SDK source의 tracked tree 내용 차이는0이다. Provider Go 구현/Dockerfile/배치 manifest를 변경하지 않았다.

**공식 SDK 신규 빌드/race 계약 검사 + 구현 내용 동일성 + 기존 실환경 증거**로 적용한다. 새 바이너리를 각 장기 클러스터에 교체해 fresh runtime 시험한 것으로 확대하지 않는다. AutoScaler image/바이너리는 실검증과 동일하다. 기본 recipe runtime qualification에 patch/architecture, Provider/AutoScaler source/image, SDK source를 잠그고 publisher가 확인한다. 다른 버전/source/image/SDK에 이 판정을 재사용하면 게시가 거부된다.

## 게시 절차와 검증

`release-iso.yml`의 `version=all`은6개 기본 ISO가 모두 독립 검증 PASS를 얻은 뒤 게시한다. 같은 producer source의 여러 버전 tag는 각각 정확한 ref/commit으로 검사한다. component source의 공식 branch ancestry, 공식 component Release tag/source, 공식 SDK tag/source 및 위 코드 내용 동일성을 게시 시 재확인한다. 개발 산출물·기존 공개 Release 교체·candidate SDK·pending CSI는 허용하지 않는다. 게시 후 인증 없는 전체 ISO GET과 실제 SHA256을 확인한다.

공식 ISO download URL과 SHA256은 게시한 각 Release의 registration.json/SHA256SUMS와 #1228 완료 댓글에 기록한다. 기존 등록 ISO와 장기 클러스터는 변경하지 않는다.

- AutoScaler 1.34: [공식 릴리즈](https://github.com/ablecloud-team/autoscaler/releases/tag/mold-k8s1.34-r1-2132862adc75) / `ghcr.io/dhslove/autoscaler@sha256:83e1337f0c0f1bb0fdf6fab91fcacbb98c98ebc1b5667eb8a72c1cd0b73b8e87`

- AutoScaler 1.35: [공식 릴리즈](https://github.com/ablecloud-team/autoscaler/releases/tag/mold-k8s1.35-r1-2132862adc75) / `ghcr.io/dhslove/autoscaler@sha256:b701271bc2fa9c30fb7673cb57cbad0a5d5eb721243393aeb4ac3607987388e8`

- AutoScaler 1.36: [공식 릴리즈](https://github.com/ablecloud-team/autoscaler/releases/tag/mold-k8s1.36-r1-2132862adc75) / `ghcr.io/dhslove/autoscaler@sha256:77e1cd39911063d6a55a5c8d99e548f6185fa312d09c9d33fa923ebf19e4a316`

- AutoScaler 1.37: [공식 릴리즈](https://github.com/ablecloud-team/autoscaler/releases/tag/mold-k8s1.37-r1-2132862adc75) / `ghcr.io/dhslove/autoscaler@sha256:c6fa3f28db3f6f7fa0b4ad0b3bc23c1a3a69f8d7643913d9bdbacde7d8e0c6d7`
