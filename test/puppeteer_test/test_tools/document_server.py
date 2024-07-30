# -*- coding: utf-8 -*-
import json
import re
from rich import print
from typing import Optional
from urllib.parse import urlparse

import requests

from .file_paths import FilePaths


class DocumentServer:
    version_pattern = re.compile(r'Version:\s*(\d+\.\d+\.\d+)\s*\(build:(\d+)\)', re.IGNORECASE)
    sdk_link = 'sdkjs/word/sdk-all.js'

    def __init__(self, url: str):
        self.path = FilePaths()
        self.url = self._get_url(url)

    def get_version(self) -> Optional[str]:
        if self.url:
            match = self.version_pattern.search(self._get_sdk_all_js_content(self.url))
            if match:
                return f"{match.group(1)}.{match.group(2)}"
        return None

    @staticmethod
    def _get_sdk_all_js_content(url: str) -> Optional[str]:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None

    def _get_url(self, url) -> str:
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}/{self.sdk_link}"
