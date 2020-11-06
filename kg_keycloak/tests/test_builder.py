import unittest

from kubragen import KubraGen
from kubragen.jsonpatch import FilterJSONPatches_Apply, ObjectFilter, FilterJSONPatch
from kubragen.provider import Provider_Generic

from kg_keycloak import KeycloakBuilder, KeycloakOptions


class TestBuilder(unittest.TestCase):
    def setUp(self):
        self.kg = KubraGen(provider=Provider_Generic())

    def test_empty(self):
        keycloak_config = KeycloakBuilder(kubragen=self.kg)
        self.assertEqual(keycloak_config.object_name('config-secret'), 'keycloak-config-secret')
        self.assertEqual(keycloak_config.object_name('deployment'), 'keycloak')

    def test_basedata(self):
        keycloak_config = KeycloakBuilder(kubragen=self.kg, options=KeycloakOptions({
            'namespace': 'myns',
            'basename': 'mykeycloak',
        }))
        self.assertEqual(keycloak_config.object_name('config-secret'), 'mykeycloak-config-secret')
        self.assertEqual(keycloak_config.object_name('deployment'), 'mykeycloak')

        FilterJSONPatches_Apply(items=keycloak_config.build(keycloak_config.BUILD_SERVICE), jsonpatches=[
            FilterJSONPatch(filters=ObjectFilter(names=[keycloak_config.BUILDITEM_SERVICE]), patches=[
                {'op': 'check', 'path': '/metadata/name', 'cmp': 'equals', 'value': 'mykeycloak'},
                {'op': 'check', 'path': '/metadata/namespace', 'cmp': 'equals', 'value': 'myns'},
            ]),
        ])
