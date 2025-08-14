#!/usr/bin/env python
"""Get ARP table from a FW and parse it in JSON format."""

import logging
from netmiko import ConnectHandler
from getpass import getpass

logging.basicConfig(level=logging.INFO)

device = {
    "device_type": "paloalto_panos",
    "host": "172.25.10.4",
    "username": "admin",
    "password": getpass("Password: "),
}

# Execute a command
command = "show arp all"
with ConnectHandler(**device) as net_connect:
    output = net_connect.send_command(command, expect_string=r">", use_textfsm=True)
    net_connect.disconnect()

print(output)
