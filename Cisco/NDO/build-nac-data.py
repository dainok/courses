#!/usr/bin/env python3

import os
import yaml
from jinja2 import Environment, FileSystemLoader
from infra import Infra, Site
from pathlib import Path
import subprocess  # nosec
import shutil


def dump_yaml(data: dict, filename: str):
    """Dump YAML file and lint via yamlfmt."""
    file_path = Path(filename)
    with open(file_path, "w", encoding="utf-8") as fh:
        yaml.dump(
            data,
            fh,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=True,
            indent=2,
        )

    yamlfmt_path = shutil.which("yamlfmt")
    if not yamlfmt_path:
        yamlfmt_path = shutil.which("yamlfmt.exe")
    if not yamlfmt_path:
        return

    subprocess.run([yamlfmt_path, file_path])  # nosec


config_file = "config.yaml"
secret_file = "secrets.yaml"  # nosec

# Reading config file
with open(secret_file, "r", encoding="utf-8") as f:
    secrets = yaml.safe_load(f)

# Reading secret file
with open(config_file, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

config_ndo_schema = config["ndo"]["schema"]
config_ndo_tenant = config["ndo"]["tenant"]
config_ndo_templates = config["ndo"]["templates"]

ndo_data = {}
ndo_mi_data = {}
ndo_rm_data = {}
ndo_stretched_data = {}

# Reading input data
i = Infra()


# ***************************************************************************
# Dumping Terraform vars files
# ***************************************************************************

env = Environment(loader=FileSystemLoader("."), autoescape=True)
template_tfvars = env.get_template("templates/terraform.tfvars.j2")
template_variables = env.get_template("templates/variables.tf.j2")
template_apic_custom = env.get_template("templates/apic-custom.tf.j2")
template_apic_main = env.get_template("templates/apic-main.tf.j2")
template_apic_providers = env.get_template("templates/apic-providers.tf.j2")
template_apic_versions = env.get_template("templates/apic-versions.tf.j2")
template_ndo_main = env.get_template("templates/ndo-main.tf.j2")
template_ndo_providers = env.get_template("templates/ndo-providers.tf.j2")
template_ndo_versions = env.get_template("templates/ndo-versions.tf.j2")
tfvars = {
    "site-shared": {
        "main.tf": template_ndo_main.render(keep_trailing_newline=True),
        "providers.tf": template_ndo_providers.render(keep_trailing_newline=True),
        "versions.tf": template_ndo_versions.render(keep_trailing_newline=True),
        "variables.tf": template_variables.render(keep_trailing_newline=True),
        "terraform.tfvars": template_tfvars.render(i.get_apic_login_data_by_site(Site("SHARED"))),
    },
    "site-mi": {
        "custom.tf": template_apic_custom.render(site=Site("MI").value.lower()),
        "main.tf": template_apic_main.render(site=Site("MI").value.lower()),
        "providers.tf": template_apic_providers.render(site=Site("MI").value.lower()),
        "versions.tf": template_apic_versions.render(site=Site("MI").value.lower()),
        "variables.tf": template_variables.render(),
        "terraform.tfvars": template_tfvars.render(i.get_apic_login_data_by_site(Site("MI"))),
    },
    "site-rm": {
        "custom.tf": template_apic_custom.render(site=Site("RM").value.lower()),
        "main.tf": template_apic_main.render(site=Site("RM").value.lower()),
        "providers.tf": template_apic_providers.render(site=Site("RM").value.lower()),
        "versions.tf": template_apic_versions.render(site=Site("RM").value.lower()),
        "variables.tf": template_variables.render(),
        "terraform.tfvars": template_tfvars.render(i.get_apic_login_data_by_site(Site("RM"))),
    },
}
os.makedirs("nac-data", exist_ok=True)
for dir, templates in tfvars.items():
    os.makedirs(dir, exist_ok=True)
    for file, content in templates.items():
        with open(f"{dir}/{file}", "w", encoding="utf-8") as fh:
            fh.write(content)


# ***************************************************************************
# Preparing NDO sites (NaC)
# ***************************************************************************

ndo_data["sites"] = [
    {
        "apic_urls": [
            apic.url,
        ],
        "name": apic.name,
    }
    for apic in i.apics
]


# ***************************************************************************
# Preparing NDO shared templates (NaC)
# ***************************************************************************

# Template: contracts (deploy order: 1)
ndo_template_shared_contracts_data = {
    "name": config_ndo_templates["contracts"]["name"],
    "deploy_order": config_ndo_templates["contracts"]["deploy_order"],
    "sites": i.get_apic_names(),
    "tenant": config_ndo_tenant,
    "contracts": [],
    "filters": config_ndo_templates["site_stretched"].get("filters", []),
}
for vrf in i.vrfs:
    ndo_template_shared_contracts_data["contracts"].append(
        {
            "name": f"vzAny-{vrf.name}_Contract",
            "scope": "context",  # Scope: VRF
            "type": "bothWay",  # Apply: both directions
            "filters": [
                {
                    "name": "ANY_Filter",
                }
            ],
        }
    )

# Template: stretched_vrf (deploy order: 1)
ndo_template_shared_vrf_data = {
    "name": config_ndo_templates["stretched_vrf"]["name"],
    "deploy_order": config_ndo_templates["stretched_vrf"]["deploy_order"],
    "sites": i.get_apic_names(),
    "tenant": config_ndo_tenant,
    "vrfs": [],
}
for vrf in i.vrfs:
    ndo_template_shared_vrf_data["vrfs"].append(
        {
            "name": f"{vrf.name}_VRF",
            "data_plane_learning": True,
            "vzany": True,
            "contracts": {
                "consumers": [
                    {
                        "name": f"vzAny-{vrf.name}_Contract",
                        "template": config_ndo_templates["contracts"]["name"],
                    }
                ],
                "providers": [
                    {
                        "name": f"vzAny-{vrf.name}_Contract",
                        "template": config_ndo_templates["contracts"]["name"],
                    }
                ],
            },
        }
    )

# Template: stretched_extepg (deploy order: 3)
ndo_template_shared_extepg_data = {
    "name": config_ndo_templates["stretched_extepg"]["name"],
    "deploy_order": config_ndo_templates["stretched_extepg"]["deploy_order"],
    "sites": i.get_apic_names(),
    "tenant": config_ndo_tenant,
}

# ***************************************************************************
# Preparing NDO stretched template (NaC)
# ***************************************************************************

# Template: site_stretched (deploy order: 2)
ndo_template_stretched_data = {
    "name": config_ndo_templates["site_stretched"]["name"],
    "deploy_order": config_ndo_templates["site_stretched"]["deploy_order"],
    "sites": i.get_apic_names(),
    "tenant": config_ndo_tenant,
    "bridge_domains": i.get_tenant_bridge_domains(site=Site("SHARED")),
    "application_profiles": i.get_tenant_application_profiles(site=Site("SHARED")),
}

# ***************************************************************************
# Preparing NDO site template (NaC)
# ***************************************************************************

# Template: site_mi (deploy order: 2)
ndo_template_mi_data = {
    "name": config_ndo_templates["site_mi"]["name"],
    "deploy_order": config_ndo_templates["site_mi"]["deploy_order"],
    "sites": [i.get_apic_name_by_site(Site("MI"))],
    "tenant": config_ndo_tenant,
    "bridge_domains": i.get_tenant_bridge_domains(site=Site("MI")),
    "application_profiles": i.get_tenant_application_profiles(site=Site("MI")),
}

# Template: site_rm (deploy order: 2)
ndo_template_rm_data = {
    "name": config_ndo_templates["site_rm"]["name"],
    "deploy_order": config_ndo_templates["site_rm"]["deploy_order"],
    "sites": [i.get_apic_name_by_site(Site("RM"))],
    "tenant": config_ndo_tenant,
    "bridge_domains": i.get_tenant_bridge_domains(site=Site("RM")),
    "application_profiles": i.get_tenant_application_profiles(site=Site("RM")),
}


# ***************************************************************************
# Preparing NDO schemas (NaC)
# ***************************************************************************

ndo_data["schemas"] = [
    {
        "name": config["ndo"]["schema"],
        "templates": [
            ndo_template_shared_contracts_data,
            ndo_template_shared_extepg_data,
            ndo_template_shared_vrf_data,
        ],
    }
]

ndo_stretched_data["schemas"] = [
    {
        "name": config["ndo"]["schema"],
        "templates": [
            ndo_template_stretched_data,
        ],
    }
]

ndo_mi_data["schemas"] = [
    {
        "name": config["ndo"]["schema"],
        "templates": [
            ndo_template_mi_data,
        ],
    }
]

ndo_rm_data["schemas"] = [
    {
        "name": config["ndo"]["schema"],
        "templates": [
            ndo_template_rm_data,
        ],
    }
]

# ***************************************************************************
# Preparing NDO tenants (NaC)
# ***************************************************************************

ndo_data["tenants"] = [
    {
        "name": config_ndo_tenant,
        "sites": [{"name": apic_name} for apic_name in i.get_apic_names()],
    }
]


# ***************************************************************************
# Dumping NDO data (NaC)
# ***************************************************************************

dump_yaml({"ndo": ndo_data}, filename="nac-data/ndo.nac.yaml")
dump_yaml({"ndo": ndo_stretched_data}, filename="nac-data/ndo-stretched.nac.yaml")
dump_yaml({"ndo": ndo_mi_data}, filename="nac-data/ndo-mi.nac.yaml")
dump_yaml({"ndo": ndo_rm_data}, filename="nac-data/ndo-rm.nac.yaml")


# ***************************************************************************
# Dumping APIC Fabric data (NaC)
# ***************************************************************************

apic_fabric_mi_data = {
    "apic": {
        "access_policies": {
            "leaf_interface_profiles": i.get_fabric_access_leaf_interface_profiles(
                Site("MI"), apic=True
            ),
            "leaf_switch_profiles": i.get_fabric_access_leaf_switch_profiles(
                Site("MI"), apic=True
            ),
            "leaf_interface_policy_groups": i.get_fabric_access_leaf_interface_vpc_policy_groups(
                Site("MI"), apic=True
            ),
        },
    }
}
dump_yaml(apic_fabric_mi_data, filename="nac-data/apic-fabric-mi.nac.yaml")

apic_fabric_rm_data = {
    "apic": {
        "access_policies": {
            "leaf_interface_profiles": i.get_fabric_access_leaf_interface_profiles(
                Site("RM"), apic=True
            ),
            "leaf_switch_profiles": i.get_fabric_access_leaf_switch_profiles(
                Site("RM"), apic=True
            ),
            "leaf_interface_policy_groups": i.get_fabric_access_leaf_interface_vpc_policy_groups(
                Site("RM"), apic=True
            ),
        },
    }
}
dump_yaml(apic_fabric_rm_data, filename="nac-data/apic-fabric-rm.nac.yaml")


# ***************************************************************************
# APIC APIC Tenant data (NaC)
# ***************************************************************************

apic_tenant_shared_mi_data = {
    "apic": {
        "tenants": [
            {
                "name": config_ndo_tenant,
                "ndo_managed": True,
                "application_profiles": i.get_tenant_application_profiles(
                    site=Site("SHARED"), apic=True, physical_site=Site("MI")
                ),
            }
        ]
    }
}
dump_yaml(
    data=apic_tenant_shared_mi_data, filename="nac-data/apic-tenant-shared-mi.nac.yaml"
)

apic_tenant_mi_data = {
    "apic": {
        "tenants": [
            {
                "name": config_ndo_tenant,
                "ndo_managed": True,
                "application_profiles": i.get_tenant_application_profiles(
                    site=Site("MI"), apic=True
                ),
            }
        ]
    }
}
dump_yaml(data=apic_tenant_mi_data, filename="nac-data/apic-tenant-mi.nac.yaml")

apic_tenant_shared_rm_data = {
    "apic": {
        "tenants": [
            {
                "name": config_ndo_tenant,
                "ndo_managed": True,
                "application_profiles": i.get_tenant_application_profiles(
                    site=Site("SHARED"), apic=True, physical_site=Site("RM")
                ),
            }
        ]
    }
}
dump_yaml(
    data=apic_tenant_shared_rm_data, filename="nac-data/apic-tenant-shared-rm.nac.yaml"
)

apic_tenant_rm_data = {
    "apic": {
        "tenants": [
            {
                "name": config_ndo_tenant,
                "ndo_managed": True,
                "application_profiles": i.get_tenant_application_profiles(
                    site=Site("RM"), apic=True
                ),
            }
        ]
    }
}
dump_yaml(data=apic_tenant_rm_data, filename="nac-data/apic-tenant-rm.nac.yaml")


# ***************************************************************************
# Custom policies (Terraform without NaC)
# ***************************************************************************

apic_terraform_mi_data = {
    "fabric": {
        "access_policies": {
            "policies": {
                "switch": {
                    "vpc_default": i.get_fabric_access_vpc_default_data(Site("MI")),
                }
            }
        }
    }
}
dump_yaml(data=apic_terraform_mi_data, filename="nac-data/apic-mi.terraform.yaml")

apic_terraform_rm_data = {
    "fabric": {
        "access_policies": {
            "policies": {
                "switch": {
                    "vpc_default": i.get_fabric_access_vpc_default_data(Site("RM")),
                }
            }
        }
    }
}
dump_yaml(data=apic_terraform_rm_data, filename="nac-data/apic-rm.terraform.yaml")
