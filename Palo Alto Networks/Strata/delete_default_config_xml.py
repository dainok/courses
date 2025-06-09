#!/usr/bin/env python
from getpass import getpass
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}

# Defining paths
xpaths = [
    "/config/devices/entry/vsys/entry[@name='vsys1']/rulebase/security/rules/entry[@name='rule1']",
    "/config/devices/entry/network/virtual-wire/entry[@name='default-vwire']",
    "/config/devices/entry/vsys/entry[@name='vsys1']/zone/entry[@name='trust']",
    "/config/devices/entry/vsys/entry[@name='vsys1']/zone/entry[@name='untrust']",
    "/config/devices/entry/vsys/entry[@name='vsys1']/import/network/interface/member[text()='ethernet1/1']",
    "/config/devices/entry/vsys/entry[@name='vsys1']/import/network/interface/member[text()='ethernet1/2']",
    "/config/devices/entry/network/interface/ethernet/entry[@name='ethernet1/1']",
    "/config/devices/entry/network/interface/ethernet/entry[@name='ethernet1/2']",
]
# Deleting objects
for xpath in xpaths:
    url = f"https://172.24.1.34/api/?type=config&action=delete&xpath={xpath}&key={token}"
    req = requests.get(url, headers=headers, verify=False)
    # req.raise_for_status()
