cisco_ios_system
================

Configures hostname, domain name, DNS servers and DNS lookup on Cisco IOS devices.

Requirements
------------

Role requires collection `cisco.ios=>8.0.0`.

Role Variables
--------------

Role takes three variables:

- `inventory_hostname_short`, to get the hostname;
- `inventory_hostname`, used to extract domain name;
- `dns_lookup` (boolean), used to configure DNS lookup;
- `dns_servers` (list of IP addresses), used to configure DNS servers.

Example Playbook
----------------

```yaml
- hosts: cisco_ios
  roles:
    - role: cisco_ios_system
      dns_lookup: false
      dns_servers:
        - 8.8.4.4
        - 8.8.8.8
```

License
-------

BSD
