locals {
  custom_config = yamldecode(file("${path.cwd}/../nac-data/apic-.terraform.yaml"))
}

resource "aci_vpc_explicit_protection_group" "vpc_groups" {
  for_each = { for v in local.custom_config.fabric.access_policies.policies.switch.vpc_default : v.name => v }
  name                              = each.value.name
  switch1                           = each.value.switch1
  switch2                           = each.value.switch2
  vpc_explicit_protection_group_id  = each.value.vpc_explicit_protection_group_id
}