# KubraGen Builder: Keycloak

[![PyPI version](https://img.shields.io/pypi/v/kg_keycloak.svg)](https://pypi.python.org/pypi/kg_keycloak/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/kg_keycloak.svg)](https://pypi.python.org/pypi/kg_keycloak/)

kg_keycloak is a builder for [KubraGen](https://github.com/RangelReale/kubragen) that deploys 
a [Keycloak](https://www.keycloak.org/) server in Kubernetes.

[KubraGen](https://github.com/RangelReale/kubragen) is a Kubernetes YAML generator library that makes it possible to generate
configurations using the full power of the Python programming language.

* Website: https://github.com/RangelReale/kg_keycloak
* Repository: https://github.com/RangelReale/kg_keycloak.git
* Documentation: https://kg_keycloak.readthedocs.org/
* PyPI: https://pypi.python.org/pypi/kg_keycloak

## Example
```python
from kubragen import KubraGen
from kubragen.consts import PROVIDER_GOOGLE, PROVIDERSVC_GOOGLE_GKE
from kubragen.object import Object
from kubragen.option import OptionRoot
from kubragen.options import Options
from kubragen.output import OutputProject, OD_FileTemplate, OutputFile_ShellScript, OutputFile_Kubernetes, \
    OutputDriver_Print
from kubragen.provider import Provider

from kg_keycloak import KeycloakBuilder, KeycloakOptions

kg = KubraGen(provider=Provider(PROVIDER_GOOGLE, PROVIDERSVC_GOOGLE_GKE), options=Options({
    'namespaces': {
        'mon': 'app-monitoring',
    },
}))

out = OutputProject(kg)

shell_script = OutputFile_ShellScript('create_gke.sh')
out.append(shell_script)

shell_script.append('set -e')

#
# OUTPUTFILE: app-namespace.yaml
#
file = OutputFile_Kubernetes('app-namespace.yaml')

file.append([
    Object({
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {
            'name': 'app-monitoring',
        },
    }, name='ns-monitoring', source='app', instance='app')
])

out.append(file)
shell_script.append(OD_FileTemplate(f'kubectl apply -f ${{FILE_{file.fileid}}}'))

shell_script.append(f'kubectl config set-context --current --namespace=app-monitoring')

#
# SETUP: keycloak
#
keycloak_config = KeycloakBuilder(kubragen=kg, options=KeycloakOptions({
    'namespace': OptionRoot('namespaces.mon'),
    'basename': 'mykeycloak',
    'config': {
        'service_port': 80,
        'proxy_address_forwarding': True,
        'admin': {
            'user': 'test@example.com',
            'password': 'mypassword',
        },
    },
    'kubernetes': {
        'resources': {
            'deployment': {
                'requests': {
                    'cpu': '150m',
                    'memory': '300Mi'
                },
                'limits': {
                    'cpu': '300m',
                    'memory': '450Mi'
                },
            },
        },
    }
}))

keycloak_config.ensure_build_names(keycloak_config.BUILD_CONFIG, keycloak_config.BUILD_SERVICE)

#
# OUTPUTFILE: keycloak-config.yaml
#
file = OutputFile_Kubernetes('keycloak-config.yaml')
out.append(file)

file.append(keycloak_config.build(keycloak_config.BUILD_CONFIG))

shell_script.append(OD_FileTemplate(f'kubectl apply -f ${{FILE_{file.fileid}}}'))

#
# OUTPUTFILE: keycloak.yaml
#
file = OutputFile_Kubernetes('keycloak.yaml')
out.append(file)

file.append(keycloak_config.build(keycloak_config.BUILD_SERVICE))

shell_script.append(OD_FileTemplate(f'kubectl apply -f ${{FILE_{file.fileid}}}'))

#
# Write files
#
out.output(OutputDriver_Print())
# out.output(OutputDriver_Directory('/tmp/build-gke'))
```

Output:

```text
****** BEGIN FILE: 001-app-namespace.yaml ********
apiVersion: v1
kind: Namespace
metadata:
  name: app-monitoring

****** END FILE: 001-app-namespace.yaml ********
****** BEGIN FILE: 002-keycloak-config.yaml ********
apiVersion: v1
kind: Secret
metadata:
  name: mykeycloak-config-secret
  namespace: app-monitoring
data:
  user: dGVzdEBleGFtcGxlLmNvbQ==
  password: bXlwYXNzd29yZA==

****** END FILE: 002-keycloak-config.yaml ********
****** BEGIN FILE: 003-keycloak.yaml ********
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mykeycloak
  labels:
    app: mykeycloak
  namespace: app-monitoring
spec:
  selector:
    matchLabels:
      app: mykeycloak
<...more...>
****** END FILE: 003-keycloak.yaml ********
****** BEGIN FILE: create_gke.sh ********
#!/bin/bash

set -e
kubectl apply -f 001-app-namespace.yaml
kubectl config set-context --current --namespace=app-monitoring
kubectl apply -f 002-keycloak-config.yaml
kubectl apply -f 003-keycloak.yaml

****** END FILE: create_gke.sh ********
```

### Credits

based on

[keycloak/keycloak-quickstarts](https://github.com/keycloak/keycloak-quickstarts/tree/latest/kubernetes-examples)

## Author

Rangel Reale (rangelreale@gmail.com)
