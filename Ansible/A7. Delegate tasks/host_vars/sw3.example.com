interfaces:
  Ethernet0/1:
    description: to SW1
    profile: isl
  Ethernet0/2:
    description: to SW2
    profile: isl
  Ethernet0/3:
    description: to printer
    profile: office
upstream_port: Ethernet1/0
