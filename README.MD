# pdns-umanager

PDNS micro manager is a helper script for managing DNS zones in PowerDNS from 
a source file (or stdin).

It's a quick-win solution for those lacking interfaces or authorization for delegation 
and sub-zone management. 

## Usage

```
virtualenv -p python3 .venv
. .venv/bin/activate
pip3 install git+https://github.com/pan-net-security/pdns-umanager.git >/dev/null
pdnsumanager --help
usage: pdnsumanager [-h] [--pdns-server-url PDNS_SERVER_URL]
                    [--pdns-api-key PDNS_API_KEY] [-f FILE]
                    [--ca-cert-file CA_CERT_FILE] [-d] [--dry-run]

A utility to keep pdns zones tight and clean

optional arguments:
  -h, --help            show this help message and exit
  --pdns-server-url PDNS_SERVER_URL
                        The FQDN of the PowerDNS API endpoint
  --pdns-api-key PDNS_API_KEY
                        The API key for the zone
  -f FILE, --file FILE  A file to process. If not defined, stdin is assumed
  --ca-cert-file CA_CERT_FILE
                        A file containing root CA(s) for TLS verification
  -d, --debug           increase output verbosity
  --dry-run             don't make changes, only print
```

## Running

```
export PDNS_API_KEY="somekey"
export PDNS_SERVER_URL="https://pdns-api.example.org/"
pdns-umanager --file tests/test.yaml -d
2019-01-18 11:15:02,432 main+82:	DEBUG    [8774] PDNS_SERVER_URL: https://pdns-api.example.org/
2019-01-18 11:15:02,432 main+83:	DEBUG    [8774] PDNS_API_KEY: ****
2019-01-18 11:15:02,432 main+84:	DEBUG    [8774] CA_CERT_FILE: /etc/ssl/certs/ca-certificates.crt
2019-01-18 11:15:02,436 main+102:	DEBUG    [8774] Loaded zone content from file
2019-01-18 11:15:02,436 main+103:	DEBUG    [8774] {'example.org': {'wwww': {'records': ['web.frontend.example.org']}, 'monitoring': {'type': 'cNaMe', 'records': ['web.monitoring.example.org']}, 'hello': {'type': 'A', 'records': ['172.162.3.5', '172.162.3.6']}, 'web': {'type': 'A', 'records': ['']}}}
2019-01-18 11:15:02,436 config+58:	DEBUG    [8774] Setting up config for PDNSJanitor
2019-01-18 11:15:02,436 setup_api+230:	DEBUG    [8774] API Host set to 'https://pdns-api.example.org'
2019-01-18 11:15:02,436 setup_api+234:	DEBUG    [8774] Full URL API set to 'https://pdns-api.example.org/api/v1/servers/localhost/'
2019-01-18 11:15:02,436 zone_order+69:	DEBUG    [8774] Found the following declared zones:
example.org
2019-01-18 11:15:02,436 zone_order+75:	DEBUG    [8774] Sorted zones:
example.org
2019-01-18 11:15:02,436 run+81:	INFO     [8774] * ZONE: 'example.org'
2019-01-18 11:15:02,436 query_zone+193:	DEBUG    [8774] Check if the zone 'example.org.' exists and is readable
2019-01-18 11:15:02,450 _new_conn+813:	DEBUG    [8774] Starting new HTTPS connection (1): pdns-api.example.org:443
2019-01-18 11:15:02,698 _make_request+393:	DEBUG    [8774] https://pdns-api.example.org:443 "GET /api/v1/servers/localhost/zones/example.org. HTTP/1.1" 403 None
2019-01-18 11:15:02,704 query_zone+205:	ERROR    [8774] Unable to read zone 'example.org.'.
2019-01-18 11:15:02,705 query_zone+207:	INFO     [8774] Not enough rights to list 'example.org.'
2019-01-18 11:15:02,705 query_zone+208:	DEBUG    [8774] Server returned status '403': 'Not authorized for zone "example.org."!'
2019-01-18 11:15:02,705 run+90:	WARNING  [8774] Skipping zone 'example.org'...
```

## File format - yaml

```

# the data structure should be read as:
#
# <zone_name>:
#    <rrset_name>:
#        type: <CNAME|A>
#        records:
#            - <value2 ..>
#        ttls: <integer>
#
#
# DNS canonical format is optional (it's enforced in the script)

example.org:
   # 'type' can be omitted, defaults to 'cname'
   wwww:
        records:
          - "web.frontend.example.org"

   # 'type can also be explicit, case insensitive
   monitoring:
        type: 'cNaMe'
        records:
          - "web.monitoring.example.org"

   # records could be multiple values
   hello:
        type: "A"
        records:
          - "172.162.3.5"
          - "172.162.3.6"

   # empty records effectively delete the rrset
   web:
        type: "A"
        records:
          - ""

#   # reserved type, 'zone'; coming soon
#   monitoring.example.org:
#        type: "zone"

```