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
commands = [
    'delete rulebase security rules "rule1"',
    "delete network virtual-wire default-vwire",
    "delete zone trust network virtual-wire",
    "delete zone untrust network virtual-wire",
    "delete network interface ethernet ethernet1/1 virtual-wire",
    "delete network interface ethernet ethernet1/2 virtual-wire",
    "delete zone trust",
    "delete zone untrust",
    "delete network interface ethernet ethernet1/1",
    "delete network interface ethernet ethernet1/2",
    "commit",
]
net_connect = ConnectHandler(**device)
net_connect.send_config_set(commands)
net_connect.disconnect()
