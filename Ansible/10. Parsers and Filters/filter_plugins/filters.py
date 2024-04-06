"""Filterset used in Ansible playbooks."""


class FilterModule(object):
    """Ansible filter."""

    def get_to_dict(self, items: list, key: str = None) -> dict:
        """Convert a list of dict into a dict of dict."""
        return {item[key]: item for item in items}

    def drop_down_interfaces(self, interfaces: list) -> list:
        """Return a list of active interfaces."""
        result = []
        for interface in interfaces:
            if interface["status"] == "up":
                result.append(interface)
        return result

    def filters(self):
        """Invoked function. Keys define how filters are called."""
        return {
            "drop_down_interfaces": self.drop_down_interfaces,
            "to_dict": self.get_to_dict,
        }
