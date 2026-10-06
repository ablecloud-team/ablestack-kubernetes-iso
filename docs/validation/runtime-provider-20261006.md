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

## 수정 후 단계 검증: 1.36.5 r9 native AS 2→3→2 및 LB 연속 접속

### 실제 실행과 결과
- Provider db79dec21bf76cc0f5082dfccbaf4e23376b75d3 / 이미지 e37041d0668e3448c9ac0c4de733e7352364e586a86368b6a08a351b94ed695a. 컨테이너에서 실제 실행 중인 cloudstack-ccm 바이너리 SHA256 182a7486a95ac42fd6a17814ede1fa42f956b02f981cc52d98e61674bc183c85를 Origin artifact와 대조했습니다.
- native 확장 job8347: 15:22:59→15:24:22 KST(83초) 성공, worker198 신규 생성. control1/worker3 모두 Ready/native providerID 확인, 실제 role template326/GFS2 ROOT238.
- CCM 15:24:22.462의 신규 NodePort 준비 검사 실패가 backend 추가를 보류했습니다. 직접 NodePort 첫 성공은 15:24:23.981이며, CCM 재시도 후 15:25:16.396에 backend3 적용 성공. 기존 healthy backend는 유지했습니다.
- min2/max3, 기본 10분 축소 대기 유지. 부하 제거 후 native 축소 job8351: 15:36:03→15:36:17 KST(14초) 성공. cluster Running/control1+worker2 Ready 및 LB backend2.
- 연속 외부 LB 관측 **15:22:22.131→15:47:22.221 KST / 실제 1500.089초 / 14,983 요청 / 오류0 / 최대 지연 7.864ms**. 수정 전 r9의 20분 11,967건/timeout1과 구분합니다.

### backend·자원·데이터 증거
- 기존 worker194/195 직접 NodePort 각각14,998건/오류0. 신규 worker198 직접 probe에는 준비 전22회 실패 및 축소 종료 경계1회 실패가 기록됐습니다. 이것을 외부 LB 오류로 합산하거나 숨기지 않습니다. 신규 backend first-success/실제 제거 시각과 구분했습니다.
- VM198 removed/Expunging, ROOT238 Expunged, cluster mapping 제거, SSH PF2225 제거. 세 compute host 모두 해당 domain 및 ROOT path 없음 확인.
- 축소 후 앱65/65 및 HTTP100/오류0, DB100건/파일64개(4MiB) 체크섬 유지. 다른 기본 노드/볼륨/앱 데이터는 보존됐습니다.
- 이 관측 창에서 외부 LB 접속 오류가 재현되지 않았습니다. TCP 연결 준비 검사이며 UDP와 애플리케이션 수준 readiness/PDB·모든 네트워크 토폴로지에 대한 무중단 보증은 아닙니다.

현재 r9는 6b ISO로 생성한 뒤 Origin Provider를 별도 적용한 진단 시험입니다. 신규 4a ISO clean 생성·버전별 반복 및 전체 RT01–13/upgrade/HA/최종삭제는 아직 완료 기준으로 남습니다. #1258은 해당 clean 반복 및 PR 병합 전 OPEN으로 유지합니다.


## 단계 기록: #1258 Provider 반영 ISO 6종 빌드 및 등록

- ISO Origin 커밋: 4a2c2f100dacc7bd81062198c57b832317ae07a9. Local 6종 실제 ISO 생성/독립 검증 및 Origin Actions 37422398502의 6종 빌드/게시가 모두 성공했습니다.
- Provider db79dec21bf76cc0f5082dfccbaf4e23376b75d3, 이미지 ghcr.io/dhslove/ablestack-kubernetes-provider@sha256:e37041d0668e3448c9ac0c4de733e7352364e586a86368b6a08a351b94ed695a에 신규 TCP NodePort 준비 확인이 포함됩니다.
- Origin 시험 Release에서 인증 없는 전체 ISO 다운로드를 실행한 뒤 SHA256/바이트 크기를 확인했습니다. Mold 등록 이후 Secondary 스토리지의 실제 ISO 파일도 같은 SHA256/크기로 대조하여 6/6 일치했습니다.
- 아래 6종 모두 Ready이며, 이전 등록 27개를 유지하여 현재 카탈로그는 33개입니다. 등록 중 임시 변경한 store.download.follow.redirects는 원래 값 false로 복구했습니다.

| Kubernetes | SupportedVersion ID | ISO ID | Origin/Secondary SHA256 |
|---|---|---|---|
| 1.34.2 | 22ea0ad7-486a-4521-95f3-e88baad433b5 | c8241590-34ec-4e5a-aec4-23f7449e01e6 | 6c5f4f280143c8afd9af7a0f36a499e26538c318a34c1d2e2a3c2acdb10197fa |
| 1.34.9 | 4afd0d74-61e6-4031-b819-5e641a9fbc42 | fb7b9551-4507-42c3-b320-76df2751e339 | c7b888ebd6f7c993e404057db3f9057958abfb6e9b4f1197d9dd122a283deea2 |
| 1.34.12 | 3f95f819-1ca9-4757-af0a-c4f7ca00e0a7 | fe6a5f0b-fb44-4560-be33-3483e5540d88 | cd2918708be9b690f488925bb6adcd0abcb41476639e3b432f34321c902a3162 |
| 1.35.9 | ef34ec05-4573-49a4-9251-098e698c4698 | 323101ad-dc68-47da-ad5a-a2b4063f1d7b | 6992d335ccc082b246972924abf80dd94ecda993a91c6b6a5317faf91b88a370 |
| 1.36.5 | 66b16daf-7c48-47ec-8d70-be21a0911412 | 571e02e9-31d1-4430-b938-4966c6eb6354 | 46addbecf974040cc5255e18ddfc7971ffeaf3a87738ac553d419e8c460f8a90 |
| 1.37.1 | 786f1b55-4fc3-4a8f-81a8-93946edba6bd | 9625eb09-dcf6-49fe-b2b7-38c4e5c6c63a | 89ef16690abff52360c4ce2c9a3b972fe95ce951197d46de4c35b8c9af82b781 |

1.37.1은 DEV 시험 후보입니다. 이는 Origin 시험 산출물이며 Upstream 최종 Release/병합 완료가 아닙니다. Local/Origin ISO는 각각 검증을 통과했으나 ISO 해시가 서로 달라 비트 단위 재현성은 주장하지 않습니다. 현재 r9는 기존 6b ISO로 생성 후 Provider를 별도 패치한 진단 시험이므로, 이 새 ISO로 생성한 클러스터의 전 생명주기 PASS와 구분합니다. #1260 lifecycle/SDK 수정은 이 4a 후보에 아직 포함되지 않았습니다.

## 후속 후보 #1260
본 커밋 recipe는 Provider 605d3f61cad1a164079c86c7a1df2e4cbd51a9b3 및 SDK 후보 v2.19.2-mold-test.2 (77401eb09d9fbfb3ec31b13bf66ea6c7bacbc74f)를 고정합니다. Provider Local lifecycle/전체 race 및 Origin Actions37425756198/37425756306 성공, 실제 r9 컨테이너 실행 바이너리도 Origin SHA256과 일치합니다.

위 25분 #1258 결과는 db79 Provider의 관측이며 새 lifecycle Provider 전체 PASS로 대체하지 않습니다. worker stop/recovery와 본 source의 새 ISO 빌드/등록/clean cluster qualification은 진행 중입니다. 공식 Upstream Release/병합은 미완료입니다.
