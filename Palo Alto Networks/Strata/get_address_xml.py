#!/usr/bin/env python
from getpass import getpass
import requests
import urllib3
import xml.etree.ElementTree as ET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}

token = getpass("Token: ")

# Getting configured elements
xpaths = [
    "/config/shared/address/entry",  # Shared (Panorama)
    "/config/devices/entry/vsys/entry[@name='vsys1']/address",  # VSYS
]
for xpath in xpaths:
    url = f"https://172.24.1.34/api/?type=config&action=get&xpath={xpath}&key={token}"
    req = requests.get(url, headers=headers, verify=False)
    req.raise_for_status()
    if "/shared/" in xpath:
        location = "Shared"
        find_path = ".//result/"
    else:
        location = "VSYS"
        find_path = ".//result/address/"

    root = ET.fromstring(req.text)
    for entry in root.iterfind(find_path):
        name = entry.attrib["name"]
        address = entry.find("ip-netmask").text
        print(f"{name},{address},{location}")
