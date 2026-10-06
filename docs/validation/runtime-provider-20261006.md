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
- 아래 6종 모두 Ready이며, 이전 등록 27개를 유지하여 당시 카탈로그는 33개였습니다. 등록 중 임시 변경한 store.download.follow.redirects는 원래 값 false로 복구했습니다.

| Kubernetes | SupportedVersion ID | ISO ID | Origin/Secondary SHA256 |
|---|---|---|---|
| 1.34.2 | 22ea0ad7-486a-4521-95f3-e88baad433b5 | c8241590-34ec-4e5a-aec4-23f7449e01e6 | 6c5f4f280143c8afd9af7a0f36a499e26538c318a34c1d2e2a3c2acdb10197fa |
| 1.34.9 | 4afd0d74-61e6-4031-b819-5e641a9fbc42 | fb7b9551-4507-42c3-b320-76df2751e339 | c7b888ebd6f7c993e404057db3f9057958abfb6e9b4f1197d9dd122a283deea2 |
| 1.34.12 | 3f95f819-1ca9-4757-af0a-c4f7ca00e0a7 | fe6a5f0b-fb44-4560-be33-3483e5540d88 | cd2918708be9b690f488925bb6adcd0abcb41476639e3b432f34321c902a3162 |
| 1.35.9 | ef34ec05-4573-49a4-9251-098e698c4698 | 323101ad-dc68-47da-ad5a-a2b4063f1d7b | 6992d335ccc082b246972924abf80dd94ecda993a91c6b6a5317faf91b88a370 |
| 1.36.5 | 66b16daf-7c48-47ec-8d70-be21a0911412 | 571e02e9-31d1-4430-b938-4966c6eb6354 | 46addbecf974040cc5255e18ddfc7971ffeaf3a87738ac553d419e8c460f8a90 |
| 1.37.1 | 786f1b55-4fc3-4a8f-81a8-93946edba6bd | 9625eb09-dcf6-49fe-b2b7-38c4e5c6c63a | 89ef16690abff52360c4ce2c9a3b972fe95ce951197d46de4c35b8c9af82b781 |

1.37.1은 DEV 시험 후보입니다. 이는 Origin 시험 산출물이며 Upstream 최종 Release/병합 완료가 아닙니다. Local/Origin ISO는 각각 검증을 통과했으나 ISO 해시가 서로 달라 비트 단위 재현성은 주장하지 않습니다. 현재 r9는 기존 6b ISO로 생성 후 Provider를 별도 패치한 진단 시험이므로, 이 새 ISO로 생성한 클러스터의 전 생명주기 PASS와 구분합니다. #1260 lifecycle/SDK 수정은 이 4a 후보에 아직 포함되지 않았습니다.

## 최신 후보 #1260: 실제 워커 복구와 6종 빌드·등록 완료

