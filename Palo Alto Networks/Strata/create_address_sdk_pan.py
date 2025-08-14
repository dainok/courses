#!/usr/bin/env python
from getpass import getpass
import ssl
import xml.etree.ElementTree as ET
from pan import xapi

addresses = {
    "google-dns-1": "8.8.4.4",
    "google-dns-2": "8.8.8.8",
}

token = getpass("Token: ")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
fw = xapi.PanXapi(hostname="172.24.1.34", api_key=token, ssl_context=ctx)


# Create elements
for name, ip in addresses.items():
    # xpath = "/config/shared/address/entry" # Shared (Panorama)
    xpath = "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address/entry"  # VSYS
    xpath = xpath + f"[@name='{name}']"
    element = f"<ip-netmask>{ip}</ip-netmask>"
    fw.set(xpath=xpath, element=element)
