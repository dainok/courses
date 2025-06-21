#!/usr/bin/env python
from getpass import getpass
import ssl
from pan import xapi

token = getpass("Token: ")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
fw = xapi.PanXapi(hostname="172.24.1.34", api_key=token, ssl_context=ctx)

# Defining paths
xpaths = [
    "/config/devices/entry/vsys/entry[@name='vsys1']/rulebase/security/rules/entry[@name='rule1']",
    "/config/devices/entry/network/virtual-wire/entry[@name='default-vwire']",
    "/config/devices/entry/vsys/entry[@name='vsys1']/zone/entry[@name='trust']",
    "/config/devices/entry/vsys/entry[@name='vsys1']/zone/entry[@name='untrust']",
    "/config/devices/entry/vsys/entry[@name='vsys1']/import/network/interface/member[text()='ethernet1/1']",
    "/config/devices/entry/vsys/entry[@name='vsys1']/import/network/interface/member[text()='ethernet1/2']",
    "/config/devices/entry/network/interface/ethernet/entry[@name='ethernet1/1']",
    "/config/devices/entry/network/interface/ethernet/entry[@name='ethernet1/2']",

]
for xpath in xpaths:
    fw.delete(xpath=xpath)
