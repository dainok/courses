#!/usr/bin/env python
from getpass import getpass
import requests
import xml.etree.ElementTree as ET

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}
url = f"https://172.25.10.4/api/?type=op&cmd=<show><arp><entry name = 'all'/></arp></show>&key="
url = url + getpass()
req = requests.get(url, headers=headers, verify=False)
req.raise_for_status()

root = ET.fromstring(req.text)
for entry in root.iterfind(".//result/entries/"):
    interface = entry.find('interface').text
    ip = entry.find('ip').text
    mac = entry.find('mac').text
    print(f"{interface},{ip},{mac}")