- ISO producer는 b46a588562b7504af96d3d2467dafcc0dad5b764입니다. 이후 문서 커밋은 ISO producer가 아닙니다.
- Provider 제품 코드605d3f61cad1a164079c86c7a1df2e4cbd51a9b3, SDK v2.19.2-mold-test.2/77401eb09d9fbfb3ec31b13bf66ea6c7bacbc74f를 고정합니다. Provider 후속6e93401은 HTTP 테스트 fixture의 오류 검사만 추가했으며 제품 코드/본 ISO 후보를 변경하지 않습니다.
- Provider Origin 이미지 ghcr.io/dhslove/ablestack-kubernetes-provider@sha256:7e65497ab43e8058639981af7f8e1b43dd0df142723c1df3cb72b8f501eee029 및 실제 r9 실행 바이너리 SHA256 5283c78b6215f1b52b2e4a0085c2c332d8bff39b3c1fceaf0911a141f45abbfc를 대조했습니다. Provider Local lifecycle/race 및 Origin37425756198/37425756306 성공, SDK Local/Origin contract와 Upstream RAT/build 성공입니다. 최신 Provider PR에서 실행된 lint/build/CodeQL은 성공했고 일부 build/e2e는 SKIPPED입니다.
- GFS2 전용 worker195만 Mold 한국어 UI에서 일반 정지→시작했습니다. 실제 Stopped 확인 후 shutdown taint를 붙이고 동일 Node UID/native providerID를 보존했습니다. 재기동 Ready/taint 제거, machine-id/DBus ID/systemUUID/SSH fingerprint 동일, 같은 ROOT UUID/Ready/GFS2 및 앱65/65·DB/파일 체크섬 복구를 확인했습니다. CCM의 해당 lifecycle/unimplemented 오류는 새 Pod 로그에서0건입니다. [실행 기록](https://github.com/ablecloud-team/ablestack-cloud/issues/1260#issuecomment-6011219376).
- drain 없는 VM 정지 구간의 외부 LB 관측은 10분5,689건/오류226건(timeout16/RemoteDisconnected210)입니다. [#1263](https://github.com/ablecloud-team/ablestack-cloud/issues/1263)에 계획 정지/drain/PDB/LB 제외와 복구 기준 개선을 등록했으며 무중단 PASS로 표시하지 않습니다. 위 db79 native AS25분 오류0과 별개의 실행입니다.
- Origin Actions37426687628의6종 build/publish 및 WSL ext4 Local6종 실제 생성/독립 검증이 성공했습니다. Local 첫 실행의 containerd runtime 디렉터리 준비 오류는 보존했고 실행 환경 준비 후 전 버전을 다시 빌드·검증했습니다. 인증 없는 전체 GET과 Secondary 실제파일 hash/바이트 대조6/6, 이전33개 유지/총39개 Ready 등록, redirects=false 복구를 확인했습니다. [등록/실파일 증거](https://github.com/ablecloud-team/ablestack-cloud/issues/1230#issuecomment-6011396975).

| Kubernetes | SupportedVersion ID | ISO ID | Origin/Secondary SHA256 |
|---|---|---|---|
| 1.34.2 | 4336320f-c4e2-4db5-b196-6b72d0525ec2 | 85dc88f4-1c46-41b5-8ff2-a6e762be42b0 | 0b6a204252317915f55cddc467288364c7e33485a86d831aab690bfac02f7eff |
| 1.34.9 | de179e30-a8d3-4fc7-9c1c-784882d80413 | 2692f9f2-c341-4695-ba21-38605a130783 | 2b2cdbff66314e8321bc0e68c0da9d5195964ae78c3ff4a3bf148d25c88f3915 |
| 1.34.12 | b9f72057-cb47-41dc-a7ea-0b026aff7bac | 17818cfe-82b9-4a23-972e-c4f8ff92ba56 | 6ad28d83dac39fdccf4386bac16c608813deb2e20f2cf1a77877b608a0b10cec |
| 1.35.9 | 43e027b4-0455-4155-8b86-323e99f7c30a | 1007880c-108d-498b-94db-5510d17a6ca9 | 34178caefea7f1c6eeb8d1d82552c4214a177433b0b9ccc34bc05bf1bbc34ac8 |
| 1.36.5 | 2cbf95a1-4a1c-4a40-be05-98345506d838 | bd033f46-2af3-4a6d-885c-7fb1c83bcdfa | 8e514d081543eb2acf438bc93cbe93fa8f86d0140bac575954a7ea15a9748169 |
| 1.37.1 | b616ea0f-b1c8-4e4c-908b-74582589e1df | 82173094-cad8-496c-ac2a-6250424a74df | 5a5b3fb484f218c0a511ab6a7e33bdc50b0bad424a45bc1552d8380ece447776 |

Local/Origin 산출물은 각각 검증했으나 서로 해시가 달라 비트 재현성을 주장하지 않습니다. 1.37.1은 DEV 후보입니다. 새 b46 ISO의 독립 clean cluster 반복, 전체 RT01–13/upgrade/HA/최종삭제, 대표24시간 및 DEV4시간은 미완료입니다. r9는 이전6b 설치 후 Provider를 별도 적용한 진단 시험이며 새 ISO 전체 qualification을 대체하지 않습니다. PR 병합과 공식 Upstream Release도 미완료입니다.

1.35.9 r8에서는 실제2시간/120회 관측·앱HTTP12,120건 오류0을 확인했습니다. 외부 LB 연속2시간은 포함하지 않으며 기존 template identity #1251·대표24시간은 남아 있습니다. [RT12 기록](https://github.com/ablecloud-team/ablestack-cloud/issues/1230#issuecomment-6011035465).
