#!/usr/bin/env python3
"""
NaC importer for Cisco APIC.

Download Cobra SDK from the APIC: https://172.25.82.1/cobra/_downloads/
Install modules with PIP: pip install *whl
"""
import os
import urllib3
import yaml
from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.internal.codec.jsoncodec import toJSONStr
# from cobra.model.fv import Tenant, Ctx
# import cobra.model.fv
# import cobra.model.ip
# import cobra.model.vz
# import cobra.model.pol
# import cobra.model.vpc
# import cobra.model.fvns
# import cobra.model.lacp
# import cobra.model.phys
# import cobra.model.infra
# import cobra.model.l3ext
# import cobra.model.fabric

urllib3.disable_warnings()

IGNORED_TENANTS = [
    "infra",
    "mgmt",
    "common",
]

def parse_boolean(s):
    if s.lower() in ["yes", "true"]:
        return True
    if s.lower() in ["no", "false"]:
        return False
    if not s:
        return False
    return bool(s)
    
# Login
apic_address = os.environ.get("ACI_ADDRESS")
apic_username = os.environ.get("ACI_USERNAME")
apic_password = os.environ.get("ACI_PASSWORD")
session = LoginSession(f"https://{apic_address}", apic_username, apic_password)
moDir = MoDirectory(session)
moDir.login()

os.makedirs("data", exist_ok=True)

# Tests
# dn = "uni/tn-TenantTest/ctx-Default_VRF"
# obj = moDir.lookupByDn(dn)
# attrs = list(dir(obj))
# for attr in attrs:
#     print(attr, "=", getattr(obj, attr))
# sys.exit(0)

# Get Tenants
fvTenant_objs = moDir.lookupByClass("fvTenant")
for tenant in fvTenant_objs:
    if tenant.name in IGNORED_TENANTS:
        # Ignore tenant
        continue
    nac_tenant_data = {}
    nac_tenant_data["name"] = tenant.name
    if tenant.descr:
        nac_tenant_data["description"] = tenant.descr

    # Get VRFs
    fvCtx_objs = moDir.lookupByClass('fvCtx', parentDn=tenant.dn)
    if fvCtx_objs:
        nac_tenant_data["vrfs"] = []
    for vrf in fvCtx_objs:
        nac_vrf_data = {}
        nac_vrf_data["name"] = vrf.name
        nac_vrf_data["enforcement_preference"] = vrf.pcEnfPref
        if vrf.descr:
            nac_vrf_data["description"] = vrf.descr
        nac_tenant_data["vrfs"].append(nac_vrf_data)

    # Get BrideDomains
    fvBD_objs = moDir.lookupByClass('fvBD', parentDn=tenant.dn, subtree="children")
    if fvBD_objs:
        nac_tenant_data["bridge_domains"] = []
    for bd in fvBD_objs:
        nac_bd_data = {}
        nac_bd_data["name"] = bd.name
        nac_bd_data["multicast_arp_drop"] = parse_boolean(bd.mcastARPDrop)
        nac_bd_data["ip_dataplane_learning"] = parse_boolean(bd.ipLearning)
        nac_bd_data["unknown_unicast"] = bd.unkMacUcastAct
        if bd.descr:
            nac_bd_data["description"] = bd.descr
        nac_tenant_data["bridge_domains"].append(nac_bd_data)

        # Find VRF
        for child in bd.children:
            if child.meta.moClassName == "fvRsCtx":
                vrf = moDir.lookupByDn(child.tDn)
                nac_bd_data["vrf"] = vrf.name
                break
        
    # Dump data
    with open(f"data/tenant-{tenant.name}.nac.yaml", "w", encoding="utf-8") as fh:
        nac_data = {"apic": {"tenants": [nac_tenant_data]}}
        yaml.dump(nac_data, fh, default_flow_style=False, sort_keys=False, allow_unicode=True)
