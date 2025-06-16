#!/usr/bin/env python
from getpass import getpass
from panos.firewall import Firewall
from panos.objects import AddressObject

token = getpass("Token: ")
fw = Firewall("172.24.1.34", api_key=token)

# Getting configured elements
for entry in AddressObject.refreshall(fw):
    name = entry.name
    address = entry.value
    location = entry.vsys
    print(f"{name},{address},{location}")
