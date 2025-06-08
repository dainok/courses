#!/usr/bin/env python
from getpass import getpass
import requests
import urllib3
import xml.etree.ElementTree as ET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

addresses = {
    "google-dns-1": "8.8.4.4",
    "google-dns-2": "8.8.8.8",
}
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}

token = getpass("Token: ")

# xpath = "/config/shared/address/entry" # Shared (Panorama)
xpath = "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address/entry" # VSYS

# Create elements
for name, ip in addresses.items():
    url = f"https://172.24.1.34/api/?type=config&action=set&xpath={xpath}"
    url = url + f"[@name='{name}']&element=<ip-netmask>{ip}</ip-netmask>"
    url = url + f"&key={token}"
    req = requests.get(url, headers=headers, verify=False)
    req.raise_for_status()
