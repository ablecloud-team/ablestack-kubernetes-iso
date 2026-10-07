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

# Kubernetes 워커 계획 유지보수의 복구 준비 게이트

이 문서는 #1230/#1263/#1264의 31번 시험에서 얻은 운영 절차입니다. Cloud 제품의 자동 유지보수 기능 또는 모든 네트워크/CNI의 무중단 지원을 뜻하지 않습니다. 실제 관측 결과는 runtime-provider-20261006.md와 연결된 이슈의 단계 댓글을 기준으로 판단합니다.

## 준비 계약

기존 인증된 kubeconfig로 작업하며 해당 클러스터의 worker UUID/Node 이름과 데이터 보존 정책을 확인합니다. 한 번에 한 워커만 다룹니다. control/etcd, 공유 host 또는 관리 서버를 이 절차의 정지 대상으로 사용하지 않습니다.

- 복제 수와 남은 노드 capacity, 실제 서비스 endpoint를 확인하고 workload에 적합한 PDB를 적용합니다. 단일 Redis 등의 구성은 HA로 취급하지 않습니다. PDB를 강제 우회하거나 남은 수용량 부족을 숨기지 않습니다.
- AutoScaler가 유지보수 노드를 의도하지 않게 대체하지 않도록 기존 설정과 일시 중지/복원 계획을 기록합니다. 전용 시험에서는 AS deployment를 일시0으로 중지했으며 완료 후1로 복구했습니다.
- 대상 노드의 node.kubernetes.io/exclude-from-external-load-balancers label을 적용하고 Mold의 실제 LB backend 제외를 확인합니다. label 적용 응답만으로 cloud 적용 완료를 추정하지 않습니다.
- PDB를 존중하는 kubectl drain을 수행합니다. 시험에서는 --ignore-daemonsets와 명시적인 timeout을 사용했습니다. 성공과 남은 Pod의 소유권을 확인하기 전 VM을 정지하지 않습니다.
- 데이터/identity/볼륨 기준선과 외부 HTTP 관측을 확보한 뒤 Mold에서 해당 시험 worker만 일반 정지합니다.

Kubernetes의 [안전한 drain 절차](https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/)는 PDB를 존중하는 eviction과 drain 성공 이후 정지를 설명합니다. 그 절차의 완료와 아래 복구 준비 게이트를 각각 확인합니다.

## 복구와 서비스 복귀

1. Mold VM을 시작합니다. Node Ready여도 cordon과 LB 제외를 유지합니다.
2. 실제 CNI profile의 대상 노드 agent와 kube-proxy를 확인합니다. 이번 Calico profile은 calico-node/kube-proxy Pod Ready, Node NetworkUnavailable=False 및 재기동 후 새 container startedAt을 함께 확인했습니다. 과거 Ready condition을 새 실행의 준비 증거로 사용하지 않습니다.
3. 준비된 다른 노드에서 대상 노드 NodePort를 통한 실제 서비스 요청을 확인합니다. 이번 HTTP fixture에서는 다른 worker의 healthy Pod를 경유한 요청20건을 확인했습니다. TCP connect만으로 application/overlay의 전체 준비를 보장하지 않습니다.
4. 위 게이트가 통과하면 uncordon합니다. 필요한 workload replicas/readiness와 데이터 서비스를 확인하고 새 endpoint를 포함한 양쪽 worker의 실제 서비스 요청을 다시 확인합니다.
5. LB 제외 label을 제거하고 Mold의 실제 backend 복귀 및 외부 서비스를 확인합니다. AutoScaler와 임시 설정을 원래 상태로 복원하며 연속 관측과 데이터 검증을 마칩니다.

게이트 실패/timeout에는 cordon/LB 제외를 보존하고 실패 단계와 실제 상태를 기록합니다. 임의 대기로 결과를 바꾸거나 강제 VM 정지로 drain 실패를 우회하지 않습니다. custom CNI나 비HTTP 서비스에는 profile별 agent/readiness와 data path 검증이 필요합니다.

## 발견한 복귀 실패

첫 r9 계획 유지보수에서는 Node Ready16:52:48, 새 Web Pod Ready16:52:56이 Calico Ready16:53:35보다 먼저 관측됐습니다. Node Ready만으로 uncordon한 뒤 외부 HTTP timeout14건이 발생했습니다. Provider는16:52:57에 신규 NodePort timeout을 감지해 backend 추가를 보류했고 실제 추가는16:53:40에 성공했습니다. 실패 시간창은 새 backend 추가 이전이므로 이를 backend 오추가로 단정하지 않습니다.

이 실행과 복구 게이트를 적용한 다음 실행을 서로 다른 run으로 보존합니다. 실제6버전 clean 반복, upgrade/HA 및 전체 생명주기 qualification은 남아 있습니다. 제품 UI/API의 준비 계약 확대는 [#1264](https://github.com/ablecloud-team/ablestack-cloud/issues/1264)에서 추적합니다.
