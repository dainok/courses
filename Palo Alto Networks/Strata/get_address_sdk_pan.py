#!/usr/bin/env python
from getpass import getpass
import ssl
from pan import xapi

token = getpass("Token: ")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
fw = xapi.PanXapi(hostname="172.24.1.34", api_key=token, ssl_context=ctx)

# Getting configured elements
xpaths = [
    "/config/shared/address/entry",  # Shared (Panorama)
    "/config/devices/entry/vsys/entry[@name='vsys1']/address",  # VSYS
]
for xpath in xpaths:
    if "/shared/" in xpath:
        location = "Shared"
        find_path = ".//result/"
    else:
        location = "VSYS"
        find_path = ".//result/address/"

    fw.get(xpath=xpath)
    root = fw.element_root
    for entry in root.iterfind(find_path):
        name = entry.attrib["name"]
        address = entry.find("ip-netmask").text
        print(f"{name},{address},{location}")
