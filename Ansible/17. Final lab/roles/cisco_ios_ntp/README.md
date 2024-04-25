cisco_ios_ntp
================

Configures NTP peers on Cisco IOS devices.

Requirements
------------

Role requires collection `cisco.ios=>8.0.0`.

Role Variables
--------------

Role takes three variables:

- `ntp_servers` (list of IP addresses), used to configure NTP peers.

Example Playbook
----------------

```yaml
- hosts: cisco_ios
  roles:
    - role: cisco_ios_ntp
      ntp_servers:
        - 195.201.19.162
        - 141.98.136.83
```

License
-------

BSD
