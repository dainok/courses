#!/usr/bin/env python3
"""
NaC importer for Cisco APIC.

Download Cobra SDK from the APIC: https://172.25.82.1/cobra/_downloads/
Install modules with PIP: pip install *whl
"""
import sys
import os
import urllib3
import yaml
import subprocess
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

import_cmds = []

MAPPING = [
    {
        "module": "aci_tenant",
        "class": "fvTenant",
    },
    {
        "module": "aci_vrf",
        "class": "fvCtx",
    },
    {
        "module": "aci_bridge_domain",
        "class": "fvBD",
    },
    {
        "module": "aci_vrf",
        "class": "fvRsBgpCtxPol",
    },
    {
        "module": "aci_vrf",
        "class": "fvRsCtxToExtRouteTagPol",
    },
    {
        "module": "aci_vrf",
        "class": "fvRsOspfCtxPol",
    },
    {
        "module": "aci_vrf",
        "class": "vzAny",
    },
    {
        "module": "aci_bridge_domain",
        "class": "fvRsCtx",
    },
]
IGNORED_TENANTS = [
    "infra",
    "mgmt",
    "common",
]

def get_nac_module(cls):
    for map in MAPPING:
        if cls == map["class"]:
            return map["module"]
    return None

def add_import_cmd(cls, path, dn):
    nac_module = get_nac_module(cls)
    if not nac_module:
        # print(f"Class {cls} for dn={dn} is not supported")
        return
    cmd = (
        f'terraform import module.aci.module.{nac_module}[\"{path}\"].aci_rest_managed.{cls} {dn}'
    )
    import_cmds.append(cmd)
    return


def import_object(obj, parent=None):
    # print(toJSONStr(obj, prettyPrint=True))
    if parent:
        path = f"{parent}/{obj.name}"
    else:
        path = obj.name
    cls = obj.meta.moClassName
    nac_module = get_nac_module(cls)
    if not nac_module:
        # print(f"Class {cls} for dn={dn} is not supported")
        return
    cmd = (
        f'terraform import module.aci.module.{nac_module}[\"{path}\"].aci_rest_managed.{cls} {obj.dn}'
    )
    import_cmds.append(cmd)
    return

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
    import_object(tenant)
    nac_tenant_data = {}
    nac_tenant_data["name"] = tenant.name
    if tenant.descr:
        nac_tenant_data["description"] = tenant.descr

    # Get VRFs
    fvCtx_objs = moDir.lookupByClass('fvCtx', parentDn=tenant.dn)
    if fvCtx_objs:
        nac_tenant_data["vrfs"] = []
    for vrf in fvCtx_objs:
        import_object(vrf, parent=tenant.name)
        add_import_cmd(cls="fvRsBgpCtxPol", path=f"{tenant.name}/{vrf.name}", dn=f"{vrf.dn}/rsbgpCtxPol")
        add_import_cmd(cls="fvRsCtxToExtRouteTagPol", path=f"{tenant.name}/{vrf.name}", dn=f"{vrf.dn}/rsctxToExtRouteTagPol")
        add_import_cmd(cls="fvRsOspfCtxPol", path=f"{tenant.name}/{vrf.name}", dn=f"{vrf.dn}/rsospfCtxPol")
        add_import_cmd(cls="vzAny", path=f"{tenant.name}/{vrf.name}", dn=f"{vrf.dn}/any")
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
        import_object(bd, parent=tenant.name)
        add_import_cmd(cls="fvRsCtx", path=f"{tenant.name}/{bd.name}", dn=f"{bd.dn}/rsctx")
        nac_bd_data = {}
        nac_bd_data["name"] = bd.name
        if bd.descr:
            nac_bd_data["description"] = bd.descr
        nac_tenant_data["bridge_domains"].append(nac_bd_data)

        # Find VRF
        vrf = None
        for child in bd.children:
            if child.meta.moClassName == "fvRsCtx":
                vrf = moDir.lookupByDn(child.tDn)
                break
        nac_bd_data["vrf"] = vrf.name
        
    # Dump data
    with open(f"data/tenant-{tenant.name}.nac.yaml", "w", encoding="utf-8") as fh:
        nac_data = {"apic": {"tenants": [nac_tenant_data]}}
        yaml.dump(nac_data, fh, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
# Terraform import
for cmd in import_cmds:
    print(cmd)
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    if result.returncode != 0 and "Resource already managed by Terraform" not in result.stderr:
        print("CMD:", cmd)
        print("RC:", result.returncode)
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)
        raise
