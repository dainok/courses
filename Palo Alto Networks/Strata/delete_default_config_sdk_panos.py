#!/usr/bin/env python
from getpass import getpass
from panos.firewall import Firewall
from panos.policies import Rulebase, SecurityRule
from panos.network import VirtualWire, Zone, EthernetInterface

token = getpass("Token: ")
fw = Firewall("172.24.1.34", api_key=token)

# Delete default rule
rulebase = Rulebase.refreshall(fw)
for rule in SecurityRule.refreshall(rulebase):
    if rule.name == "rule1":
        rule.delete()

# Delete default vwire
for vwire in VirtualWire.refreshall(fw):
    if vwire.name == "default-vwire":
        vwire.delete()

# Delete default zones
for zone in Zone.refreshall(fw):
    if zone.name in ["trust", "untrust"]:
        zone.delete()

# Delete default interfaces
for intf in EthernetInterface.refreshall(fw):
    if intf.name in ["ethernet1/1", "ethernet1/2"]:
        intf.delete()
