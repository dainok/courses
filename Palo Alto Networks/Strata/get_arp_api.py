#!/usr/bin/env python
from getpass import getpass
import requests
import urllib3
import xml.etree.ElementTree as ET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}
url = "https://172.24.1.34/api/?type=op&cmd=<show><arp><entry name = 'all'/></arp></show>&key="
url = url + getpass("Token: ")
req = requests.get(url, headers=headers, verify=False)
req.raise_for_status()

root = ET.fromstring(req.text)
for entry in root.iterfind(".//result/entries/"):
    interface = entry.find("interface").text
    ip = entry.find("ip").text
    mac = entry.find("mac").text
    print(f"{interface},{ip},{mac}")
