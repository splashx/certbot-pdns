"""DNS Authenticator for PowerDNS."""

import logging

import zope.interface
from certbot import interfaces
from certbot.plugins import dns_common
from certbot import errors

from certbot_dns_powerdns.pdnsapi import PdnsApi

logger = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """PDNS Authenticator."""

    description =  ('Obtain certificates using a DNS TXT record (if you are using PowerDNS for '
                   'DNS).')

    ttl = 60

    backend = None

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(add)
        add("credentials", default="/etc/letsencrypt/certbot-powerdns.json",
            help="PowerDNS credentials JSON file.")

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
                'PowerDNS API'

    def _setup_credentials(self):
        self._configure_file('credentials',
                             'Absolute path to PowerDNS credentials JSON file')
        dns_common.validate_file_permissions(self.conf('credentials'))
        self.credentials = self._configure_credentials(
            'credentials',
            'PowerDNS credentials INI file',
            {
                'api-url': 'URL of PowerDNS server without uri/path/api version',
                'api-key': 'API key able to change records in the PowerDNS zone'
            }
        )

    def _perform(self, domain, validation_name, validation):
        self._get_powerdns_client().add_txt_record(domain, validation_name, validation, self.ttl)

    def _cleanup(self, domain, validation_name, validation):
        self._get_powerdns_client().del_txt_record(domain, validation_name, validation)

    def _get_powerdns_client(self):
        return _PowerDNSClient(api_url=self.credentials.conf('api-url'),
                               api_key=self.credentials.conf('api-key'))


class _PowerDNSClient(object):
    """
    Encapsulates all communication with the PowerDNS API.
    """

    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.axfr_time = 5
        self.zones = None
        self.pdns_client = PdnsApi(api_url=api_url, api_key=api_key)
        self._prepare(self.pdns_client)

    def add_txt_record(self, domain, record_name, record_content, record_ttl):
        """
        Add a TXT record using the supplied information.
        :param str domain: The domain to use to look up the zone in PowerDNS.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        :param int record_ttl: The record TTL (number of seconds that the record may be cached).
        :raises certbot.errors.PluginError: if an error occurs communicating with the DNS server
        """
        zone = self._find_best_matching_zone(domain)

        if zone is None:
            raise errors.PluginError("Could not find zone for %s" % domain)

        res = self.pdns_client.replace_record(zone_name=zone["name"],
                                              name="_acme-challenge." + domain + ".",
                                              type="TXT",
                                              ttl=record_ttl,
                                              content=record_content)
        if res is not None:
            raise errors.PluginError("Bad return from PDNS API when adding record: %s", res)

    def del_txt_record(self, domain, record_name, record_content):
        """
        Delete a TXT record using the supplied information.
        Note that both the record's name and content are used to ensure that similar records
        created concurrently (e.g., due to concurrent invocations of this plugin) are not deleted.
        Failures are logged, but not raised.
        :param str domain: The domain to use to look up the PowerDNS zone.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        """

        zone = self._find_best_matching_zone(domain)
        if zone is None:
            return

        res = self.pdns_client.delete_record(zone_name=zone["name"],
                                             name=record_name,
                                             type="TXT",)
        if res is not None:
            raise errors.PluginError("Bad return from PDNS API when deleting record: %s" % res)
        else:
            logger.debug('Deleted TXT record successfully. Clean up finished.')

    def _find_best_matching_zone(self, domain):
        logger.debug("Checking zones matching domain '%s'", domain)
        if domain is None or domain == "":
            logger.debug("Exhausted all zones - couldn't find one matching '%s'" % domain)
            return None
        for zone in self.zones:
            if zone['name'] == self.pdns_client.ensure_dot(text=domain):
                logger.debug("Found zone '%s' for domain '%s'", zone["name"], domain)
                return zone
            logger.debug("Domain '%s' does not match zone '%s' ...", domain, zone['name'])
        return self._find_best_matching_zone(domain[domain.index(".") + 1:]) if "." in domain else None

    def _prepare(self, client):
        self.pdns_client = client

        try:
            logger.debug('Getting list of all zones ...')
            self.zones = self.pdns_client.list_zones()
        except Exception as e:
            logger.error('Encountered an Exception while retrieving zones.')
            logger.debug('The error message was: %s', str(e))
            raise errors.PluginError('Error while retrieving zones from PowerDNS API: {0}'.format(e))

        if self.zones is None:
            raise errors.PluginError("Zone listing returned nothing.")
        else:
            logger.debug('Found %d zones in total...', len(self.zones))
