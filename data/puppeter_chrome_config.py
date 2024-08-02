# -*- coding: utf-8 -*-
import json
from os import getcwd
from os.path import join
from rich import print

from pydantic import BaseModel, Field
from urllib.parse import urlparse
from typing import List
from .decorators import singleton
from .test_exceptions import PuppeteerChromeConfigError


class TestOptionsModel(BaseModel):
    """
    A Pydantic model for validating the configuration parameters.
    """
    url: str
    urlParam: str
    debugMode: bool
    messageType: List[str]
    cacheEnabled: bool


class PuppeteerOptionsModel(BaseModel):
    """
    A Pydantic model for validating the configuration parameters.
    """
    browser: str
    headless: bool
    puppeteerDelay: int
    userDelay: int
    executablePath: str


class ReportOptionsModel(BaseModel):
    """
    A Pydantic model for validating the configuration parameters.
    """
    ignoreBrowserErrors: List[str]
    ignoreExternalScriptsErrors: List[str] = Field(default_factory=list)


class FullConfigModel(BaseModel):
    """
    A Pydantic model for validating the configuration parameters.
    """
    testOptions: TestOptionsModel
    puppeteerOptions: PuppeteerOptionsModel
    reportOptions: ReportOptionsModel


@singleton
class PuppeteerChromeConfig:
    def __init__(self, config_path: str = join(getcwd(), 'configs', 'puppeteer_chrome_config.json')):
        self.config_path = config_path
        self._config = self._load_config(self.config_path)
        self.test_options = self._config.testOptions
        self.puppeteer_options = self._config.puppeteerOptions
        self.report_options = self._config.reportOptions
        self.ds_url = self.test_options.url
        self.browser: str = self.puppeteer_options.browser
        self._verify_browser_type()
        self._verify_document_server_url()

    @staticmethod
    def _load_config(file_path: str) -> FullConfigModel:
        with open(file_path, 'r') as f:
            return FullConfigModel(**json.load(f))

    def _verify_browser_type(self):
        if self.browser not in ["chrome", "firefox"]:
            raise PuppeteerChromeConfigError(
                f"[red]|ERROR| Browser type '{self.browser}' is not allowed. Allowed types: 'chrome' or 'firefox'"
            )

    def _verify_document_server_url(self):
        if not self.ds_url.endswith('/example'):
            parsed_url = urlparse(self.ds_url)
            correct_url = f'{parsed_url.scheme}://{parsed_url.netloc}/example'
            raise PuppeteerChromeConfigError(
                f"[red]Error: DocumentServer URL must end with '/example'. "
                f"Please fix the parameter [cyan]url[/] "
                f"in the [cyan]{self.config_path}[/] file to [cyan]{correct_url}[/]"
            )
