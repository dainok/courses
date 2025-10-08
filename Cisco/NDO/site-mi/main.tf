module "aci" {
  source  = "netascode/nac-aci/aci"
  version = "1.1.0"

  yaml_files = [
    "../input-data/custom-apic-fabric.nac.yaml",
    "../nac-data/apic-fabric-mi.nac.yaml",
    "../nac-data/apic-tenant-shared-mi.nac.yaml",
    "../nac-data/apic-tenant-mi.nac.yaml",
  ]

  # See inputs: https://registry.terraform.io/modules/netascode/nac-aci/aci/latest
  manage_access_policies    = true
  manage_fabric_policies    = false
  manage_interface_policies = false
  manage_node_policies      = false
  manage_pod_policies       = false
  manage_tenants            = true
}
