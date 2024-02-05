"""Filterset used in Ansible playbooks."""


class FilterModule(object):
    """Ansible filter."""

    def get_to_dict(self, items, key_name=None):
        """Convert a list of dict into a dict of dict."""
        return {item[key_name]: item for item in items}

    def get_real_ia_name(self, text):
        """Replace AI with SALAMI."""
        return text.replace("AI", "SALAMI")

    def filters(self):
        """Invoked function. Keys define how filters are called."""
        return {
            "real_ai_name": self.get_real_ia_name,
            "to_dict": self.get_to_dict,
        }
