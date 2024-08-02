# -*- coding: utf-8 -*-
import re
import requests
from rich import print

from typing import Optional
from urllib.parse import urlparse
from host_tools import Str
from data import DocumentServerError

from .paths import Paths


class DocumentServer:
    """
    A class to interact with a document server
    """
    version_pattern = re.compile(r'Version:\s*(\d+\.\d+\.\d+)\s*\(build:(\d+)\)', re.IGNORECASE)
    sdk_link = 'sdkjs/word/sdk-all.js'

    def __init__(self, url: str):
        """
        Initialize the DocumentServer with a base URL.
        :param url: The base URL of the document server.
        """
        self.path = Paths()
        self.url = url
        self.parsed_url = urlparse(url)

    def get_version(self) -> Optional[str]:
        """
        Retrieve the version information from the SDK JavaScript file on the document server.
        :return: The version string if found, otherwise None.
        """
        if self.url:
            match = self.version_pattern.search(self._get_sdk_all_js_content())
            if match:
                return f"{match.group(1)}.{match.group(2)}"
        return None

    def check_example_is_up(self) -> bool:
        """
        Check if the DocumentServer example page is up and running.

        This method constructs the URL for the example page based on the parsed URL of the DocumentServer instance.
        It sends a GET request to this URL and checks the response status code. If the response status code is 200,
        it prints an informational message and returns True. Otherwise, it raises a DocumentServerError with an
        appropriate error message.

        :return: True if the example page is up (status code 200), False otherwise.
        :raises DocumentServerError: If the example page responds with a status code other than 200.
        """
        example_url = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}/example/"

        response = self._request_get(example_url)
        if response and response.status_code == 200:
            print(
                f"[green]|INFO| DocumentServer Example [cyan]{Str.delete_last_slash(example_url)}[/] is up. "
                f"Status Code: [cyan]{response.status_code}[/]"
            )
            return True

        raise DocumentServerError(
            f"[red]|ERROR| DocumentServer Example [cyan]{Str.delete_last_slash(example_url)}[/] "
            f"responded with status code: [cyan]{response.status_code}[/]"
        )

    def _get_sdk_all_js_content(self) -> Optional[str]:
        """
        Retrieve the content of the SDK JavaScript file from the given URL.

        :return: The content of the file if the request is successful, otherwise None.
        """
        sdk_all_url = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}/{self.sdk_link}"

        response = self._request_get(sdk_all_url)
        if response and response.status_code == 200:
            return response.text
        return None

    @staticmethod
    def _request_get(url: str) -> Optional[requests.Response]:
        """
        Sends a GET request to the specified URL and returns the response.

        This method attempts to connect to the given URL and handle any connection or request errors.
        It prints an error message if the connection fails or if any other request error occurs.

        :param url: The URL to send the GET request to.
        :return: The response object if the request is successful; None otherwise.
        """
        try:
            return requests.get(url)

        except requests.ConnectionError:
            print(f"[red]|ERROR| Failed to connect to the server: {url}")
            return None

        except requests.RequestException as e:
            print(f"[red]|ERROR| An error occurred connect to the server: {url}\nError: {e}")
            return None


