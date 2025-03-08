cisco_ios_interface_profile
=========

Configure an interface given a profile name.

Requirements
------------

Role requires collection `cisco.ios=>8.0.0`.

Role Variables
--------------

Role takes the following variables:

- `interfaces` (dict of interface name/interface vaules), used to configure interfaces.

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

```yaml
- hosts: cisco_ios
  roles:
    - role: cisco_ios_interface_profile
      tags: interface
```

License
-------

BSD
