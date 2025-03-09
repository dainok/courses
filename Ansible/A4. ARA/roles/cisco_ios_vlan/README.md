cisco_ios_vlan
================

Configures VLANs on Cisco IOS devices.

Requirements
------------

Role requires collection `cisco.ios=>8.0.0`.

Role Variables
--------------

Role takes the following variables:

- `vlans` (list), used to configure the SNMPv2 community.

Example Playbook
----------------

```yaml
- hosts: cisco_ios
  roles:
    - role: cisco_ios_vlan
      vlans:
        - id: 50
          name: SERVER
        - id: 51
          name: DMZ
```

License
-------

BSD
