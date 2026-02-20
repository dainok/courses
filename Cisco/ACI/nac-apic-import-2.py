#!/usr/bin/env python3
"""Terraform importer for Cisco APIC using NaC modeling."""
import yaml
import subprocess
from pathlib import Path

DATA_DIR = "./data"

import_cmds = []
def add_import_cmd(cls, mod, path, dn):
    cmd = (
        f'terraform import module.aci.module.{mod}[\"{path}\"].aci_rest_managed.{cls} {dn}'
    )
    import_cmds.append(cmd)

data_path = Path(DATA_DIR)
for nac_file in data_path.rglob("*.nac.yaml"):
    print(f"Loading {nac_file}...")
    nac_data = None
    with open(nac_file, "r", encoding="utf-8") as fh:
        nac_data = yaml.safe_load(fh)
    apic_data = nac_data.get("apic", {})

    # Get Tenants
    for tenant_data in apic_data.get("tenants"):
        tenant_name = tenant_data.get("name")
        tenant_dn = f"uni/tn-{tenant_name}"
        tenant_path = tenant_name
        add_import_cmd(cls="fvTenant", mod="aci_tenant", path=tenant_path, dn=tenant_dn)

        # Get VRFs
        for vrf_data in tenant_data.get("vrfs", []):
            vrf_name = vrf_data.get("name")
            vrf_dn = f"{tenant_dn}/ctx-{vrf_name}"
            vrf_path = f"{tenant_name}/{vrf_name}"
            add_import_cmd(cls="fvCtx", mod="aci_vrf", path=vrf_path, dn=vrf_dn)
            add_import_cmd(cls="fvRsBgpCtxPol", mod="aci_vrf", path=vrf_path, dn=f"{vrf_dn}/rsbgpCtxPol")
            add_import_cmd(cls="fvRsCtxToExtRouteTagPol", mod="aci_vrf", path=vrf_path, dn=f"{vrf_dn}/rsctxToExtRouteTagPol")
            add_import_cmd(cls="fvRsOspfCtxPol", mod="aci_vrf", path=vrf_path, dn=f"{vrf_dn}/rsospfCtxPol")
            add_import_cmd(cls="vzAny", mod="aci_vrf", path=vrf_path, dn=f"{vrf_dn}/any")

        # Get BrideDomains
        for bd_data in tenant_data.get("bridge_domains", []):
            bd_name = bd_data.get("name")
            bd_dn = f"{tenant_dn}/BD-{bd_name}"
            bd_path = f"{tenant_name}/{bd_name}"
            add_import_cmd(cls="fvBD", mod="aci_bridge_domain", path=bd_path, dn=bd_dn)
            add_import_cmd(cls="fvRsCtx", mod="aci_bridge_domain", path=bd_path, dn=f"{bd_dn}/rsctx")

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
