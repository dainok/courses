#!/usr/bin/env python
from getpass import getpass
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "X-PAN-KEY": getpass("Token: "),
}

# Defining API
base_url = "https://172.24.1.34/restapi/v10.2"
urls = [
    f"{base_url}/Policies/SecurityRules?name=rule1&location=vsys&vsys=vsys1",
    f"{base_url}/Network/VirtualWires?name=default-vwire",
    f"{base_url}/Network/Zones?name=trust&location=vsys&vsys=vsys1",
    f"{base_url}/Network/Zones?name=untrust&location=vsys&vsys=vsys1",
    # f"{base_url}/Network/EthernetInterfaces?name=ethernet1/1", # Validation error
    # f"{base_url}/Network/EthernetInterfaces?name=ethernet1/2", # Validation error
]
# Deleting objects
for url in urls:
    req = requests.delete(url, headers=headers, verify=False)
    # req.raise_for_status()
