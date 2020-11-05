from typing import List, Optional

from kubragen import KubraGen
from kubragen.builder import Builder
from kubragen.data import ValueData
from kubragen.exception import InvalidNameError
from kubragen.helper import QuotedStr
from kubragen.kdata import IsKData
from kubragen.kdatahelper import KDataHelper_Env, KDataHelper_Volume
from kubragen.object import ObjectItem, Object
from kubragen.types import TBuild, TBuildItem

from .option import KeycloakOptions


class KeycloakBuilder(Builder):
    """
    Keycloak builder.

    Based on `keycloak/keycloak-quickstarts <https://github.com/keycloak/keycloak-quickstarts/tree/latest/kubernetes-examples>`_.

    .. list-table::
        :header-rows: 1

        * - build
          - description
        * - BUILD_CONFIG
          - creates ConfigMap
        * - BUILD_SERVICE
          - creates StatefulSet and Services

    .. list-table::
        :header-rows: 1

        * - build item
          - description
        * - BUILDITEM_CONFIG_SECRET
          - Secret
        * - BUILDITEM_DEPLOYMENT
          - Deployment
        * - BUILDITEM_SERVICE
          - Service

    .. list-table::
        :header-rows: 1

        * - object name
          - description
          - default value
        * - config-secret
          - Secret
          - ```<basename>-config-secret```
        * - service
          - Service
          - ```<basename>```
        * - deployment
          - Deployment
          - ```<basename>```
        * - pod-label-all
          - label *app* to be used by selection
          - ```<basename>```
    """
    options: KeycloakOptions
    _namespace: str

    SOURCE_NAME = 'kg_keycloak'

    BUILD_CONFIG: TBuild = 'config'
    BUILD_SERVICE: TBuild = 'service'

    BUILDITEM_CONFIG_SECRET: TBuildItem = 'config-secret'
    BUILDITEM_DEPLOYMENT: TBuildItem = 'deployment'
    BUILDITEM_SERVICE: TBuildItem = 'service'

    def __init__(self, kubragen: KubraGen, options: Optional[KeycloakOptions] = None):
        super().__init__(kubragen)
        if options is None:
            options = KeycloakOptions()
        self.options = options

        self._namespace = self.option_get('namespace')

        self.object_names_update({
            'config-secret': self.basename('-config-secret'),
            'service': self.basename(),
            'deployment': self.basename(),
            'pod-label-app': self.basename(),
        })

    def option_get(self, name: str):
        return self.kubragen.option_root_get(self.options, name)

    def basename(self, suffix: str = ''):
        return '{}{}'.format(self.option_get('basename'), suffix)

    def namespace(self):
        return self._namespace

    def build_names(self) -> List[TBuild]:
        return [self.BUILD_CONFIG, self.BUILD_SERVICE]

    def build_names_required(self) -> List[TBuild]:
        return [self.BUILD_CONFIG, self.BUILD_SERVICE]

    def builditem_names(self) -> List[TBuildItem]:
        return [
            self.BUILDITEM_CONFIG_SECRET,
            self.BUILDITEM_DEPLOYMENT,
            self.BUILDITEM_SERVICE,
        ]

    def internal_build(self, buildname: TBuild) -> List[ObjectItem]:
        if buildname == self.BUILD_CONFIG:
            return self.internal_build_config()
        elif buildname == self.BUILD_SERVICE:
            return self.internal_build_service()
        else:
            raise InvalidNameError('Invalid build name: "{}"'.format(buildname))

    def internal_build_config(self) -> List[ObjectItem]:
        secret_data = {}

        if not IsKData(self.option_get('config.realm_import')):
            if self.option_get('config.realm_import') is not None:
                secret_data.update({
                    'keycloak-realm.json': self.kubragen.secret_data_encode(self.option_get('config.realm_import')),
                })

        if not IsKData(self.option_get('config.admin.user')):
            if self.option_get('config.admin.user') is not None:
                secret_data.update({
                    'user': self.kubragen.secret_data_encode(self.option_get('config.admin.user')),
                })

        if not IsKData(self.option_get('config.admin.password')):
            if self.option_get('config.admin.password') is not None:
                secret_data.update({
                    'password': self.kubragen.secret_data_encode(self.option_get('config.admin.password')),
                })

        if not IsKData(self.option_get('config.db.password')):
            if self.option_get('config.db.password') is not None:
                secret_data.update({
                    'dbpassword': self.kubragen.secret_data_encode(self.option_get('config.db.password')),
                })

        ret = []
        if len(secret_data) > 0:
            ret.append(Object({
                'apiVersion': 'v1',
                'kind': 'Secret',
                'metadata': {
                    'name': self.object_name('config-secret'),
                    'namespace': self.namespace(),
                },
                'data': secret_data
            }, name=self.BUILDITEM_CONFIG_SECRET, source=self.SOURCE_NAME, instance=self.basename()))

        return ret

    def internal_build_service(self) -> List[ObjectItem]:
        ret = [
            Object({
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': self.object_name('deployment'),
                    'labels': {
                        'app': self.object_name('pod-label-app'),
                    },
                    'namespace': self.namespace(),
                },
                'spec': {
                    'selector': {
                        'matchLabels': {
                            'app': self.object_name('pod-label-app'),
                        }
                    },
                    'template': {
                        'metadata': {
                            'labels': {
                                'app': self.object_name('pod-label-app'),
                            }
                        },
                        'spec': {
                            'volumes': [
                                KDataHelper_Volume.info(base_value={
                                    'name': 'keycloak-realm-volume',
                                }, kdata_value=self.option_get('config.realm_import'), default_value={
                                    'secret': {
                                        'secretName': self.object_name('config-secret'),
                                        'items': [{
                                            'key': 'keycloak-realm.json',
                                            'path': 'keycloak-realm.json',
                                        }]
                                    },
                                }, key_path='keycloak-realm.json', enabled=self.option_get('config.realm_import') is not None),
                            ],
                            'containers': [{
                                'name': 'keycloak',
                                'image': self.option_get('container.keycloak'),
                                'env': [
                                    KDataHelper_Env.info(base_value={
                                        'name': 'KEYCLOAK_USER',
                                    }, kdata_value=self.option_get('config.admin.user'), default_value={
                                        'valueFrom': {
                                            'secretKeyRef': {
                                                'name': self.object_name('config-secret'),
                                                'key': 'user'
                                            }
                                        },
                                    }, disable_if_none=True),
                                    KDataHelper_Env.info(base_value={
                                        'name': 'KEYCLOAK_PASSWORD',
                                    }, kdata_value=self.option_get('config.admin.password'), default_value={
                                        'valueFrom': {
                                            'secretKeyRef': {
                                                'name': self.object_name('config-secret'),
                                                'key': 'password'
                                            }
                                        },
                                    }, disable_if_none=True),
                                    ValueData(value={
                                        'name': 'KEYCLOAK_IMPORT',
                                        'value': '/etc/kc-auth-realm/keycloak-realm.json'
                                    }, enabled=self.option_get('config.realm_import') is not None),
                                    KDataHelper_Env.info(base_value={
                                        'name': 'DB_VENDOR',
                                    }, value=self.option_get('config.db.vendor'), disable_if_none=True),
                                    KDataHelper_Env.info(base_value={
                                        'name': 'DB_ADDR',
                                    }, value=self.option_get('config.db.addr'), disable_if_none=True),
                                    KDataHelper_Env.info(base_value={
                                        'name': 'DB_PORT',
                                    }, value=self.option_get('config.db.port'), default_value={
                                        'value': QuotedStr(self.option_get('config.db.port')),
                                    }, disable_if_none=True),
                                    KDataHelper_Env.info(base_value={
                                        'name': 'DB_DATABASE',
                                    }, value=self.option_get('config.db.database'), disable_if_none=True),
                                    KDataHelper_Env.info(base_value={
                                        'name': 'DB_SCHEMA',
                                    }, value=self.option_get('config.db.schema'), disable_if_none=True),
                                    KDataHelper_Env.info(base_value={
                                        'name': 'DB_USER',
                                    }, value=self.option_get('config.db.user'), disable_if_none=True),
                                    KDataHelper_Env.info(base_value={
                                        'name': 'DB_PASSWORD',
                                    }, kdata_value=self.option_get('config.db.password'), default_value={
                                        'valueFrom': {
                                            'secretKeyRef': {
                                                'name': self.object_name('config-secret'),
                                                'key': 'dbpassword',
                                            }
                                        },
                                    }, disable_if_none=True),
                                    KDataHelper_Env.info(base_value={
                                        'name': 'PROXY_ADDRESS_FORWARDING',
                                    }, kdata_value=self.option_get('config.proxy_address_forwarding'), default_value={
                                        'value': QuotedStr('true' if self.option_get(
                                            'config.proxy_address_forwarding') is not False else 'false'),
                                    }, disable_if_none=True),
                                ],
                                'ports': [{
                                    'name': 'web',
                                    'containerPort': 8080
                                },
                                {
                                    'name': 'websecure',
                                    'containerPort': 8443
                                }],
                                'readinessProbe': {
                                    'httpGet': {
                                        'path': '/auth/realms/master',
                                        'port': 8080
                                    }
                                },
                                'volumeMounts': [
                                    ValueData({
                                        'name': 'keycloak-realm-volume',
                                        'mountPath': '/etc/kc-auth-realm'
                                    }, enabled=self.option_get('config.realm_import') is not None)
                                ],
                                'resources': ValueData(value=self.option_get('kubernetes.resources.deployment'),
                                                       disabled_if_none=True),
                            }]
                        }
                    }
                }
            }, name=self.BUILDITEM_DEPLOYMENT, source=self.SOURCE_NAME, instance=self.basename()),
            Object({
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': self.object_name('service'),
                    'namespace': self.namespace(),
                },
                'spec': {
                    'ports': [{
                        'name': 'web',
                        'port': self.option_get('config.service_port'),
                        'targetPort': 8080
                    }],
                    'selector': {
                        'app': self.object_name('pod-label-app'),
                    }
                }
            }, name=self.BUILDITEM_SERVICE, source=self.SOURCE_NAME, instance=self.basename())
        ]
        return ret
