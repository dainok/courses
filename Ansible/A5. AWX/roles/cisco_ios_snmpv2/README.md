cisco_ios_snmpv2
================

Configures a single SNMPv2 read-only community on Cisco IOS devices.

Requirements
------------

Role requires collection `cisco.ios=>8.0.0`.

Role Variables
--------------

Role takes three variables:

- `snmp_community`, used to configure the SNMPv2 community.

Example Playbook
----------------

```yaml
- hosts: cisco_ios
  roles:
    - role: cisco_ios_snmpv2
      snmp_community: romanagement
```

License
-------

BSD
