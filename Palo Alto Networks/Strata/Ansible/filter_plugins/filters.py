"""Filterset used in Ansible playbooks."""

import json
from datetime import datetime
import pytz
import dateparser


class FilterModule(object):
    """Ansible filter."""

    def panos_content(self, output: dict, latest: bool = False) -> str:
        """
        Return the installed content version.

        If latest == True, return the latest content version.
        """
        current_version = None
        latest_version = "0"

        try:
            data = json.loads(output)
            entries = data["response"]["result"]["content-updates"]["entry"]

            if not isinstance(entries, list):
                # Transform a single entry to a list
                entries = [entries]

            for entry in entries:
                if entry["current"] == "yes":
                    current_version = entry["version"]
                if float(latest_version.replace("-", ".")) < float(
                    entry["version"].replace("-", ".")
                ):
                    latest_version = entry["version"]

            if latest:
                return latest_version
            return current_version

        except json.decoder.JSONDecodeError:
            pass
        except KeyError:
            pass
        except ValueError:
            pass
        raise ValueError("string is not output from request content upgrade info")

    def panos_content_period(self, output: dict, hours: int = 86400) -> bool:
        """Return True if last update is within hours (default 24 hours)."""
        try:
            data = json.loads(output)
            last_updated_at = data["response"]["result"]["content-updates"][
                "@last-updated-at"
            ]
            if not last_updated_at:
                raise ValueError(
                    "string is not output from request content upgrade info"
                )
            delta = (
                datetime.now(pytz.utc) - dateparser.parse(last_updated_at)
            ).total_seconds()
            if delta < hours * 3600:
                return True
            return False
        except json.decoder.JSONDecodeError:
            pass
        except KeyError:
            pass
        raise ValueError("string is not output from request content upgrade info")

    def filters(self):
        """Invoked function. Keys define how filters are called."""
        return {
            "panos_content": self.panos_content,
            "panos_content_period": self.panos_content_period,
        }
