#!/usr/bin/env python
from getpass import getpass
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "X-PAN-KEY": getpass(),
}

# Getting configured elements
url = f"https://172.25.10.4/restapi/v10.2/Objects/Addresses?location=vsys&vsys=vsys1"
req = requests.get(url, headers=headers, verify=False)
req.raise_for_status()

if req.json()["result"].get("entry"):
    for entry in req.json()["result"]["entry"]:
        print(f"{entry['@name']},{entry['ip-netmask']},{entry['@location']}")
