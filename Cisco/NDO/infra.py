import csv
from enum import Enum
from typing import List, Optional, Union
from pydantic import (
    BaseModel,
    Field,
    IPvAnyInterface,
    model_validator,
    HttpUrl,
    field_validator,
)
import yaml
from slugify import slugify


def parse_vlan_ranges(raw):
    """Transform a VLAN range (str) in a list of int."""
    vlans = []

    if not raw:
        return vlans

    for vlan_range in raw.split(","):
        if "-" in vlan_range:
            start, end = map(int, vlan_range.split("-"))
            vlans.extend(range(start, end + 1))
        else:
            vlans.append(int(vlan_range))
    return vlans


class Site(str, Enum):
    MI = "MI"
    RM = "RM"
    SHARED = "SHARED"

    def __str__(self):
        return self.value


class APIC(BaseModel):
    site: Site
    name: str
    url: HttpUrl
    insecure: bool
    username: str
    password: str

    def __str__(self):
        return self.name

    @model_validator(mode="after")
    def validate_rules(self):
        self.url = str(self.url)
        return self


class VRF(BaseModel):
    name: str

    def __str__(self):
        return self.name

    @field_validator("name", mode="before")
    @classmethod
    def parse_name(cls, raw=str | None):
        if raw:
            return raw.strip()
        return "default"

    @model_validator(mode="after")
    def validate_rules(self):
        if not self.name.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"With VRF {self.name}, name is not valid")

        return self


class Leaf(BaseModel):
    name: str
    site: Site

    @model_validator(mode="after")
    def validate_rules(self):
        if "-" in self.name:
            # Name must be 101-102
            name_left = int(self.name.split("-")[0])
            name_right = int(self.name.split("-")[1])
            if name_right != name_left + 1:
                raise ValueError(f"With leaf {self.name}, name must be 101-102")
        else:
            # Name must be 101
            int(self.name)

        return self


class Network(BaseModel):
    vlan: int = Field(..., ge=1, le=4094)
    name: str
    site: Site
    vrf: VRF
    advertised: bool = False
    anycast_address: Optional[IPvAnyInterface] = None
    l2_stretched: bool = False

    def __str__(self):
        return self.name

    @field_validator("l2_stretched", mode="before")
    @classmethod
    def parse_l2_stretched(cls, raw):
        if raw == "":
            return False
        return bool(int(raw))
    
    @field_validator("advertised", mode="before")
    @classmethod
    def parse_advertised(cls, raw):
        if raw == "":
            return False
        return bool(int(raw))
    
    @model_validator(mode="after")
    def validate_rules(self):
        if not self.name.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"with network {self.name}, name is not valid")

        # Convert IP to string
        if self.anycast_address:
            self.anycast_address = str(self.anycast_address)

        # if anycast_address -> l2_stretched=True
        if self.site.name == "SHARED" and self.anycast_address and not self.l2_stretched:
            raise ValueError(
                f"with network {self.name}, shared network with anycast_address must be l2_stretched"
            )

        # If site=MI/RM -> l2_stretched=False
        if self.site in {Site.MI, Site.RM} and self.l2_stretched:
            raise ValueError(
                f"with network {self.name}, if site is local, network cannot be l2_stretched"
            )

        # If advertised=True -> anycast_address must be set
        if self.advertised and not self.anycast_address:
            raise ValueError(
                f"with network {self.name}, if advertised=True, anycast_address must be set"
            )

        return self


