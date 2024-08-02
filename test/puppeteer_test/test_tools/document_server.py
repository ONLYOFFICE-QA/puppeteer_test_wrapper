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
        example_url = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}/example/"

        response = self._request_get(example_url)
        if response.status_code == 200:
            print(
                f"[green]|INFO| DocumentServer Example [cyan]{Str.delete_last_slash(example_url)}[/] is up. "
                f"Status Code: [cyan]{response.status_code}[/]"
            )
            return True

        print(
            f"[red]|ERROR| DocumentServer Example [cyan]{Str.delete_last_slash(example_url)}[/] "
            f"responded with status code: [cyan]{response.status_code}[/]"
        )
        raise DocumentServerError

    def _get_sdk_all_js_content(self) -> Optional[str]:
        """
        Retrieve the content of the SDK JavaScript file from the given URL.

        :return: The content of the file if the request is successful, otherwise None.
        """
        sdk_all_url = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}/{self.sdk_link}"

        response = self._request_get(sdk_all_url)
        if response.status_code == 200:
            return response.text
        return None

    @staticmethod
    def _request_get(url: str) -> Optional[requests.Response]:
        try:
            return requests.get(url)

        except requests.ConnectionError:
            print(f"[red]|ERROR| Failed to connect to the server: {url}")
            return None

        except requests.RequestException as e:
            print(f"[red]|ERROR| An error occurred connect to the server: {url}\nError: {e}")
            return None


