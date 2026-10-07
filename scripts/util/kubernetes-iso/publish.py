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
''')
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