class InterfaceGroup(BaseModel):
    leaf: Leaf
    site: Site
    profile: str
    ifaces: list[int]
    tagged_vlans: list[int] = []
    native_vlan: Optional[int]
    selector: str
    description: Optional[str]

    @field_validator("description", mode="before")
    @classmethod
    def parse_description(cls, raw):
        if raw:
            return raw.strip()
        return None

    @field_validator("ifaces", mode="before")
    @classmethod
    def parse_ifaces(cls, ifaces=List[str]):
        return map(int, ifaces)

    @field_validator("tagged_vlans", mode="before")
    @classmethod
    def parse_tagged_vlans(cls, raw):
        return parse_vlan_ranges(raw)

    @field_validator("native_vlan", mode="before")
    @classmethod
    def parse_native_vlan(cls, raw):
        if raw:
            return int(raw)
        return None

    @model_validator(mode="after")
    def validate_rules(self):
        # Copy description from selector
        if not self.description:
            self.description = self.selector
        self.selector = slugify(self.selector).upper()

        # Native VLAN must not be in tagged VLANs
        if self.native_vlan in self.tagged_vlans:
            raise ValueError(
                f"With interface group {self.selector}, native VLAN {self.native_vlan} cannot be included in tagged VLANs {self.tagged_vlans}"
            )

        return self


