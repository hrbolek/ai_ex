import asyncio
import aiohttp


class AzureLightClient:
    """
    A simple API client that persists a ClientSession for reuse,
    with support for async context management.
    """
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.session = None

    async def initialize(self):
        """
        Initialize the aiohttp.ClientSession if not already initialized.
        """
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.token}"}
            )

    async def close(self):
        """
        Close the aiohttp.ClientSession if it exists.
        """
        if self.session:
            await self.session.close()
            self.session = None

    async def post(self, endpoint, json_payload):
        """
        Send a POST request to the specified endpoint with a JSON payload.

        :param endpoint: The API endpoint to call.
        :param json_payload: The JSON payload for the POST request.
        """
        await self.initialize()
        url = f"{self.base_url}{endpoint}"
        async with self.session.post(url, json=json_payload) as response:
            print(f"POST {url} -> Status: {response.status}")
            Location = response.headers.get("Location", None)
            print(f"Location = {Location}")
            if response.status in [200, 201]:
                return await self._handle_response(response=response)
            if response.status in [202]:
                print(f"waiting to finish")
                return await self._poll_location(location_url=Location)
                
            print("Unexpected status")
            text = await response.text()
            print(f"text:\n{text}")
            return text

    async def put(self, endpoint, json_payload):
        """
        Send a POST request to the specified endpoint with a JSON payload.

        :param endpoint: The API endpoint to call.
        :param json_payload: The JSON payload for the POST request.
        """
        await self.initialize()
        url = f"{self.base_url}{endpoint}"
        async with self.session.put(url, json=json_payload) as response:
            print(f"PUT {url} -> Status: {type(response.status)}: {response.status}")
            Location = response.headers.get("Location", None)
            print(f"Location = {Location}")
            if response.status in [200, 201]:
                return await self._handle_response(response=response)
            if response.status in [202]:
                print(f"waiting to finish")
                return await self._poll_location(location_url=Location)
                
            print("Unexpected status")
            text = await response.text()
            print(f"text:\n{text}")
            return text
            
    async def delete(self, endpoint):
        """
        Send a DELETE request to the specified endpoint.

        :param endpoint: The API endpoint to call.
        """
        await self.initialize()
        url = f"{self.base_url}{endpoint}"
        async with self.session.delete(url) as response:
            print(f"DELETE {url} -> Status: {response.status}")
            if response.status in [200, 202, 204]:
                return await self._handle_response(response)
            else:
                error_text = await response.text()
                return error_text
            
    async def _handle_response(self, response):
        """
        Handle the HTTP response, returning JSON or raising an exception.
        """
        text = await response.text()
        print(f"text:\n{text}")
        if response.status in [200, 201, 202]:
            try:
                return await response.json()
            except aiohttp.ContentTypeError:
                return await response.text()
        else:
            error_text = await response.text()
            raise Exception(f"HTTP {response.status}: {error_text}")

    async def _poll_location(self, location_url, timeout=600, interval=10):
        """
        Poll a Location URL for long-running operation status.

        :param location_url: The URL to poll for status updates.
        :param timeout: Total timeout for polling (seconds).
        :param interval: Interval between polls (seconds).
        :return: Final response from the Location URL.
        """
        # await self.initialize()
        start_time = asyncio.get_event_loop().time()

        while True:
            async with self.session.get(location_url) as response:
                print(f"Polling {location_url} -> Status: {response.status}")
                data = await self._handle_response(response)
                print(f"Polling data -> Data: {data}")
                # Check operation status
                if response.status == 200:
                    return data
                # if isinstance(data, dict):
                #     if data.get("status") in ["Succeeded", "Failed", "Canceled"]:
                #         return data

                # Timeout check
                if (asyncio.get_event_loop().time() - start_time) > timeout:
                    raise TimeoutError(f"Operation did not complete within {timeout} seconds.")

                # Wait before the next poll
                await asyncio.sleep(interval)

    async def get(self, endpoint):
        """
        Send a GET request to the specified endpoint.

        :param endpoint: The API endpoint to call.
        """
        await self.initialize()
        url = f"{self.base_url}{endpoint}"
        async with self.session.get(url) as response:
            print(f"GET {url} -> Status: {response.status}")
            return await response.json() if response.status == 200 else await response.text()

    async def __aenter__(self):
        """
        Enter the async context and initialize the session.
        """
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Exit the async context and close the session.
        """
        await self.close()