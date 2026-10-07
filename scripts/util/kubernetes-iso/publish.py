#!/usr/bin/env python3
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
"""Publish validated assets once; never replace public Release assets."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from release_support import autoscaler_release_basis, validate_autoscaler_production_qualification, validate_runtime_qualification


def run(args):return subprocess.check_output(args,text=True).strip()


def verify_immutable_tag(source, tag):
 if run(['git','rev-parse','refs/tags/'+tag+'^{commit}'])!=source:raise ValueError('official immutable tag mismatch')


def api(path):
 return json.loads(run(['gh','api',path]))


def verify_official_components(manifest):
 """Bind promoted releases to merged sources and the actual official SDK tag."""
 for name,component in manifest['components'].items():
  repository=component['source_repository']
  default=api('repos/'+repository)['default_branch']
  comparison=api('repos/'+repository+'/compare/'+component['source_sha']+'...'+default)
  if comparison['behind_by'] != 0:raise ValueError('component source has not merged: '+name)
  artifact_repository=component.get('artifact_repository')
  artifact_tag=component.get('artifact_tag')
  if artifact_repository!=repository or not artifact_tag:raise ValueError('official component Release lock missing: '+name)
  release=api('repos/'+repository+'/releases/tags/'+artifact_tag)
  if release['draft'] or release['prerelease']:raise ValueError('component Release is not official: '+name)
  if api('repos/'+repository+'/commits/'+artifact_tag)['sha']!=component['source_sha']:raise ValueError('component Release source mismatch: '+name)
  sdk=component.get('sdk')
  if sdk:
   sdk_repo=sdk['module'].removeprefix('github.com/').removesuffix('/v2')
   if not sdk_repo.startswith('ablecloud-team/') or api('repos/'+sdk_repo+'/commits/'+sdk['version'])['sha']!=sdk['source_sha']:raise ValueError('official SDK tag source mismatch: '+name)
 # Promotion changes only dependency identities. The tested Provider/SDK code must match.
 q=manifest['features']['runtime_qualification']['provider_equivalence']
 comparison=api('repos/'+manifest['components']['provider']['source_repository']+'/compare/'+q['runtime_source_sha']+'...'+manifest['components']['provider']['source_sha'])
 if comparison.get('total_commits',0)>0 and (len(comparison.get('files',[]))>=300 or any(f['filename'] not in {'go.mod','go.sum'} for f in comparison['files'])):raise ValueError('Provider runtime source equivalence failed')
 sdk=manifest['components']['provider']['sdk']
 sdk_repo=sdk['module'].removeprefix('github.com/').removesuffix('/v2')
 if api('repos/'+sdk_repo+'/compare/'+q['runtime_sdk_source_sha']+'...'+sdk['source_sha']).get('files'):raise ValueError('SDK runtime source equivalence failed')



def registration_usage_notes(registration, manifest):
 """Explain display naming, Europa evidence and optional storage separately."""
 version=registration['kubernetesversion']
 name=registration['name']
 qualification=manifest['features'].get('runtime_qualification', {})
 evidence=qualification.get('evidence_urls', [])
 links='\n'.join('- '+url for url in evidence)
 csi=manifest['features'].get('csi', False)
 storage=('이 ISO에는 내부 HMAC-SHA256 CSI 드라이버·고정 sidecar 이미지·snapshot CRD가 포함됩니다. 설치를 요청하려면 클러스터 생성의 고급 설정에서 CSI 활성화를 선택합니다.' if csi else '이 ISO는 기본 `mold-cks` 프로파일이며 CSI 드라이버·sidecar·snapshot CRD를 포함하지 않습니다. CSI를 사용하려면 같은 Kubernetes 버전의 별도 `mold-cks-csi` ISO가 필요합니다. 이름에 csi를 넣거나 기본 ISO에서 CSI 활성화만 선택해도 CSI payload가 추가되지는 않습니다.')
 return f"""
## Mold 등록 이름과 입력

