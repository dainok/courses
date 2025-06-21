#!/usr/bin/env python
from getpass import getpass
import ssl
from pan import xapi

token = getpass("Token: ")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
fw = xapi.PanXapi(hostname="172.24.1.34", api_key=token, ssl_context=ctx)

# Getting elements
fw.op(cmd="<show><arp><entry name='all'/></arp></show>", cmd_xml=False)
root = fw.element_root
for entry in root.iterfind(".//result/entries/"):
    interface = entry.find("interface").text
    ip = entry.find("ip").text
    mac = entry.find("mac").text
    print(f"{interface},{ip},{mac}")
