# Ansible playbooks for Palo Alto Networks NGFW

Install the collection with:

```bash
ansible-galaxy collection install paloaltonetworks.panos
```

Refers also to `requirements.txt` on the root folder.

## Playbooks

- `playbook-print_all_vars.yml`: print all fatcs from NGFW using the `panos_facts` module;
- `playbook-dynamic_content_update.yml`: update dynamic contents (content, antivirus, wildfire) on NGFW. Use `grace_period` to set the maximum time between checks.
- `playbook-get_tsf.yml`: generate and download tech support file from remote NGFW. TSF is stored in local current directory.

Usage:

```bash
ansible-playbook -i inventory.ini -u admin -k playbook-print_all_vars.yml
```

## Disclaimer

Playbooks are not production ready, but can serve as examples to build your own.

## References

- [Playbook examples](https://github.com/PaloAltoNetworks/ansible-playbooks)
- [Ansible Doc](https://ansible-pan.readthedocs.io/en/latest/modules/index.html)
- [Galaxy](https://galaxy.ansible.com/ui/repo/published/paloaltonetworks/panos/)
