import time
from datetime import datetime, timedelta
import httpx


class APIClient:
    """APIClient is a specialized HTTP client for interacting with the Cisco ACI API."""

    def __init__(
        self,
        apic_address: str,
        username: str,
        password: str,
        verify: bool = True,
        timeout: int = 10,
        page_size: int = 500,
    ) -> None:
        """Initialize the APIClient and perform the first authentication."""

        # Authentication endpoint for Cisco ACI
        self.base_url = f"https://{apic_address}/api"
        self.verify_cert = verify
        self.page_size = page_size

        # Store credentials
        self.username = username
        self.__password = password
        self.__token = None
        self.client = httpx.Client(verify=verify, timeout=timeout)

        # Perform the initial authentication right away
        self.__authenticate()

    def __authenticate(self) -> None:
        """Authenticate with the APIC and store the token."""

        # Set headers
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
        now = datetime.utcnow()
        url = f"{self.base_url}/aaaLogin.json"
        res = self.client.post(url, json=payload, headers=headers)
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

        # Set headers
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__token}",
        }
        now = datetime.now()
        if (
            not self.token_expires_at
            or now + timedelta(seconds=30) > self.token_expires_at
        ):
            url = f"{self.base_url}/aaaRefresh.json"
            res = self.client.get(url, headers=headers)
            if res.is_success:
                self.token_expires_at = now + timedelta(
                    seconds=int(
                        res.json()["imdata"][0]["aaaLogin"]["attributes"][
                            "refreshTimeoutSeconds"
                        ]
                    )
                )
            else:
                # Reauth
                self.__authenticate()

    def logout(self):
        """Logout from APIC."""

        # Set headers
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__token}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/aaaLogout.json"
        self.client.post(url, headers=headers)

    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Send an HTTP request with automatic token handling."""

        # Check token
        self.__check_token()

        # Set headers
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__token}",
        }

        # For POST/PATCH/PUT requests, set Content-Type to application/json
        if method.lower() in ["post", "put", "patch"]:
            headers["Content-Type"] = "application/json"

        # Execute the request
        full_url = f"{self.base_url}{url}"
        max_retries = 5
        backoff = 1.0
        for _ in range(max_retries):
            res = self.client.request(method, full_url, headers=headers, **kwargs)

            if res.status_code == 403 and "Token was invalid" in res.text:
                # Token expired -> retry once
                self.__authenticate()
                continue
            if res.status_code == 429:
                # Rate limit exceeded
                retry_after = res.headers.get("Retry-After")
                if retry_after:
                    sleep_time = int(retry_after)
                else:
                    sleep_time = backoff
                time.sleep(sleep_time)
                backoff *= 2  # Exponential backoff
                continue

            return res
        
        raise httpx.HTTPError("Max retries exceeded")

    def get(self, url: str, **kwargs) -> httpx.Response:
        """GET wrapper."""
        return self.request("get", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        """POST wrapper."""
        return self.request("post", url, **kwargs)

    def patch(self, url: str, **kwargs) -> httpx.Response:
        """PATCH wrapper."""
        return self.request("put", url, **kwargs)

    def put(self, url: str, **kwargs) -> httpx.Response:
        """PUT wrapper."""
        return self.request("put", url, **kwargs)

    def delete(self, url: str, **kwargs) -> httpx.Response:
        """DELETE wrapper."""
        return self.request("delete", url, **kwargs)

    def get_objects(self, url: str, **kwargs):
        """GET objects handling pagination."""
        page = 0
        url = url + "&" if "?" in url else url + "?"
        while True:
            paged_url = url + f"page-size={self.page_size}&page={page}"
            res = self.request("get", paged_url, **kwargs)
            res.raise_for_status()

            items = res.json().get("imdata", [])
            if not items:
                # No more data
                break
            for item in items:
                # Return one object
                yield item
            # Next page
            page += 1


class AsyncAPIClient:
    """AsyncAPIClient is a specialized async HTTP client for interacting with the Cisco ACI API."""

    def __init__(
        self,
        apic_address: str,
        username: str,
        password: str,
        verify: bool = True,
        timeout: int = 10,
        page_size: int = 500,
    ) -> None:
        """Initialize the APIClient and perform the first authentication."""

        # Authentication endpoint for Cisco ACI
        self.base_url = f"https://{apic_address}/api"
        self.verify_cert = verify
        self.page_size = page_size

        # Store credentials
        self.username = username
        self.__password = password
        self.__token = None
        self.client = httpx.AsyncClient(verify=verify, timeout=timeout)

    async def __aenter__(self):
        """Perform the initial authentication right away."""

        await self.__authenticate()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Before exiting."""

        await self.logout()
        await self.client.aclose()

    async def __authenticate(self) -> None:
        """Authenticate with the APIC and store the token."""

        # Set headers
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
        now = datetime.utcnow()
        url = f"{self.base_url}/aaaLogin.json"
        res = await self.client.post(url, json=payload, headers=headers)
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

    async def __check_token(self) -> None:
        """Check token expiration and refresh if needed."""

        # Set headers
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__token}",
        }
        now = datetime.now()
        if (
            not self.token_expires_at
            or now + timedelta(seconds=30) > self.token_expires_at
        ):
            url = f"{self.base_url}/aaaRefresh.json"
            res = await self.client.get(url, headers=headers)
            if res.is_success:
                self.token_expires_at = now + timedelta(
                    seconds=int(
                        res.json()["imdata"][0]["aaaLogin"]["attributes"][
                            "refreshTimeoutSeconds"
                        ]
                    )
                )
            else:
                # Reauth
                await self.__authenticate()

    async def logout(self):
        """Logout from APIC."""

        # Set headers
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__token}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/aaaLogout.json"
        await self.client.post(url, headers=headers)

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Send an HTTP request with automatic token handling."""

        # Check token
        await self.__check_token()

        # Set headers
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__token}",
        }

        # For POST/PATCH/PUT requests, set Content-Type to application/json
        if method.lower() in ["post", "put", "patch"]:
            headers["Content-Type"] = "application/json"

        # Execute the request
        full_url = f"{self.base_url}{url}"
        max_retries = 5
        backoff = 1.0
        for _ in range(max_retries):
            res = await self.client.request(method, full_url, headers=headers, **kwargs)

            if res.status_code == 403 and "Token was invalid" in res.text:
                # Token expired -> retry once
                self.__authenticate()
                continue
            if res.status_code == 429:
                # Rate limit exceeded
                retry_after = res.headers.get("Retry-After")
                if retry_after:
                    sleep_time = int(retry_after)
                else:
                    sleep_time = backoff
                time.sleep(sleep_time)
                backoff *= 2  # Exponential backoff
                continue

            return res
    
        raise httpx.HTTPError("Max retries exceeded")

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """GET wrapper."""
        return await self.request("get", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """POST wrapper."""
        return await self.request("post", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> httpx.Response:
        """PATCH wrapper."""
        return await self.request("put", url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        """PUT wrapper."""
        return await self.request("put", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """DELETE wrapper."""
        return await self.request("delete", url, **kwargs)

    async def get_objects(self, url: str, **kwargs):
        """GET objects handling pagination."""
        page = 0
        url = url + "&" if "?" in url else url + "?"
        while True:
            paged_url = url + f"page-size={self.page_size}&page={page}"
            res = await self.request("get", paged_url, **kwargs)
            res.raise_for_status()

            items = res.json().get("imdata", [])
            if not items:
                # No more data
                break
            for item in items:
                # Return one object
                yield item
            # Next page
            page += 1
