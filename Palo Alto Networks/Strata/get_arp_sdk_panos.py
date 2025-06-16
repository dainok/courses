#!/usr/bin/env python
from getpass import getpass
from panos.firewall import Firewall

token = getpass("Token: ")
fw = Firewall("172.24.1.34", api_key=token)

# Getting elements
root = fw.op("<show><arp><entry name='all'/></arp></show>", cmd_xml=False)
for entry in root.iterfind(".//result/entries/"):
    interface = entry.find("interface").text
    ip = entry.find("ip").text
    mac = entry.find("mac").text
    print(f"{interface},{ip},{mac}")
