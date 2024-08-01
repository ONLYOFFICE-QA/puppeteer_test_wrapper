# -*- coding: utf-8 -*-
import re
from typing import Optional
from urllib.parse import urlparse

import requests

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
        self.url = self._get_url(url)

    def get_version(self) -> Optional[str]:
        """
        Retrieve the version information from the SDK JavaScript file on the document server.
        :return: The version string if found, otherwise None.
        """
        if self.url:
            match = self.version_pattern.search(self._get_sdk_all_js_content(self.url))
            if match:
                return f"{match.group(1)}.{match.group(2)}"
        return None

    @staticmethod
    def _get_sdk_all_js_content(url: str) -> Optional[str]:
        """
        Retrieve the content of the SDK JavaScript file from the given URL.
        :param url: The URL to the SDK JavaScript file.
        :return: The content of the file if the request is successful, otherwise None.
        """
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None

    def _get_url(self, url) -> str:
        """
        Construct the full URL to the SDK JavaScript file from the base URL.
        :param url: The base URL of the document server.
        :return: The full URL to the SDK JavaScript file.
        """
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}/{self.sdk_link}"
