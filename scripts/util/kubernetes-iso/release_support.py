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
"""Keep upstream provenance separate from exact Mold production qualification."""
import re
from urllib.parse import urlparse


def validate_autoscaler_production_qualification(document):
    qualification = document['features'].get('autoscaler_qualification')
    if qualification is None:
        return None
    component = document['components']['autoscaler']
    version = document['kubernetes_version']
    minor = '.'.join(version.split('.')[:2])
    if not isinstance(qualification, dict):
        raise ValueError('Mold AutoScaler qualification must be a record')
    if (qualification.get('status') != 'PASS' or qualification.get('support_level') != 'production'
            or qualification.get('product') != 'Mold'):
        raise ValueError('Mold AutoScaler production qualification requires production/PASS')
    if (qualification.get('kubernetes_version') != version
            or qualification.get('kubernetes_minor') != minor
            or component.get('kubernetes_minor') != minor
            or qualification.get('architecture') != document['architecture']
            or component.get('architecture') != document['architecture']):
        raise ValueError('Mold AutoScaler qualification version/architecture mismatch')
    for field in ('source_sha', 'binary_source_sha', 'image', 'api_signature', 'customization_files'):
        if not component.get(field) or qualification.get(field) != component[field]:
            raise ValueError('Mold AutoScaler qualification source/image/customization mismatch: ' + field)
    if (component['api_signature'] != 'HMAC-SHA256'
            or not re.fullmatch('[a-f0-9]{40}', component['source_sha'])
            or not re.fullmatch('[a-f0-9]{40}', component['binary_source_sha'])
            or not re.fullmatch(r'[^\s]+@sha256:[a-f0-9]{64}', component['image'])):
        raise ValueError('Mold AutoScaler qualification requires immutable SHA256 provenance')
    files = component['customization_files']
    if (not {'client.go', 'mold_worker_identity.go'}.issubset(files)
            or not all(isinstance(value, str) and re.fullmatch('[a-f0-9]{64}', value)
                       for value in files.values())):
        raise ValueError('Mold AutoScaler qualification requires locked customization hashes')
    urls = qualification.get('evidence_urls')
    if not isinstance(urls, list) or not urls:
        raise ValueError('Mold AutoScaler qualification requires evidence URLs')
    for url in urls:
        parsed = urlparse(url) if isinstance(url, str) else None
        if (parsed is None or parsed.scheme != 'https' or not parsed.hostname
                or parsed.username or parsed.password):
            raise ValueError('Mold AutoScaler qualification requires public HTTPS evidence URLs')
    return qualification


def autoscaler_release_basis(document):
    qualification = validate_autoscaler_production_qualification(document)
    component = document['components']['autoscaler']
    if component['kubernetes_minor'] != '.'.join(document['kubernetes_version'].split('.')[:2]):
        raise ValueError('Kubernetes/AutoScaler minor mismatch')
    if component.get('baseline_status') == 'stable':
        return 'upstream-stable'
    if qualification:
        return 'mold-production-qualified'
    raise ValueError('official Release requires a stable baseline or exact Mold production qualification')