- **권장 이름 / name:** `{name}` — 함께 게시된 `registration.json.name`과 같은 값입니다.
- 이름은 목록에서 구분하는 표시 이름이므로 변경할 수 있습니다. Kubernetes 버전·프로파일을 이름에서 판별하지 않습니다. 실제 버전 입력은 **semanticversion=`{version}`**, 아키텍처는 **x86_64**이며 ISO 내용과 일치해야 합니다.
- Mold UI는 이름 입력이 필수입니다. URL 등록 API에서 이름을 생략하면 `v<semanticversion>` 또는 `v<semanticversion>-<Zone 이름>`이 자동 생성되지만 운영 등록에는 권장 이름을 직접 입력합니다.
- 등록 시 내부 ISO 이름에 `-Kubernetes-Binaries-ISO`가 붙습니다. 255자 이름 저장 한도를 고려해 입력 이름은231자 이내의 간결한 이름을 권장하며, 시스템 VM 예약 이름과 중복·혼동하는 이름은 피합니다. 권장 이름은 version/profile/arch/revision/source를 구분합니다.
- 같은 이름으로 등록해도 payload·버전·CSI 설정이 바뀌지 않습니다. 클러스터는 선택한 지원 버전 ID/UUID를 사용합니다. URL·checksum·minimum resources는 이 릴리즈와 registration.json의 값을 함께 사용합니다.

## Mold Europa 검증

대상 제품/소비 브랜치는 **Mold Europa / `ablecloud-team/ablestack-cloud:ablestack-europa`**입니다. 실환경 검증은 **31번 클러스터, KVM, amd64/x86_64, GFS2 Primary**에서 수행했습니다. 버전별 신규 배포·앱/데이터·Provider LB/VPC·minor별 AutoScaler 확대/축소 및 노드 생명주기 결과는 아래 qualification 증거에 연결됩니다.

- 이 ISO의 runtime qualification: **{qualification.get('status', 'pending')}** / `{qualification.get('method', '별도 판정')}`.
- 공식 기본6종은 ISO build·독립 추출/버전·ELF·공식 바이너리 서명·매니페스트·OCI digest·격리 containerd import와 공개 전체 ISO 다운로드/SHA256을 검증했습니다.
- 공식 SDK 신규 Provider 빌드는 race/계약 검사와 기존 실검증 구현 내용 동일성을 확인했습니다. AutoScaler는 실검증 image/binary digest를 유지했습니다. 기존 Europa 실환경 결과와 이번 공식 ISO 파일 검증을 연결하며, 이번 최종 ISO6개를 모두 새 클러스터에 다시 배포한 시험으로 확대하지 않습니다.

{links}

## CSI를 선택형 프로파일로 분리한 이유

CSI는 애플리케이션의 **PVC/PV 데이터 볼륨을 Mold API로 생성·연결·확장하고 snapshot/복원·삭제/Retain을 처리하는 스토리지 드라이버**입니다. 노드 VM의 ROOT 디스크를 GFS2 Primary에 배치하는 기능과 별개이므로, GFS2에서 Kubernetes 노드를 실행한다는 이유만으로 CSI 설치가 필요한 것은 아닙니다. 기본 클러스터 생성·CNI·Provider·AutoScaler 기능에는 CSI가 필수가 아닙니다.

CSI를 켜면 데이터 볼륨/snapshot API 권한, controller/node 드라이버·sidecar, StorageClass/disk offering과 데이터 보존/삭제 정책이 추가됩니다. 이를 명시적으로 선택하고 KVM/GFS2 데이터 생명주기를 별도로 검증하도록 프로파일을 분리했습니다. 단순 ISO 크기 절감이나 CSI 자체 미구현 때문이 아닙니다. 내부 HMAC-SHA256 CSI와 GFS2 실환경 시험은 진행했으며, **CSI의 공식 SDK/source 승격 및 프로파일별 공식 qualification/게시 조건은 기본 ISO와 별도**입니다.

{storage}

## CSI 사용 절차

