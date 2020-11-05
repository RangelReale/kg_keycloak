from typing import Mapping

from kubragen.kdata import KData_Secret
from kubragen.kdatahelper import KDataHelper_Env
from kubragen.option import OptionDef, OptionDefFormat
from kubragen.options import Options


class KeycloakOptions(Options):
    """
    Options for the KeyCloak builder.

    .. list-table::
        :header-rows: 1

        * - option
          - description
          - allowed types
          - default value
        * - basename
          - object names prefix
          - str
          - ```keycloak```
        * - namespace
          - namespace
          - str
          - ```default```
        * - config |rarr| service_port
          - service port
          - int
          - ```8080```
        * - config |rarr| realm_import
          - realm import
          - str, bytes, :class:`KData_Secret`
          -
        * - config |rarr| proxy_address_forwarding
          - proxy address forwarding
          - bool, :class:`KData_Value`, :class:`KData_ConfigMap`, :class:`KData_Secret`
          -
        * - config |rarr| frontend_url
          - frontend url
          - str
          -
        * - admin |rarr| user
          - admin user name
          - str, :class:`KData_Value`, :class:`KData_ConfigMap`, :class:`KData_Secret`
          -
        * - admin |rarr| password
          - admin password
          - str, :class:`KData_Secret`
          -
        * - db |rarr| vendor
          - DB vendor
          - str, :class:`KData_Value`, :class:`KData_ConfigMap`, :class:`KData_Secret`
          -
        * - db |rarr| addr
          - DB host address
          - str, :class:`KData_Value`, :class:`KData_ConfigMap`, :class:`KData_Secret`
          -
        * - db |rarr| port
          - DB network port
          - str, :class:`KData_Value`, :class:`KData_ConfigMap`, :class:`KData_Secret`
          -
        * - db |rarr| database
          - DB database name
          - str, :class:`KData_Value`, :class:`KData_ConfigMap`, :class:`KData_Secret`
          - ```True```
        * - db |rarr| schema
          - DB schema
          - str, :class:`KData_Value`, :class:`KData_ConfigMap`, :class:`KData_Secret`
          -
        * - db |rarr| user
          - DB user
          - str, :class:`KData_Value`, :class:`KData_ConfigMap`, :class:`KData_Secret`
          -
        * - db |rarr| password
          - DB password
          - str, :class:`KData_Secret`
          -
        * - container |rarr| keycloak
          - keycloak container image
          - str
          - ```quay.io/keycloak/keycloak:<version>```
        * - kubernetes |rarr| resources |rarr| deployment
          - Kubernetes Deployment resources
          - dict
          -
    """
    def define_options(self):
        """
        Declare the options for the KeyCloak builder.

        :return: The supported options
        """
        return {
            'basename': OptionDef(required=True, default_value='keycloak', allowed_types=[str]),
            'namespace': OptionDef(required=True, default_value='default', allowed_types=[str]),
            'config': {
                'service_port': OptionDef(required=True, default_value=8080, allowed_types=[int]),
                'realm_import': OptionDef(format=OptionDefFormat.KDATA_VOLUME, allowed_types=[str, bytes, KData_Secret]),
                'proxy_address_forwarding': OptionDef(format=OptionDefFormat.KDATA_ENV,
                                                      allowed_types=[bool, *KDataHelper_Env.allowed_kdata()]),
                'frontend_url': OptionDef(allowed_types=[str]),
                'admin': {
                    'user': OptionDef(format=OptionDefFormat.KDATA_ENV, allowed_types=[str, *KDataHelper_Env.allowed_kdata()]),
                    'password': OptionDef(format=OptionDefFormat.KDATA_ENV, allowed_types=[str, KData_Secret]),
                },
                'db': {
                    'vendor': OptionDef(format=OptionDefFormat.KDATA_ENV, allowed_types=[str, *KDataHelper_Env.allowed_kdata()]),
                    'addr': OptionDef(format=OptionDefFormat.KDATA_ENV, allowed_types=[str, *KDataHelper_Env.allowed_kdata()]),
                    'port': OptionDef(format=OptionDefFormat.KDATA_ENV, allowed_types=[int, *KDataHelper_Env.allowed_kdata()]),
                    'database': OptionDef(format=OptionDefFormat.KDATA_ENV, allowed_types=[str, *KDataHelper_Env.allowed_kdata()]),
                    'schema': OptionDef(format=OptionDefFormat.KDATA_ENV, allowed_types=[str, *KDataHelper_Env.allowed_kdata()]),
                    'user': OptionDef(format=OptionDefFormat.KDATA_ENV, allowed_types=[str, *KDataHelper_Env.allowed_kdata()]),
                    'password': OptionDef(format=OptionDefFormat.KDATA_ENV, allowed_types=[str, KData_Secret]),
                },
            },
            'container': {
                'keycloak': OptionDef(required=True, default_value='quay.io/keycloak/keycloak:11.0.2', allowed_types=[str]),
            },
            'kubernetes': {
                'resources': {
                    'deployment': OptionDef(allowed_types=[Mapping]),
                }
            },
        }
