interfaces:
  Ethernet0/1:
    profile: unused
  Ethernet0/2:
    description: to Hypervisor
    profile: hypervisor
  Ethernet0/3:
    description: to Firewall
    profile: firewall
  Ethernet1/0:
    description: to SW3
    profile: isl
  Ethernet1/1:
    description: to SW4
    profile: isl
  Ethernet1/2:
    description: to SW5
    profile: isl
  Ethernet1/3:
    description: to SW6
    profile: isl
