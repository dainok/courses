#!/usr/bin/env python
from getpass import getpass
from netmiko import ConnectHandler

device = {
    "device_type": "paloalto_panos",
    "ip": "172.24.1.34",
    "username": "admin",
    "password": getpass(),
    "fast_cli": False,
}
net_connect = ConnectHandler(**device)
result = net_connect.send_command("show arp all", use_textfsm=True)
print(result)
net_connect.disconnect()
