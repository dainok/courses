from datetime import datetime, timedelta
import requests
from requests.models import Response


class APIClient(requests.Session):
    """APIClient is a specialized HTTP client for interacting with the Cisco ACI API."""

    def __init__(
        self, apic_address: str, username: str, password: str, verify: bool = True
    ) -> None:
        """Initialize the APIClient and perform the first authentication."""

        # Initialize the parent requests.Session
        super().__init__()

        # Authentication endpoint for Cisco ACI
        self.base_url = f"https://{apic_address}/api"

        # Store credentials
        self.verify_cert = verify
        self.username = username
        self.__password = password
        self.__session = requests.Session()

        # Disable self-signed certificate warning
        if not verify:
            requests.packages.urllib3.disable_warnings()

        # Will hold the Bearer token once authenticated
        self.__token = None

        # Perform the initial authentication right away
        self.__authenticate()

    def __authenticate(self) -> None:
        """Authenticate with the APIC and store the token."""

        # Headers for the token request
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Body parameters for client credentials grant
        payload = {
            "aaaUser": {
                "attributes": {
                    "name": self.username,
                    "pwd": self.__password,
                }
            }
        }

        # Send the POST request to the auth server
        now = datetime.now()
        url = f"{self.base_url}/aaaLogin.json"
        res = self.__session.post(
            url, headers=headers, json=payload, verify=self.verify_cert
        )
        res.raise_for_status()

        # Save the access token for later requests
        self.__token = res.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]
        self.token_expires_at = now + timedelta(
            seconds=int(
                res.json()["imdata"][0]["aaaLogin"]["attributes"][
                    "refreshTimeoutSeconds"
                ]
            )
        )

    def __check_token(self) -> None:
        """Check token expiration and refresh if needed."""

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        now = datetime.now()
        if now + timedelta(seconds=30) > self.token_expires_at:
            url = f"{self.base_url}/aaaRefresh.json"
            res = self.__session.get(url, headers=headers, verify=self.verify_cert)
            if res.ok:
                self.token_expires_at = now + timedelta(
                    seconds=int(
                        res.json()["imdata"][0]["aaaLogin"]["attributes"][
                            "refreshTimeoutSeconds"
                        ]
                    )
                )

    def logout(self):
        """Logout from APIC."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/aaaLogout.json"
        self.__session.post(url, headers=headers, verify=self.verify_cert)

    def request(self, method: str, url: str, **kwargs) -> Response:
        """Send an HTTP request with automatic token handling."""

        # Check token
        self.__check_token()

        # Ensure the headers dictionary exists
        if "headers" not in kwargs:
            kwargs["headers"] = {}

        # Add Authorization header with the current Bearer token
        kwargs["headers"]["Authorization"] = f"Bearer {self.__token}"

        # Accept JSON responses by default
        kwargs["headers"]["Accept"] = "application/json"

        # For POST/PUT requests, set Content-Type to application/json
        if method.lower() in ["post", "put"]:
            kwargs["headers"]["Content-Type"] = "application/json"

        # Add token to URL
        if "?" in url:
            url = f"{self.base_url}{url}&challenge={self.__token}"
        else:
            url = f"{self.base_url}{url}?challenge={self.__token}"

        # Execute the request
        res = self.__session.request(method, url, verify=self.verify_cert, **kwargs)

        # Retry once if token expired
        if res.status_code == 403 and "Token was invalid" in res.text:
            # Token expired
            self.__authenticate()
            # Retry once
            res = self.__session.request(method, url, verify=self.verify_cert, **kwargs)

        return res
