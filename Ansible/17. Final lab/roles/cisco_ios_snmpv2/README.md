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

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

```yaml
- hosts: cisco_ios
  roles:
    - role: cisco_ios_snmpv2
      snmp_community: romanagement
```

License
-------

BSD
