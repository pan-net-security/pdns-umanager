import logging
import os
import argparse
import sys
import yaml

import pdnsumanager.pdnsjanitor as janitor


PDNS_SERVER_URL = os.getenv('PDNS_SERVER_URL')
PDNS_API_KEY = os.getenv('PDNS_API_KEY')

def main():

    parser = argparse.ArgumentParser(
        description="A utility to keep pdns zones tight and clean"
    )

    parser.add_argument(
        "--pdns-server-url",
        help="The FQDN of the PowerDNS API endpoint",
        action='store',
        dest='pdns_server_url',
        default=os.environ.get('PDNS_SERVER_URL'),
        type=str
    )

    parser.add_argument(
        "--pdns-api-key",
        help="The API key for the zone",
        action='store',
        dest='pdns_api_key',
        default=os.environ.get('PDNS_API_KEY'),
        type=str
    )

    parser.add_argument(
        "-f",
        "--file",
        help="A file to process. If not defined, stdin is assumed",
        action='store',
        dest='file',
        default="",
        type=str
    )

    parser.add_argument(
        "--ca-cert-file",
        help="A file containing root CA(s) for TLS verification",
        action='store',
        dest='ca_cert_file',
        default=os.environ.get('CA_CERT_FILE', "/etc/ssl/certs/ca-certificates.crt"),
        type=str
    )

    parser.add_argument("-d", "--debug", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("--dry-run", help="don't make changes, only print",
                        action="store_true")

    args = parser.parse_args()
    config = vars(args)

    if config['debug']:
        logLevel = logging.DEBUG
        logFormat = '%(asctime)s %(funcName)s+%(lineno)s:\t%(levelname)-8s [%(process)d] %(message)s'
    else:
        logLevel = logging.INFO
        logFormat = '%(asctime)s: %(levelname)-8s [%(process)d] %(message)s'


    if not config['pdns_server_url']:
        msg = "PowerDNS URL is not defined"
        parser.error(msg)

    if not config['pdns_api_key']:
        msg = "PowerDNS API KEY is not defined"
        parser.error(msg)

    logging.basicConfig(level=logLevel,format=logFormat)

    logging.debug("PDNS_SERVER_URL: %s", config['pdns_server_url'])
    logging.debug("PDNS_API_KEY: ****")
    logging.debug("CA_CERT_FILE: %s", config['ca_cert_file'])

    if not os.path.isfile(config['ca_cert_file']):
        logging.warning("Unable to find '%s'", config['ca_cert_file'])
    else:
        os.environ['REQUESTS_CA_BUNDLE'] = config['ca_cert_file']

    data_yaml = ""
    if(len(args.file)==0):
        try:
            data_yaml = yaml.safe_load(sys.stdin)
            logging.debug("Loaded zone content from stdin")
            logging.debug(data_yaml)
        except Exception as e:
            logging.error(e)
    else:
        try:
            data_yaml = yaml.safe_load(open(args.file,'r').read())
            logging.debug("Loaded zone content from file")
            logging.debug(data_yaml)
        except Exception as e:
            logging.error(e)

    janitor_object = janitor.PDNSJanitor()
    janitor_object.config(api_host=config['pdns_server_url'],
                            api_key=config['pdns_api_key'],
                            api_version="/api/v1",
                            zones_data=data_yaml)
    janitor_object.run()


if __name__ == '__main__':
    main()