1. **같은 patch 버전의 `mold-cks-csi` ISO를 별도 이름·URL·checksum으로 등록**합니다. CSI 공식 Release가 게시되기 전의 recipe/Origin trial 산출물은 시험용입니다. 공식 운영용 CSI ISO는 공식 승격/qualification 완료 뒤 게시된 CSI Release를 선택합니다.
2. Mold에서 새 Kubernetes 클러스터를 생성할 때 CSI ISO의 지원 버전 항목을 선택하고 **고급 설정 → CSI 활성화**(`enablecsi=true`)를 선택합니다. 검증된 Europa backend가 ISO의 내부 bundle/checksum/digest와 HMAC-SHA256 profile을 확인하고 controller/node 드라이버를 배포합니다. 실제 자격증명은 Mold가 관리하는 `kube-system/cloudstack-secret`을 사용하며 ISO/README에 넣지 않습니다.
3. **GFS2 Primary에 매칭되는 shared/custom disk offering의 실제 UUID**를 StorageClass에 지정합니다. CLVM/CLVM_NG를 선택하지 않습니다. StorageClass 이름만 GFS2로 정해도 저장소가 선택되지는 않습니다. 노드 ROOT 배치용 compute offering과 PVC 데이터용 disk offering을 각각 확인합니다.
4. 아래 StorageClass를 기반으로 PVC의 `storageClassName`을 지정하고 애플리케이션 Pod에 mount합니다. `WaitForFirstConsumer`는 Pod의 스케줄링을 기다리므로 PVC만 만들었을 때 Pending일 수 있습니다. 예시의 Retain은 PVC 삭제 후 데이터를 보존하며 운영자가 회수 절차를 관리합니다. Delete 정책은 실제 데이터 볼륨 삭제로 연결되므로 용도에 맞게 선택합니다.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: mold-gfs2-retain
provisioner: csi.cloudstack.apache.org
parameters:
  csi.cloudstack.apache.org/disk-offering-id: "<GFS2-Primary-shared-custom-disk-offering-UUID>"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Retain
