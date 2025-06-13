#!/usr/bin/env python
from getpass import getpass
from panos.firewall import Firewall
from panos.objects import AddressObject

addresses = {
    "google-dns-1": "8.8.4.4",
    "google-dns-2": "8.8.8.8",
}

token = getpass("Token: ")
fw = Firewall("172.24.1.34", api_key=token)

# Create elements
for name, ip in addresses.items():
    fw.add(AddressObject(name=name, value=ip, type="ip-netmask")).create()
