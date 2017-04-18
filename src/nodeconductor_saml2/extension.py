import os
import saml2
import saml2.saml

from nodeconductor.core import NodeConductorExtension


class SAML2Extension(NodeConductorExtension):

    class Settings:
        CONF_DIR = '/etc/nodeconductor/saml2'

        NODECONDUCTOR_SAML2 = {
            # full path to the xmlsec1 binary program
            'xmlsec_binary': '/usr/local/bin/xmlsec1',
            # required for assertion consumer, single logout services and entity ID
            'base_url': 'http://example.com',
            # directory with attribute mapping
            'attribute_map_dir': os.path.join(CONF_DIR, 'attribute-maps'),
            # set to True to output debugging information
            'debug': False,
            # IdPs metadata XML files stored locally
            'idp_metadata_local': [],
            # IdPs metadata XML files stored remotely
            'idp_metadata_remote': [
                {
                    # URL to the metadata XML file
                    'url': 'http://idp.example.com/saml2/idp/metadata.php',
                    # path to PEM certificate required to retrieve the remote metadata XML file
                    'cert': os.path.join(CONF_DIR, 'example-idp.pem'),
                },
            ],
            # logging
            'log_file': '',
            'log_level': 'INFO',
            # PEM formatted certificate chain file
            'cert_file': os.path.join(CONF_DIR, 'sp1.crt'),
            # PEM formatted certificate key file
            'key_file': os.path.join(CONF_DIR, 'sp1.pem'),
            # SAML attributes that are required to identify a user
            'required_attributes': ['cn', 'mail', 'schacPersonalUniqueID'],
            # SAML attributes that may be useful to have but not required
            'optional_attributes': ['schacHomeOrganization', 'preferredLanguage'],
            # mapping between SAML attributes and User fields
            'saml_attribute_mapping': {
                'schacPersonalUniqueID': ['username', 'civil_number'],
                'cn': ['full_name'],
                'mail': ['email'],
                'preferredLanguage': ['preferred_language'],
                'schacHomeOrganization': ['organization'],
            },
            # organization responsible for the service
            # you can set multilanguage information here
            'organization': {
                'name': [('OpenNode OU', 'et'), ('OpenNode LLC', 'en')],
                'display_name': [('OpenNode', 'et'), ('OpenNode', 'en')],
                'url': [('https://opennodecloud.com/', 'et'), ('https://opennodecloud.com/', 'en')],
            },
        }

        # These shouldn't be configurable by user -- see SAML2 section for details
        SAML_CREATE_UNKNOWN_USER = True
        SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'username'

        SAML_ATTRIBUTE_MAPPING = NODECONDUCTOR_SAML2['saml_attribute_mapping']

        SAML_CONFIG = {
            # full path to the xmlsec1 binary program
            'xmlsec_binary': NODECONDUCTOR_SAML2['xmlsec_binary'],

            # your entity id, usually your subdomain plus the url to the metadata view
            'entityid': NODECONDUCTOR_SAML2['base_url'] + '/api-auth/saml2/metadata/',

            # directory with attribute mapping
            'attribute_map_dir': NODECONDUCTOR_SAML2['attribute_map_dir'],

            # this block states what services we provide
            'service': {
                # we are just a lonely SP
                'sp': {
                    # Indicates if the entity will sign the logout requests
                    'logout_requests_signed': 'true',
                    # Indicates if the authentication requests sent should be signed by default
                    'authn_requests_signed': 'true',

                    'endpoints': {
                        # url and binding to the assertion consumer service view
                        # do not change the binding or service name
                        'assertion_consumer_service': [
                            (NODECONDUCTOR_SAML2['base_url'] + '/api-auth/saml2/login/complete/',
                             saml2.BINDING_HTTP_POST),
                        ],
                        # url and binding to the single logout service view
                        # do not change the binding or service name
                        'single_logout_service': [
                            (NODECONDUCTOR_SAML2['base_url'] + '/api-auth/saml2/logout/complete/',
                             saml2.BINDING_HTTP_REDIRECT),
                            (NODECONDUCTOR_SAML2['base_url'] + '/api-auth/saml2/logout/complete/',
                             saml2.BINDING_HTTP_POST),
                        ],
                    },

                    # attributes that this project needs to identify a user
                    'required_attributes': NODECONDUCTOR_SAML2['required_attributes'],

                    # attributes that may be useful to have but not required
                    'optional_attributes': NODECONDUCTOR_SAML2['optional_attributes'],
                },
            },

            # where the remote metadata is stored
            'metadata': {
                'local': NODECONDUCTOR_SAML2['idp_metadata_local'],
                'remote': NODECONDUCTOR_SAML2['idp_metadata_remote'],
            },

            'organization': NODECONDUCTOR_SAML2['organization'],

            # set to 1 to output debugging information
            'debug': int(NODECONDUCTOR_SAML2['debug']),

            # signing
            'key_file': NODECONDUCTOR_SAML2['key_file'],  # private part
            'cert_file': NODECONDUCTOR_SAML2['cert_file'],  # public part

            'only_use_keys_in_metadata': False,
            'allow_unknown_attributes': True,

            'accepted_time_diff': 120,
        }

    @staticmethod
    def update_settings(settings):
        settings['AUTHENTICATION_BACKENDS'] += ('djangosaml2.backends.Saml2Backend',)

    @staticmethod
    def django_app():
        return 'nodeconductor_saml2'

    @staticmethod
    def django_urls():
        from .urls import urlpatterns
        return urlpatterns
