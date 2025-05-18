#!/usr/bin/env python
from getpass import getpass
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

addresses = {
    "google-dns-1": "8.8.4.4",
    "google-dns-2": "8.8.8.8",
}
headers = {
    "Content-Type": "application/json",
    "X-PAN-KEY": getpass(),
}

# Create elements
for name, ip in addresses.items():
    url = f"https://172.25.10.4/restapi/v10.2/Objects/Addresses?name={name}&location=vsys&vsys=vsys1"
    data = {
        "entry": {
            "@name": name,
            "ip-netmask": ip,
        },
    }
    req = requests.post(url, json=data, headers=headers, verify=False)
    req.raise_for_status()