```

5. `kubectl get csidrivers`, `kubectl -n kube-system get deployment cloudstack-csi-controller`, `kubectl -n kube-system get daemonset cloudstack-csi-node`와 PVC Bound/Pod mount를 확인합니다. 실제 Mold volume·GFS2 배치 및 데이터 쓰기/재연결/확장/snapshot 복원/Retain·Delete 결과를 함께 확인합니다. [CSI 사용 문서](https://github.com/ablecloud-team/ablestack-kubernetes-iso/blob/main/README.md#선택형-csi-iso-프로파일), [Kubernetes StorageClass](https://kubernetes.io/docs/concepts/storage/storage-classes/), [PV/PVC 및 reclaim policy](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)를 참고합니다.
"""


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--directory',type=Path,required=True)
 p.add_argument('--repository',required=True)
 p.add_argument('--mode',choices=['origin-trial','official'],required=True)
 args=p.parse_args()
 if args.mode=='origin-trial' and args.repository!='dhslove/ablestack-kubernetes-iso':raise ValueError('Origin trial repository mismatch')
 if args.mode=='official' and args.repository!='ablecloud-team/ablestack-kubernetes-iso':raise ValueError('official repository mismatch')
 isos=list(args.directory.glob('*.iso'))
 if len(isos)!=1:raise ValueError('publish exactly one ISO per immutable Release')
 iso=isos[0];name=iso.stem
 report=json.loads((args.directory/(name+'.validation.json')).read_text())
 registration_path=args.directory/(name+'.registration.json')
 registration=json.loads(registration_path.read_text())
 if not registration['release_eligible'] or report['status']!='PASS' or report['containerd_import']['status']!='PASS':raise ValueError('validation gate failed')
 if registration['source_repository'] != args.repository:raise ValueError('ISO producer repository mismatch')
 source=registration['source_sha']
 if source!=run(['git','rev-parse','HEAD']):raise ValueError('source HEAD mismatch')
 tag=name.replace('kubernetes-','k8s-',1)
 manifest=json.loads((args.directory/(name+'.manifest.json')).read_text())
 validate_autoscaler_production_qualification(manifest)
 if args.mode=='official':
  manifest=json.loads((args.directory/(name+'.manifest.json')).read_text())
  qualification=manifest['features'].get('runtime_qualification',{})
  if qualification.get('status')!='PASS' or not qualification.get('evidence_urls'):raise ValueError('official Release requires documented Provider/AutoScaler and node lifecycle runtime qualification')
  if manifest['features'].get('csi') and (manifest['features'].get('csi_qualification',{}).get('status') != 'PASS' or not manifest['features'].get('csi_qualification',{}).get('evidence_urls')):raise ValueError('official CSI Release requires minor-specific storage runtime qualification')
  autoscaler_release_basis(manifest)
  for component in manifest['components'].values():
   if not component['source_repository'].startswith('ablecloud-team/') or 'candidate_module' in component.get('sdk',{}):raise ValueError('official Release requires promoted Upstream component sources and SDK')
  validate_runtime_qualification(manifest)
  verify_official_components(manifest)
  verify_immutable_tag(source, tag)
  fetch=['git','fetch','upstream','main']
  if run(['git','rev-parse','--is-shallow-repository'])=='true':fetch.insert(2,'--unshallow')
  subprocess.run(fetch,check=True)
  subprocess.run(['git','merge-base','--is-ancestor',source,'upstream/main'],check=True)
 if subprocess.run(['gh','release','view',tag,'--repo',args.repository],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:raise ValueError('immutable Release already exists')
 url='https://github.com/'+args.repository+'/releases/download/'+tag+'/'+iso.name
 registration['download_url']=url
 registration_path.write_text(json.dumps(registration,indent=2)+'\n')
 manifest=json.loads((args.directory/(name+'.manifest.json')).read_text())
 autoscaler=manifest['components']['autoscaler']
 notes=args.directory/(name+'.notes.ko.md')
 notes.write_text(f'''# Kubernetes {registration['kubernetesversion']} Mold ISO

- 대상: Europa / x86_64 / Mold SHA256 Provider 및 {'.'.join(registration['kubernetesversion'].split('.')[:2])}용 AutoScaler
- 배포 구분: {args.mode}
- producer repository: `{args.repository}` / 공식 source branch: `main` / Mold 소비 branch: `ablestack-europa`
- source SHA: `{source}`
- AutoScaler baseline: `{autoscaler['original_baseline']}` / `{autoscaler['baseline_status']}` / `{autoscaler['binary_source_sha']}`
- Mold AutoScaler 지원 판정: `{manifest['features'].get('autoscaler_qualification', {}).get('support_level', 'runtime qualification 참조')}` / `{manifest['features'].get('autoscaler_qualification', {}).get('status', '별도 판정 없음')}`
- ISO 독립 추출·버전·ELF·공식 바이너리 서명·매니페스트·OCI blob·격리 containerd import: PASS
- Mold URL 등록 주소: {url}
- Mold checksum: `{registration['checksum']}`
- GitHub asset URL의 HTTP 302 다운로드에는 Mold의 `store.download.follow.redirects=true`가 다운로드 중 필요합니다. 기존 값을 기록하고 다운로드 완료 후 운영 정책에 맞게 복원합니다.
- CSI: {'내부 SHA256 GFS2 KVM opt-in 프로파일; 고정 이미지 8개 포함, 해당 minor 런타임 시험 별도' if manifest['features'].get('csi') else '기본 프로파일에는 포함하지 않음'}.
- 실환경 판정: `{manifest['features'].get('runtime_qualification', {}).get('status', 'pending')}` / `{manifest['features'].get('runtime_qualification', {}).get('method', '별도 검증')}`. 공식 SDK 신규 빌드와 구현 내용 동일성, 기존 GFS2 실환경 증거의 적용 범위는 manifest의 qualification/evidence_urls를 확인합니다.
- 클러스터 생성/확장/업그레이드 및 LB/VPC 런타임 검증의 환경·artifact 적용 범위는 별도 생명주기 기록을 따릅니다.
''' + registration_usage_notes(registration, manifest))
 files=sorted(x for x in args.directory.iterdir() if x.is_file() and x.name.startswith(name))
 sums=args.directory/'SHA256SUMS'
 def digest(path):
  h=hashlib.sha256()
  with path.open('rb') as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  return h.hexdigest()
 if digest(iso)!=report['iso_sha256'] or registration['checksum']!='{SHA-256}'+digest(iso):raise ValueError('ISO changed after validation')
 sums.write_text(''.join(digest(x)+'  '+x.name+'\n' for x in files))
 command=['gh','release','create',tag]+[str(x) for x in files]+[str(sums),'--repo',args.repository,'--target',source,'--latest=false','--title','Kubernetes '+registration['kubernetesversion']+' Mold ISO ('+args.mode+')','--notes-file',str(notes)]
 if args.mode=='origin-trial':command.append('--prerelease')
 subprocess.run(command,check=True)
 # Public GET is a separate download check; do not use authenticated gh download.
 downloaded=args.directory/(iso.name+'.public-download')
 try:
  subprocess.run(['curl','--fail','--location','--retry','3','--silent','--show-error',url,'-o',str(downloaded)],check=True)
  if digest(downloaded)!=digest(iso):raise ValueError('public Release download checksum mismatch')
 finally:downloaded.unlink(missing_ok=True)
 print(json.dumps({'release':'https://github.com/'+args.repository+'/releases/tag/'+tag,'iso_url':url,'public_download':'PASS'}))


if __name__=='__main__':main()
