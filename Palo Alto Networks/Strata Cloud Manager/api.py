import requests
from requests.models import Response
from requests.auth import HTTPBasicAuth


class APIClient(requests.Session):
    """APIClient is a specialized HTTP client for interacting with the Palo Alto Networks API."""

    def __init__(self, tenant_id: int, username: str, password: str) -> None:
        """Initialize the APIClient and perform the first authentication."""

        # Initialize the parent requests.Session
        super().__init__()

        # Authentication endpoint for Palo Alto Networks
        self.auth_url = "https://auth.apps.paloaltonetworks.com/oauth2/access_token"

        # Store credentials and tenant information
        self.tenant_id = tenant_id
        self.username = username
        self.__password = password

        # Will hold the Bearer token once authenticated
        self.__token = None

        # Perform the initial authentication right away
        self.__authenticate()

    def __authenticate(self) -> None:
        """Authenticate with the Palo Alto endpoint and store the Bearer token."""

        # Build HTTP Basic Auth
        basic_auth = HTTPBasicAuth(
            f"{self.username}@{self.tenant_id}.iam.panserviceaccount.com",
            self.__password,
        )

        # Headers for the token request
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Body parameters for client credentials grant
        data = {
            "grant_type": "client_credentials",
            "scope": f"tsg_id:{self.tenant_id}",
        }

        # Send the POST request to the auth server
        req = requests.post(self.auth_url, auth=basic_auth, headers=headers, data=data)
        req.raise_for_status()

        # Save the access token for later requests
        self.__token = req.json()["access_token"]

    def request(self, method: str, url: str, **kwargs) -> Response:
        """Send an HTTP request with automatic Bearer token handling."""

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

        # If the given URL is just a path, prefix it with the API base URL
        if url.startswith("/"):
            url = f"https://api.strata.paloaltonetworks.com{url}"

        # Execute the request
        req = super().request(method, url, **kwargs)

        # Retry once if token expired
        if req.status_code == 401 and req.json()["message"] == "Invalid Request Token.":
            # Token expired
            self.__authenticate()
            # Retry once
            kwargs["headers"]["Authorization"] = f"Bearer {self.__token}"
            req = super().request(method, url, **kwargs)

        return req
