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
pdns-umanager --help
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
```

## Running

```
export PDNS_API_KEY="somekey"
export PDNS_SERVER_URL="https://pdns-api.example.org/"
pdns-umanager --file tests/test.yaml -d
2019-01-18 11:25:45,726 main+82:	DEBUG    [8981] PDNS_SERVER_URL: https://pdns-api.example.org/
2019-01-18 11:25:45,726 main+83:	DEBUG    [8981] PDNS_API_KEY: ****
2019-01-18 11:25:45,726 main+84:	DEBUG    [8981] CA_CERT_FILE: /etc/ssl/certs/ca-certificates.crt
2019-01-18 11:25:45,730 main+102:	DEBUG    [8981] Loaded zone content from file
2019-01-18 11:25:45,730 main+103:	DEBUG    [8981] {'example.org': {'wwww': {'records': ['web.frontend.example.org']}, 'graphs': {'type': 'cNaMe', 'records': ['web.frontend.monitoring.example.org']}, 'hello': {'type': 'A', 'records': ['10.235.2.21', '10.235.2.22']}, 'web': {'type': 'A', 'records': ['']}}, 'it.example.org': {'wwww': {'records': ['web.frontend.it.example.org']}}}
2019-01-18 11:25:45,731 config+58:	DEBUG    [8981] Setting up config for PDNSJanitor
2019-01-18 11:25:45,731 setup_api+230:	DEBUG    [8981] API Host set to 'https://pdns-api.example.org'
2019-01-18 11:25:45,731 setup_api+234:	DEBUG    [8981] Full URL API set to 'https://pdns-api.example.org/api/v1/servers/localhost/'
2019-01-18 11:25:45,731 zone_order+69:	DEBUG    [8981] Found the following declared zones:
example.org
it.example.org
2019-01-18 11:25:45,731 zone_order+75:	DEBUG    [8981] Sorted zones:
example.org
it.example.org
2019-01-18 11:25:45,731 run+81:	INFO     [8981] * ZONE: 'example.org'
2019-01-18 11:25:45,731 query_zone+193:	DEBUG    [8981] Check if the zone 'example.org.' exists and is readable
2019-01-18 11:25:45,743 _new_conn+813:	DEBUG    [8981] Starting new HTTPS connection (1): pdns-api.example.org:443
2019-01-18 11:25:45,995 _make_request+393:	DEBUG    [8981] https://pdns-api.example.org:443 "GET /api/v1/servers/localhost/zones/example.org. HTTP/1.1" 200 1457
2019-01-18 11:25:46,002 query_zone+202:	DEBUG    [8981] Content of zone 'example.org.: {
    "account": "",
    "api_rectify": false,
    "dnssec": false,
    "id": "example.org.",
    "kind": "Master",
    "last_check": 0,
    "masters": [],
    "name": "example.org.",
    "notified_serial": 2019011848,
    "nsec3narrow": false,
    "nsec3param": "",
    "rrsets": [
        {
            "comments": [],
            "name": "example.org.",
            "records": [
                {
                    "content": "hostmaster.example.org. 0. 2019011848 10800 3600 604800 3600",
                    "disabled": false
                }
            ],
            "ttl": 3600,
            "type": "SOA"
        },
        {
            "comments": [],
            "name": "example.org.",
            "records": [
                {
                    "content": "ns1.example.org.",
                    "disabled": false
                },
                {
                    "content": "ns2.example.org.",
                    "disabled": false
                }
            ],
            "ttl": 3600,
            "type": "NS"
        }
    ],
    "serial": 2019011848,
    "soa_edit": "",
    "soa_edit_api": "DEFAULT",
    "url": "/api/v1/servers/localhost/zones/example.org."
}
2019-01-18 11:25:46,002 run+85:	INFO     [8981] Zone 'example.org' exists and is readable
2019-01-18 11:25:46,002 run+93:	INFO     [8981] Applying updates for zone 'example.org'
2019-01-18 11:25:46,002 add_record+107:	DEBUG    [8981] RRSET_NAME: wwww
2019-01-18 11:25:46,002 add_record+115:	WARNING  [8981] Missing 'type' for record 'wwww' in zone 'example.org', using 'CNAME'
2019-01-18 11:25:46,002 add_record+120:	WARNING  [8981] Missing 'ttl' for record 'wwww' in zone 'example.org', using '150'
2019-01-18 11:25:46,003 add_record+126:	DEBUG    [8981]  RRSET_TYPE: CNAME
2019-01-18 11:25:46,003 add_record+127:	DEBUG    [8981]  RRSET_TTL: 150
2019-01-18 11:25:46,003 add_record+128:	DEBUG    [8981]  RRSET_RECORDS: ['web.frontend.example.org']
2019-01-18 11:25:46,003 add_record+144:	DEBUG    [8981]  RECORD_PAYLOAD: [{'content': 'web.frontend.example.org.', 'disabled': False, 'set-ptr': False}]
2019-01-18 11:25:46,003 add_record+158:	DEBUG    [8981] Patching zone 'example.org' with payload {'rrsets': [{'name': 'wwww.example.org.', 'type': 'cname', 'ttl': '150', 'records': [{'content': 'web.frontend.example.org.', 'disabled': False, 'set-ptr': False}], 'changetype': 'REPLACE'}]}
2019-01-18 11:25:46,006 _new_conn+813:	DEBUG    [8981] Starting new HTTPS connection (1): pdns-api.example.org:443
2019-01-18 11:25:46,291 _make_request+393:	DEBUG    [8981] https://pdns-api.example.org:443 "PATCH /api/v1/servers/localhost/zones/example.org. HTTP/1.1" 204 0
2019-01-18 11:25:46,298 add_record+174:	INFO     [8981] OK: Done updating zone 'example.org' with rrset 'wwww'.
2019-01-18 11:25:46,299 add_record+107:	DEBUG    [8981] RRSET_NAME: graphs
2019-01-18 11:25:46,299 add_record+120:	WARNING  [8981] Missing 'ttl' for record 'graphs' in zone 'example.org', using '150'
2019-01-18 11:25:46,299 add_record+126:	DEBUG    [8981]  RRSET_TYPE: cNaMe
2019-01-18 11:25:46,299 add_record+127:	DEBUG    [8981]  RRSET_TTL: 150
2019-01-18 11:25:46,300 add_record+128:	DEBUG    [8981]  RRSET_RECORDS: ['web.frontend.monitoring.example.org']
2019-01-18 11:25:46,302 add_record+144:	DEBUG    [8981]  RECORD_PAYLOAD: [{'content': 'web.frontend.monitoring.example.org.', 'disabled': False, 'set-ptr': False}]
2019-01-18 11:25:46,302 add_record+158:	DEBUG    [8981] Patching zone 'example.org' with payload {'rrsets': [{'name': 'graphs.example.org.', 'type': 'cname', 'ttl': '150', 'records': [{'content': 'web.frontend.monitoring.example.org.', 'disabled': False, 'set-ptr': False}], 'changetype': 'REPLACE'}]}
2019-01-18 11:25:46,306 _new_conn+813:	DEBUG    [8981] Starting new HTTPS connection (1): pdns-api.example.org:443
2019-01-18 11:25:49,602 _make_request+393:	DEBUG    [8981] https://pdns-api.example.org:443 "PATCH /api/v1/servers/localhost/zones/example.org. HTTP/1.1" 204 0
2019-01-18 11:25:49,605 add_record+174:	INFO     [8981] OK: Done updating zone 'example.org' with rrset 'graphs'.
2019-01-18 11:25:49,605 add_record+107:	DEBUG    [8981] RRSET_NAME: hello
2019-01-18 11:25:49,605 add_record+120:	WARNING  [8981] Missing 'ttl' for record 'hello' in zone 'example.org', using '150'
2019-01-18 11:25:49,605 add_record+126:	DEBUG    [8981]  RRSET_TYPE: A
2019-01-18 11:25:49,605 add_record+127:	DEBUG    [8981]  RRSET_TTL: 150
2019-01-18 11:25:49,605 add_record+128:	DEBUG    [8981]  RRSET_RECORDS: ['10.235.2.21', '10.235.2.22']
2019-01-18 11:25:49,605 add_record+144:	DEBUG    [8981]  RECORD_PAYLOAD: [{'content': '10.235.2.21', 'disabled': False, 'set-ptr': False}, {'content': '10.235.2.22', 'disabled': False, 'set-ptr': False}]
2019-01-18 11:25:49,605 add_record+158:	DEBUG    [8981] Patching zone 'example.org' with payload {'rrsets': [{'name': 'hello.example.org.', 'type': 'a', 'ttl': '150', 'records': [{'content': '10.235.2.21', 'disabled': False, 'set-ptr': False}, {'content': '10.235.2.22', 'disabled': False, 'set-ptr': False}], 'changetype': 'REPLACE'}]}
2019-01-18 11:25:49,607 _new_conn+813:	DEBUG    [8981] Starting new HTTPS connection (1): pdns-api.example.org:443
2019-01-18 11:25:50,758 _make_request+393:	DEBUG    [8981] https://pdns-api.example.org:443 "PATCH /api/v1/servers/localhost/zones/example.org. HTTP/1.1" 204 0
2019-01-18 11:25:50,764 add_record+174:	INFO     [8981] OK: Done updating zone 'example.org' with rrset 'hello'.
2019-01-18 11:25:50,764 add_record+107:	DEBUG    [8981] RRSET_NAME: web
2019-01-18 11:25:50,764 add_record+120:	WARNING  [8981] Missing 'ttl' for record 'web' in zone 'example.org', using '150'
2019-01-18 11:25:50,764 add_record+126:	DEBUG    [8981]  RRSET_TYPE: A
2019-01-18 11:25:50,764 add_record+127:	DEBUG    [8981]  RRSET_TTL: 150
2019-01-18 11:25:50,765 add_record+128:	DEBUG    [8981]  RRSET_RECORDS: ['']
2019-01-18 11:25:50,765 add_record+144:	DEBUG    [8981]  RECORD_PAYLOAD: []
2019-01-18 11:25:50,765 add_record+158:	DEBUG    [8981] Patching zone 'example.org' with payload {'rrsets': [{'name': 'web.example.org.', 'type': 'a', 'ttl': '150', 'records': [], 'changetype': 'REPLACE'}]}
2019-01-18 11:25:50,767 _new_conn+813:	DEBUG    [8981] Starting new HTTPS connection (1): pdns-api.example.org:443
2019-01-18 11:25:51,069 _make_request+393:	DEBUG    [8981] https://pdns-api.example.org:443 "PATCH /api/v1/servers/localhost/zones/example.org. HTTP/1.1" 204 0
2019-01-18 11:25:51,072 add_record+174:	INFO     [8981] OK: Done updating zone 'example.org' with rrset 'web'.
2019-01-18 11:25:51,072 run+81:	INFO     [8981] * ZONE: 'it.example.org'
2019-01-18 11:25:51,072 query_zone+193:	DEBUG    [8981] Check if the zone 'it.example.org.' exists and is readable
2019-01-18 11:25:51,074 _new_conn+813:	DEBUG    [8981] Starting new HTTPS connection (1): pdns-api.example.org:443
2019-01-18 11:25:51,346 _make_request+393:	DEBUG    [8981] https://pdns-api.example.org:443 "GET /api/v1/servers/localhost/zones/it.example.org. HTTP/1.1" 403 None
2019-01-18 11:25:51,352 query_zone+205:	ERROR    [8981] Unable to read zone 'it.example.org.'.
2019-01-18 11:25:51,352 query_zone+207:	INFO     [8981] Not enough rights to list 'it.example.org.'
2019-01-18 11:25:51,352 query_zone+208:	DEBUG    [8981] Server returned status '403': 'Not authorized for zone "it.example.org."!'
2019-01-18 11:25:51,352 run+90:	WARNING  [8981] Skipping zone 'it.example.org'...
```

## File Examples

Files must be in yaml format. Here is an example with inline comments on what to expect.
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
