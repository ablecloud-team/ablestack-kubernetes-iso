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
import copy
import importlib.util
import json
from pathlib import Path
import sys
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from release_support import autoscaler_release_basis, validate_autoscaler_production_qualification, validate_runtime_qualification

spec = importlib.util.spec_from_file_location('iso_publish', HERE / 'publish.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class ProductionQualification(unittest.TestCase):
    def setUp(self):
        self.recipe = json.loads((HERE / 'recipes/kubernetes-1.37.1-amd64.json').read_text())

    def test_qualified_internal_build_preserves_development_provenance(self):
        self.assertEqual(autoscaler_release_basis(self.recipe), 'mold-production-qualified')
        self.assertEqual(self.recipe['components']['autoscaler']['baseline_status'], 'development-candidate')

    def test_stable_baseline_does_not_require_internal_override(self):
        r = json.loads((HERE / 'recipes/kubernetes-1.34.2-amd64.json').read_text())
        self.assertEqual(autoscaler_release_basis(r), 'upstream-stable')

    def test_development_baseline_without_qualification_is_rejected(self):
        del self.recipe['features']['autoscaler_qualification']
        with self.assertRaisesRegex(ValueError, 'stable baseline or exact Mold'):
            autoscaler_release_basis(self.recipe)

    def test_changed_build_or_platform_cannot_reuse_production_acceptance(self):
        changes = {'kubernetes_version':'1.37.2', 'kubernetes_minor':'1.36', 'architecture':'arm64',
                   'source_sha':'0'*40, 'binary_source_sha':'0'*40,
                   'image':'example.com/autoscaler@sha256:'+'0'*64,
                   'api_signature':'HMAC-SHA1', 'customization_files':{}}
        for field, value in changes.items():
            with self.subTest(field=field):
                r = copy.deepcopy(self.recipe)
                r['features']['autoscaler_qualification'][field] = value
                with self.assertRaises(ValueError):
                    validate_autoscaler_production_qualification(r)

    def test_changed_component_must_be_requalified(self):
        for field, value in {'source_sha':'0'*40, 'architecture':'arm64', 'image':'example.com/as@sha256:'+'0'*64,
                             'customization_files':{'client.go':'0'*64}}.items():
            with self.subTest(field=field):
                r = copy.deepcopy(self.recipe)
                r['components']['autoscaler'][field] = value
                with self.assertRaises(ValueError):
                    autoscaler_release_basis(r)

    def test_missing_failed_or_nonproduction_decision_is_rejected(self):
        for field, value in [('status','pending'), ('status','FAIL'), ('support_level','development'), ('product','Other'),
                             ('evidence_urls',[]), ('evidence_urls','https://example.com'),
                             ('evidence_urls',['http://example.com']),
                             ('evidence_urls',['https://user:password@example.com'])]:
            with self.subTest(field=field, value=value):
                r = copy.deepcopy(self.recipe)
                r['features']['autoscaler_qualification'][field] = value
                with self.assertRaises(ValueError):
                    autoscaler_release_basis(r)

    def test_csi_profile_uses_the_same_autoscaler_decision(self):
        csi = json.loads((HERE / 'recipes/kubernetes-1.37.1-mold-cks-csi-amd64.json').read_text())
        self.assertEqual(autoscaler_release_basis(csi), 'mold-production-qualified')
        self.assertEqual(csi['features']['autoscaler_qualification'], self.recipe['features']['autoscaler_qualification'])

    def assert_official_publish_still_rejects(self, manifest, message):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            name = 'kubernetes-v1.37.1-mold-cks-amd64-r1-12345678'
            (root / (name+'.iso')).write_bytes(b'fixture')
            (root / (name+'.manifest.json')).write_text(json.dumps(manifest))
            (root / (name+'.validation.json')).write_text(json.dumps({'status':'PASS','containerd_import':{'status':'PASS'}}))
            (root / (name+'.registration.json')).write_text(json.dumps({
                'release_eligible':True, 'source_repository':'ablecloud-team/ablestack-kubernetes-iso',
                'source_sha':'1'*40}))
            argv = ['publish.py','--directory',str(root),'--repository','ablecloud-team/ablestack-kubernetes-iso','--mode','official']
            with patch.object(sys,'argv',argv), patch.object(publisher,'run',return_value='1'*40), \
                 patch.object(publisher.subprocess,'run',side_effect=AssertionError('must not publish or mutate refs')):
                with self.assertRaisesRegex(ValueError,message):
                    publisher.main()

    def test_internal_autoscaler_acceptance_does_not_skip_lifecycle_gate(self):
        r = copy.deepcopy(self.recipe)
        r['features']['runtime_qualification'] = {'status':'pending', 'evidence_urls':[]}
        self.assert_official_publish_still_rejects(r,'node lifecycle runtime qualification')

    def test_internal_autoscaler_acceptance_does_not_skip_csi_gate(self):
        r = json.loads((HERE / 'recipes/kubernetes-1.37.1-mold-cks-csi-amd64.json').read_text())
        r['features']['runtime_qualification'] = {'status':'PASS','evidence_urls':['https://example.com/runtime']}
        self.assert_official_publish_still_rejects(r,'minor-specific storage runtime qualification')

    def test_internal_autoscaler_acceptance_does_not_skip_component_or_sdk_promotion(self):
        r = copy.deepcopy(self.recipe)
        r['components']['provider']['sdk']['candidate_module'] = 'github.com/dhslove/ablestack-mold-go/v2'
        self.assert_official_publish_still_rejects(r,'promoted Upstream component sources and SDK')

    def test_runtime_promotion_is_bound_to_version_components_and_sdk(self):
        validate_runtime_qualification(self.recipe)
        for name, field in [('provider','source_sha'), ('provider','image'), ('autoscaler','image')]:
            r = copy.deepcopy(self.recipe)
            r['features']['runtime_qualification']['components'][name][field] = 'stale'
            with self.assertRaisesRegex(ValueError,'component lock mismatch'):
                validate_runtime_qualification(r)
        r = copy.deepcopy(self.recipe)
        r['features']['runtime_qualification']['kubernetes_version'] = '1.37.2'
        with self.assertRaisesRegex(ValueError,'version/architecture'):
            validate_runtime_qualification(r)
        r = copy.deepcopy(self.recipe)
        r['components']['provider']['sdk']['source_sha'] = '0'*40
        with self.assertRaisesRegex(ValueError,'SDK lock mismatch'):
            validate_runtime_qualification(r)

    def test_multiple_version_tags_at_one_source_are_allowed_exactly(self):
        with tempfile.TemporaryDirectory() as temporary:
            subprocess.run(['git','init','--quiet',temporary],check=True)
            previous=os.getcwd()
            try:
                os.chdir(temporary)
                subprocess.run(['git','-c','user.name=Test','-c','user.email=test@example.com','commit','--allow-empty','-m','fixture','--quiet'],check=True)
                source=publisher.run(['git','rev-parse','HEAD'])
                for tag in ['k8s-v1.34.2-mold-cks-amd64-r1-'+source[:8], 'k8s-v1.37.1-mold-cks-amd64-r1-'+source[:8]]:
                    subprocess.run(['git','tag',tag],check=True)
                    publisher.verify_immutable_tag(source,tag)
                with self.assertRaisesRegex(ValueError,'immutable tag mismatch'):
                    publisher.verify_immutable_tag('0'*40,tag)
            finally:
                os.chdir(previous)


if __name__ == '__main__':
    unittest.main()
