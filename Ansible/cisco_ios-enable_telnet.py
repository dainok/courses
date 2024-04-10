#!/usr/bin/env python3
"""Connect to a Cisco IOS device via telnet and enable SSH."""

# netmiko==4.3.0

from pprint import pprint
from netmiko import ConnectHandler
from getpass import getpass

host = input("Enter hostname:       ")
user = input("Enter username: ")
password = getpass(prompt="Enter password: ")

device = {
    "host": host,
    "username": user,
    "password": password,
    "verbose": False,
}

output = ""
net_connect = ConnectHandler(**device, device_type="cisco_ios_telnet")
output += net_connect.send_config_set("ip domain name example.com")
output += net_connect.send_config_set("crypto key generate rsa modulus 2048")
output += net_connect.send_config_set("ip ssh version 2")
output += net_connect.send_config_set([
    "line vty 0 4",
    "transport input telnet ssh",
])
net_connect.disconnect()
pprint(output)

net_connect = ConnectHandler(**device, device_type="cisco_ios")
net_connect.disconnect()
print("*" * 70)
print(f"SSH is enabled on {device['host']}")
print("*" * 70)