class Infra:
    _input_data_dir = "input-data"
    _fabric_interfaces_csvfile = f"{_input_data_dir}/fabric-interfaces.csv"
    _fabric_leaves_csvfile = f"{_input_data_dir}/fabric-leaves.csv"
    _l2_networks_csvfile = f"{_input_data_dir}/l2-networks.csv"
    _config_file = "config.yaml"
    _secrets_file = "secrets.yaml"
    _apic_customization_file = "input-data/custom-apic-fabric.nac.yaml"

    def __load_apics__(self):
        """Reading APICs."""
        self.apics: List[APIC] = []

        for site_id, apic_data in self.config["apics"].items():
            apic = APIC(
                site=Site(site_id.upper()),
                name=apic_data["name"],
                url=apic_data["url"],
                insecure=apic_data["url_insecure"],
                username=self.secrets[site_id]["username"],
                password=self.secrets[site_id]["password"],
            )
            self.apics.append(apic)

    def __load_fabric_leaves__(self):
        """Reading fabric leaves data file (Leaf)."""
        self.leaves: List[Leaf] = []

        with open(
            self._fabric_leaves_csvfile, mode="r", newline="", encoding="utf-8"
        ) as fh:
            reader = csv.DictReader(fh, delimiter=";")
            for row in reader:
                leaf_id = int(row["ID"])
                leaf = Leaf(
                    name=str(leaf_id),
                    site=Site(row["SITE"].upper()),
                )

                # Check for duplicated leaves
                if self.get_leaf_by_name_site(name=leaf.name, site=leaf.site):
                    raise ValueError(
                        f"With leaf {leaf.name}, name is duplicated on site {leaf.site.name}"
                    )
                self.leaves.append(leaf)

                if leaf_id % 2 == 0:
                    # Adding also the 101-102 leaf
                    leaf = Leaf(
                        name=f"{leaf_id - 1}-{leaf_id}",
                        site=leaf.site,
                    )
                    self.leaves.append(leaf)

    def __load_fabric_interfaces__(self):
        """Reading fabric interfaces data file (Site)."""
        self.interface_groups: List[InterfaceGroup] = []

        with open(
            self._fabric_interfaces_csvfile, mode="r", newline="", encoding="utf-8"
        ) as fh:
            reader = csv.DictReader(fh, delimiter=";")
            rows = list(reader)

        # Sort rows
        rows.sort(key=lambda r: (r["SITE"], r["LEAF_ID"], r["INTERFACES"]))
    
        # Read rows
        for row in rows:
            site = Site(row["SITE"].upper())
            interface_group = InterfaceGroup(
                leaf=Leaf(name=row["LEAF_ID"], site=site),
                profile=row["POLICY_GROUP"],
                ifaces=row["INTERFACES"].split(","),
                site=site,
                native_vlan=row["NATIVE_VLAN"],
                tagged_vlans=row["TAGGED_VLANS"],
                selector=row["GROUP_NAME"],
                description=row["PORT_DESCRIPTION"],
            )

            # Check for duplicated selectors
            if self.get_interface_group_by_leaf_selector_site(
                leaf=interface_group.leaf,
                site=interface_group.site,
                selector=interface_group.selector,
            ):
                raise ValueError(
                    f"With interface group {interface_group.profile}, selector {interface_group.selector} is already used on site {interface_group.site.name} leaf {interface_group.leaf.name}"
                )

            # Check for duplicated interfaces
            for iface in interface_group.ifaces:
                leaves = []
                if "-" in interface_group.leaf.name:
                    # Checking also on each leaf
                    leaves = [
                        interface_group.leaf,
                        Leaf(
                            name=interface_group.leaf.name.split("-")[0],
                            site=interface_group.site,
                        ),
                        Leaf(
                            name=interface_group.leaf.name.split("-")[1],
                            site=interface_group.site,
                        ),
                    ]
                else:
                    leaves = [interface_group.leaf]
                    # Checking also on both leaves
                    leaf_id = int(interface_group.leaf.name)
                    if leaf_id % 2 == 0:
                        # Even
                        leaves.append(
                            Leaf(
                                name=f"{leaf_id - 1}-{leaf_id}",
                                site=interface_group.site,
                            )
                        )
                    else:
                        # Odd
                        leaves.append(
                            Leaf(
                                name=f"{leaf_id}-{leaf_id + 1}",
                                site=interface_group.site,
                            )
                        )

                for leaf in leaves:
                    if self.get_interface_group_by_interface_leaf_site(
                        leaf=leaf,
                        site=interface_group.site,
                        iface=iface,
                    ):
                        raise ValueError(
                            f"With interface group {interface_group.profile}, interface e{iface} is already used on site {interface_group.site.name} leaf {leaf.name}"
                        )

            # Check L2 network exists
            for vlan in interface_group.tagged_vlans + [
                interface_group.native_vlan
            ]:
                if not vlan:
                    continue
                if not self.get_network_by_vlan_site(
                    vlan=vlan, site=interface_group.site
                ) and not self.get_network_by_vlan_site(
                    vlan=vlan, site=Site("SHARED")
                ):
                    raise ValueError(
                        f"With interface group {interface_group.profile}, interface e{iface} is using an inexistent network {vlan} on site {interface_group.site.name} leaf {interface_group.leaf.name}"
                    )

            # Check Leaf exists
            if not self.get_leaf_by_name_site(
                name=interface_group.leaf.name, site=site
            ):
                raise ValueError(
                    f"With interface group {interface_group.profile}, on site {interface_group.site.name} leaf {interface_group.leaf.name} doesn't exist"
                )

            self.interface_groups.append(interface_group)

    def __load_l2_networks__(self):
        """Reading tenant L2 data file (Network, VRF)."""
        self.networks: List[Network] = []
        self.vrfs: List[VRF] = []

        # Read L2 VLAN pools
        vlan_pools = []
        for pool in self.apic_customization["apic"]["access_policies"]["vlan_pools"]:
            for range in pool["ranges"]:
                vlan_pools = vlan_pools + parse_vlan_ranges(f"{range['from']}-{range['to']}")

        with open(
            self._l2_networks_csvfile, mode="r", newline="", encoding="utf-8"
        ) as fh:
            reader = csv.DictReader(fh, delimiter=";")
            rows = list(reader)

        # Sort rows
        rows.sort(key=lambda r: (r["SITE"], int(r["VLAN_ID"])))

        # Read rows
        for row in rows:
            network = Network(
                vlan=int(row["VLAN_ID"]),
                name=row["VLAN_NAME"],
                site=Site(row["SITE"].upper()),
                anycast_address=row["ANYCAST_ADDRESS"] or None,
                vrf=VRF(name=row["VRF"]),
                advertised=row["ADVERTISED"],
                l2_stretched=row["L2_STRETCHED"],
            )

            # Check for duplicated networks
            if self.get_network_by_vlan_site(vlan=network.vlan, site=network.site):
                raise ValueError(
                    f"With network {network.vlan}, VLAN is duplicated on site {network.site}"
                )

            # Check for missing VLAN pools
            if network.vlan not in vlan_pools:
                raise ValueError(
                    f"With network {network.vlan}, VLAN is not included in any VLAN pool"
                )

            self.networks.append(network)

            # Add VRF
            if not self.get_network_by_vrf(name=network.vrf.name):
                self.vrfs.append(network.vrf)

    def __init__(self):
        # Reading config file
        with open(self._config_file, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # Reading secret file
        with open(self._secrets_file, "r", encoding="utf-8") as f:
            self.secrets = yaml.safe_load(f)

        # Read APIC customization
        with open(self._apic_customization_file, "r", encoding="utf-8") as f:
            self.apic_customization = yaml.safe_load(f)

        # Reading input data
        self.__load_apics__()
        self.__load_l2_networks__()
        self.__load_fabric_leaves__()
        self.__load_fabric_interfaces__()

    # ***********************************************************************
    # Getters: APIC
    # ***********************************************************************

    def get_apic_login_data_by_site(self, site: Site) -> dict[str] | None:
        """Return APIC login data given site."""
        if site.name == Site.SHARED:
            # Return NDO data
            return {
                "url": self.config["ndo"]["url"],
                "insecure": self.config["ndo"].get("url_insecure"),
                "username": self.secrets["ndo"]["username"],
                "password": self.secrets["ndo"]["password"],
            }
        for item in self.apics:
            # Return APIC data
            if item.site.name == site.name:
                return {
                    "url": item.url,
                    "insecure": item.insecure,
                    "username": item.username,
                    "password": item.password,
                }
        return None

    def get_apic_name_by_site(self, site: Site) -> str | None:
        """Return APIC name by site."""
        for item in self.apics:
            if item.site.name == site.name:
                return item.name
        return None

    def get_apic_names(self) -> list[str]:
        """Return APIC list names."""
        return [item.name for item in self.apics]

    # ***********************************************************************
    # Getters: Interface
    # ***********************************************************************

    def get_interface_group_by_interface_leaf_site(
        self, leaf: Leaf, site: Site, iface: int
    ) -> InterfaceGroup | None:
        for item in self.interface_groups:
            if (
                item.leaf.name == leaf.name
                and item.site.name == site.name
                and iface in item.ifaces
            ):
                return item
        return None

    def get_interface_group_by_leaf_selector_site(
        self, leaf: Leaf, site: Site, selector: str
    ) -> InterfaceGroup | None:
        for item in self.interface_groups:
            selector = selector.upper()
            if (
                item.leaf.name == leaf.name
                and item.site.name == site.name
                and item.selector == selector
            ):
                return item
        return None

    def get_interfaces_group_by_leaf_site(
        self, leaf: Leaf, site: Site
    ) -> List[InterfaceGroup]:
        """Return Interface Group list given site and leaf."""
        return [
            item
            for item in self.interface_groups
            if item.leaf.name == leaf.name and item.site.name == site.name
        ]

    def get_interfaces_group_by_site(self, site: Site) -> List[InterfaceGroup]:
        """Return Interface Group list given site."""
        return [item for item in self.interface_groups if item.site.name == site.name]

    def get_interfaces_group_by_site_vlan(
        self, site: Site, vlan: int
    ) -> List[InterfaceGroup]:
        """Return Interface Group list given leaf, site, VLAN."""
        return [
            item
            for item in self.interface_groups
            if item.site.name == site.name
            and (vlan in item.tagged_vlans or vlan == item.native_vlan)
        ]

    # ***********************************************************************
    # Getters: Leaf
    # ***********************************************************************

    def get_leaf_by_name_site(self, name: str, site: Site) -> Leaf | None:
        """Return Leaf given site and name."""
        for item in self.leaves:
            if item.name == name and item.site.name == site.name:
                return item
        return None

    def get_leaves_by_name(self, name: str) -> List[Leaf]:
        """Return Leaf list given Leaf name."""
        return [item for item in self.leaves if item.leaf.name == name]

    def get_leaves_by_site(self, site: Site) -> List[Leaf]:
        """Return Leaf list given site."""
        return [item for item in self.leaves if item.site.name == site.name]

    # ***********************************************************************
    # Getters: Network
    # ***********************************************************************

    def get_network_by_vlan_site(self, vlan: int, site: Site) -> Network | None:
        """Return Network given site and VLAN."""
        for item in self.networks:
            if item.vlan == vlan and item.site.name == site.name:
                return item
        return None

    def get_networks_by_site(self, site: Site) -> List[Network]:
        """Return Network list given site."""
        return [item for item in self.networks if item.site.name == site.name]

    def get_networks_by_site_vrf(self, site: Site, vrf: VRF) -> List[Network]:
        """Return Network list given site and VRF."""
        return [
            item
            for item in self.networks
            if item.site.name == site.name and item.vrf.name == vrf.name
        ]

    # ***********************************************************************
    # Getters: VRF
    # ***********************************************************************

    def get_network_by_vrf(self, name: str) -> VRF | None:
        """Return VRF given name."""
        for item in self.vrfs:
            if item.name == name:
                return item
        return None

    # ***********************************************************************
    # NaC getters: Fabric
    # ***********************************************************************

    def get_fabric_access_leaf_interface_vpc_policy_groups(
        self, site: Site, apic: bool = False
    ) -> List[dict]:
        """Return Fabric -> Access Policies -> Interfaces -> Leaf Interfaces -> Policy Groups."""
        if not apic:
            raise ValueError(
                "With get_fabric_access_leaf_interface_vpc_policy_groups, apic=False is not supported"
            )

        policy_groups_data = []
        for interface_group in self.get_interfaces_group_by_site(site=site):
            # Building vPC policy groups
            if "-" not in interface_group.leaf.name:
                # Skip non vPC
                continue

            policy_group_data = dict(
                self.config["fabric"]["port_channel_policies"][interface_group.profile]
            )
            policy_group_data["name"] = f"{interface_group.selector}_PolGrp"
            policy_groups_data.append(policy_group_data)

        return policy_groups_data

    def get_fabric_access_leaf_interface_profiles(
        self, site: Site, apic: bool = False
    ) -> List[dict]:
        """Return Fabric -> Access Policies -> Interfaces -> Leaf Interfaces -> Profiles."""
        if not apic:
            raise ValueError(
                "With get_fabric_access_leaf_interface_profiles, apic=False is not supported"
            )

        data = []
        for leaf in self.get_leaves_by_site(site):
            # Building interface profiles
            selectors = []
            for interface_group in self.get_interfaces_group_by_leaf_site(
                leaf=leaf, site=site
            ):
                if "-" in interface_group.leaf.name:
                    # vPC
                    policy_group = f"{interface_group.selector}_PolGrp"
                else:
                    # Single ports
                    policy_group = f"{interface_group.profile}_PolGrp"
                selector = {
                    "name": f"{interface_group.selector}_Sel",
                    "policy_group": policy_group,
                    "port_blocks": [],
                }
                for iface in interface_group.ifaces:
                    port_block = {
                        "name": f"Block{iface}",
                        "from_port": iface,
                    }
                    if interface_group.description:
                        port_block["description"] = interface_group.description
                    selector["port_blocks"].append(port_block)
                selectors.append(selector)

            data.append(
                {
                    "name": f"Leaf-{leaf.name}_IntProf",
                    "selectors": selectors,
                }
            )
        return data

    def get_fabric_access_leaf_switch_profiles(
        self, site: Site, apic: bool = False
    ) -> List[dict]:
        """Return Fabric -> Access Policies -> Switches -> Leaf Switches -> Profiles."""
        if not apic:
            raise ValueError(
                "With get_fabric_access_leaf_interface_profiles, apic=False is not supported"
            )

        data = []
        for leaf in self.get_leaves_by_site(site):
            data.append(
                {
                    "name": f"Leaf-{leaf.name}_LeafProf",
                    "interface_profiles": [f"Leaf-{leaf.name}_IntProf"],
                    "selectors": [
                        {
                            "name": f"Leaf-{leaf.name}_Sel",
                            "node_blocks": [
                                {
                                    "name": f"Block{int(leaf_id)}",
                                    "from": int(leaf_id),
                                }
                                for leaf_id in leaf.name.split("-")
                            ],
                        }
                    ],
                }
            )
        return data

    def get_fabric_access_vpc_default_data(self, site: Site) -> List[dict]:
        """Return Fabric -> Access Policies -> Policies -> Switch -> Virtual Port Channel default."""
        data = []
        for leaf in self.get_leaves_by_site(site):
            if "-" not in leaf.name:
                # Skip non vPC
                continue
            data.append(
                {
                    "name": f"Leaf-{leaf.name}_vPCSecPol",
                    "switch1": leaf.name.split("-")[0],
                    "switch2": leaf.name.split("-")[1],
                    "vpc_explicit_protection_group_id": leaf.name.split("-")[0],
                }
            )
        return data

    # ***********************************************************************
    # NaC getters: Tenant
    # ***********************************************************************

    def get_tenant_application_profiles(
        self, site: Site, apic: bool = False, physical_site=None
    ) -> List[dict]:
        """Return Tenant -> Application Profiles."""
        data = []
        for vrf in self.vrfs:
            # For each VRF, create an Application Profile
            application_profile = {
                "name": f"{site.name}-{vrf.name}_App",
                "endpoint_groups": [],
            }
            if apic:
                # APIC specific attributes
                application_profile["ndo_managed"] = True

            for network in self.get_networks_by_site_vrf(site=site, vrf=vrf):
                # Build site customization
                # sites = []
                # if site.name == Site.SHARED:
                #     # Add all sites
                #     for apic_name in self.get_apic_names():
                #         sites.append(
                #             {
                #                 "name": apic_name,
                #                 "physical_domains": [
                #                     {
                #                         "name": "Phy_Domain",  # TODO: make a parameter, coming from APIC
                #                         "deployment_immediacy": "immediate",
                #                         "resolution_immediacy": "immediate",
                #                     }
                #                 ],
                #             }
                #         )
                # else:
                #     # Add specific site
                #     sites.append(
                #         {
                #             "name": self.get_apic_name_by_site(Site(site.name)),
                #             "physical_domains": [
                #                 {
                #                     "name": "Phy_Domain",  # TODO: make a parameter, coming from APIC
                #                     "deployment_immediacy": "immediate",
                #                     "resolution_immediacy": "immediate",
                #                 }
                #             ],
                #         }
                #     )

                # For each BD, create an EPG
                endpoint_group = {
                    "name": f"{site.name}-{network.vlan:04d}-{network.name}_EPG",
                    "intra_epg_isolation": False,
                    "proxy_arp": False,
                    # "sites": sites,
                }
                if apic:
                    # APIC specific attributes
                    endpoint_group["bridge_domain"] = (
                        f"{site.name}-{network.vlan:04d}-{network.name}_BD"
                    )
                    endpoint_group["ndo_managed"] = True
                    endpoint_group["physical_domains"] = [
                        self.config["fabric"]["physical_domain"]
                    ]

                    # Static ports
                    endpoint_group["static_ports"] = []

                    # Get interfaces from site, and VLAN
                    if physical_site:
                        # If site is SHARED, interfaces are bound to physical site
                        interface_groups = self.get_interfaces_group_by_site_vlan(
                            site=physical_site, vlan=network.vlan
                        )
                    else:
                        interface_groups = self.get_interfaces_group_by_site_vlan(
                            site=site, vlan=network.vlan
                        )
                    for interface_group in interface_groups:
                        static_port_template = {
                            "pod_id": int(interface_group.leaf.name[0]),
                            "module": 1,
                            "deployment_immediacy": "immediate",
                        }

                        if network.vlan == interface_group.native_vlan:
                            # Adding native VLAN
                            static_port_template["vlan"] = interface_group.native_vlan
                            static_port_template["mode"] = (
                                "native" if interface_group.tagged_vlans else "untagged"
                            )
                        if network.vlan in interface_group.tagged_vlans:
                            # Adding tagged VLANs
                            static_port_template["vlan"] = network.vlan
                            static_port_template["mode"] = "regular"

                        if "-" in interface_group.leaf.name:
                            # vPC
                            static_port = dict(static_port_template)
                            static_port["channel"] = (
                                f"{interface_group.selector}_PolGrp"
                            )
                            static_port["node_id"] = int(
                                interface_group.leaf.name.split("-")[0]
                            )
                            static_port["node2_id"] = int(
                                interface_group.leaf.name.split("-")[1]
                            )
                            endpoint_group["static_ports"].append(static_port)
                        else:
                            # Static port on single leaf
                            static_port_template["node_id"] = int(
                                interface_group.leaf.name
                            )

                            for iface in interface_group.ifaces:
                                static_port = dict(static_port_template)
                                static_port["port"] = iface
                                endpoint_group["static_ports"].append(static_port)

                else:
                    # NDO specific attributes
                    endpoint_group["bridge_domain"] = {
                        "name": f"{site.name}-{network.vlan:04d}-{network.name}_BD",
                    }
                    endpoint_group["vrf"] = {
                        "name": f"{vrf.name}_VRF",
                        "template": self.config["ndo"]["templates"]["stretched_vrf"][
                            "name"
                        ],
                    }
                    endpoint_group["useg"] = False
                application_profile["endpoint_groups"].append(endpoint_group)

            if application_profile["endpoint_groups"]:
                data.append(application_profile)

        return data

    def get_tenant_bridge_domains(self, site: Site, apic: bool = False) -> List[dict]:
        """Return Tenant -> Networking -> Bridge Domains."""
        data = []
        for network in self.get_networks_by_site(site=site):
            bridge_domain = {
                "name": f"{site.name}-{network.vlan:04d}-{network.name}_BD",
                "arp_flooding": True,
                "unicast_routing": False,
            }

            if network.anycast_address:
                # L3 specific attributes
                bridge_domain["unicast_routing"] = True
                subnets = [
                    {
                        "ip": network.anycast_address,
                        "scope": "public" if network.advertised else "private",
                        "primary": True,
                    }
                ]
                if apic:
                    # APIC specific attributes
                    bridge_domain["subnets"] = [
                        {
                            "ip": network.anycast_address,
                            "scope": "public" if network.advertised else "private",
                            "subnets": subnets,
                        }
                    ]
                else:
                    # NDO specific attributes
                    if site.name == "SHARED":
                        bridge_domain["subnets"] = subnets
                    else:
                        bridge_domain["sites"] = [
                            {
                                "name": self.get_apic_name_by_site(Site(site.name)),
                                "subnets": subnets,
                            }
                        ]

            if apic:
                # APIC specific attributes
                bridge_domain["unknown_unicast"] = "flood"
                bridge_domain["vrf"] = f"{network.vrf.name}_VRF"
                bridge_domain["igmp_snooping_policy"] = self.config["custom"][
                    "policies"
                ]["no_igmp"]
                bridge_domain["ndo_managed"] = True
            else:
                # NDO specific attributes
                bridge_domain["l2_unknown_unicast"] = "flood"
                bridge_domain["vrf"] = {
                    "name": f"{network.vrf.name}_VRF",
                    "template": self.config["ndo"]["templates"]["stretched_vrf"][
                        "name"
                    ],
                }
                # Stretched networks specific attributes
                bridge_domain["l2_stretch"] = network.l2_stretched
                bridge_domain["intersite_bum_traffic"] = network.l2_stretched

            data.append(bridge_domain)
        return data
