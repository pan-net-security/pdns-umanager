"""
given a file with data yaml data in the format:

example.org:
   service:
        type: "CNAME"
        value: "www.somezone.com"
   smtp:
        type: "A"
        value: "192.163.62.1"
        ttl: 500
   www:
        type: "A"
        value: ""
        ttl: 500
   foo:
        type: "zone"

This will result in:

- creation of rrset:   service.example.org CNAME   www.somezone.com
- creation of rrset:   smtp.service.org    A       192.163.62.1
- deletion of rrset:   www
- creation of zone:    "acme.example.org"

TODO:
- This script could at the end manage the whole zone, including deleting the rrsets
which were added manually or not by this script

"""

import sys
import requests
import json
import logging
import urllib
import operator
import ipaddress

DEFAULT_TYPE = "CNAME"
DEFAULT_TTL = "150"


class PDNSJanitor(object):
    """
    Main execution
    """

    def __init__(self):
        pass

    def config(self, api_host, api_key, api_version, zones_data):
        self.apihost = api_host
        self.apikey = api_key
        self.zones_data = zones_data

        self.apiversion = api_version
        logging.debug("Setting up config for PDNSJanitor")
        self.setup_api()
        self.zones = self.zone_order()

    def zone_order(self):
        """
        Zones must be created in order of hierarchy. This will return a list of zones
        sorted by the smalles zone number to the greatest zone number
        :return: list
        """
        zones = self.zones_data.keys()
        logging.debug("Found the following declared zones:\n%s", "\n".join([i for i in zones]))
        zone_by_length = dict()
        for i in [k for k in zones]:
            zone_by_length[i] = len(i.split("."))

        sorted_zones = [x[0] for x in sorted(zone_by_length.items(), key=operator.itemgetter(1))]
        logging.debug("Sorted zones:\n%s", "\n".join(sorted_zones))
        return sorted_zones

    def run(self):
        for zone in self.zones:
            zone = zone.strip()
            logging.info("* ZONE: '%s'", zone)

            zone_check_result, zone_data = self.query_zone(self.ensure_dot(zone))
            if zone_data:
                logging.info("Zone '%s' exists and is readable", zone)
            else:
                if zone_check_result.status_code == 404:
                    self.add_zone(zone)
                else:
                    logging.warning("Skipping zone '%s'...", zone)
                    continue

            logging.info("Applying updates for zone '%s'", zone)
            self.add_record(zone=zone, rrsets=self.zones_data[zone])

    def add_record(self, zone, rrsets):
        """
        Add new DNS rrset/records

        """

        add_record_api_uri = self.uri + "zones/" + self.ensure_dot(zone)
        if rrsets is None:
            return
        else:
            for rrset_name in rrsets.keys():
                logging.debug("RRSET_NAME: %s", rrset_name)

                rrset_type = rrsets[rrset_name].get('type', None)
                rrset_ttl = rrsets[rrset_name].get('ttl', None)
                rrset_records = rrsets[rrset_name].get('records', None)

                if rrset_type is None:
                    logging.warning("Missing 'type' for record '%s' in zone '%s', using '%s'",
                                    rrset_name, zone, DEFAULT_TYPE)
                    rrset_type = DEFAULT_TYPE

                if rrset_ttl is None:
                    logging.warning("Missing 'ttl' for record '%s' in zone '%s', using '%s'",
                                    rrset_name, zone, DEFAULT_TTL)
                    rrset_ttl = DEFAULT_TTL

                if rrset_records is None:
                    logging.warning("[!] On zone '%s' rrset '%s' the record is empty, this will effectively erase all "
                                    "records for '%s' type '%s'", rrset_name, rrset_name, rrset_type)
                logging.debug(" RRSET_TYPE: %s", rrset_type)
                logging.debug(" RRSET_TTL: %s", rrset_ttl)
                logging.debug(" RRSET_RECORDS: %s", rrset_records)

                rrset_records_payload = []
                for record in rrset_records:
                    if record != "":
                        try:
                            record = ipaddress.ip_address(record).compressed
                        except ValueError:
                            record = self.ensure_dot(record)

                        rrset_records_payload.append({
                            "content": record.lower(),
                            "disabled": False,
                            "set-ptr": False,
                        })

                logging.debug(" RECORD_PAYLOAD: %s", rrset_records_payload)

                payload = {
                    "rrsets": [
                        {
                            "name": (self.ensure_dot(rrset_name) + self.ensure_dot(zone)).lower(),
                            "type": rrset_type.lower(),
                            "ttl": rrset_ttl,
                            "records": rrset_records_payload,
                            "changetype": "REPLACE",
                        }
                    ]
                }

                logging.debug("Patching zone '%s' with payload %s", zone, payload)
                try:
                    patch_zone = requests.patch(add_record_api_uri, data=json.dumps(payload), headers=self.headers)
                    if patch_zone.status_code == 204:
                        pass
                    else:
                        logging.error("Failed to update zone '%s', zone. Server returned status code '%s'",
                                      zone, patch_zone.status_code)
                        logging.error("The server returned the following body message: %s", patch_zone.text)
                        logging.debug(patch_zone)
                        sys.exit(1)
                except Exception as e:
                    logging.debug(e)
                    logging.error("There as an exception while updating zone '%s'", zone)
                    sys.exit(1)

                logging.info("OK: Done updating zone '%s' with rrset '%s'.", zone, rrset_name)

    def add_zone(self, zone):
        """
        This is a placemark function to be implemented
        """
        logging.info("Creating zone '%s", zone)
        pass

    def query_zone(self, zone):
        """
        Query a specific DNS zone

        :return: dictionary

        """
        zone_api_url = self.uri + "zones/" + zone

        try:
            logging.debug("Check if the zone '%s' exists and is readable", zone)
            r = requests.get(zone_api_url, headers=self.headers)
        except Exception as e:
            logging.debug(e)
            logging.error("Failed to check zone '%s'.", zone)
            sys.exit(1)

        if r.status_code == 200:
            python_data = json.loads(r.text)
            logging.debug("Content of zone '%s: %s", zone, json.dumps(python_data, indent=4))
            return r, python_data
        else:
            logging.error("Unable to read zone '%s'.", zone)
            if r.status_code == 403:
                logging.info("Not enough rights to list '%s'", zone)
            logging.debug("Server returned status '%s': '%s'", r.status_code, r.text)

        return r, None

    def setup_api(self):
        """
        Setup api endpoint

        """
        self.headers = {
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Accept-Language': 'en-us',
            'Accept-Encoding': 'gzip, deflate',
            'X-API-Key': self.apikey
        }

        parsed_apihost = urllib.parse.urlparse(self.apihost)
        parsed_apihost = parsed_apihost._replace(path="")
        if not parsed_apihost.scheme:
            parsed_apihost = parsed_apihost._replace(scheme="https")
        self.uri = parsed_apihost.geturl()
        logging.debug("API Host set to '%s'", self.uri)

        self.uri = self.uri + self.apiversion + "/servers/localhost/"

        logging.debug("Full URL API set to '%s'", self.uri)

    def ensure_dot(self, text):
        """
        This function makes sure a string contains a dot at the end
        """
        if not text.endswith("."):
            text = text + "."
        return text
