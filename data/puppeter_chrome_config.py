# -*- coding: utf-8 -*-
import json
from os import getcwd
from os.path import join

from pydantic import BaseModel, Field
from typing import List
from .decorators import singleton


class TestOptionsModel(BaseModel):
    url: str
    urlParam: str
    debugMode: bool
    messageType: List[str]
    cacheEnabled: bool


class PuppeteerOptionsModel(BaseModel):
    browser: str
    headless: bool
    puppeteerDelay: int
    userDelay: int
    executablePath: str


class ReportOptionsModel(BaseModel):
    ignoreBrowserErrors: List[str]
    ignoreExternalScriptsErrors: List[str] = Field(default_factory=list)


class FullConfigModel(BaseModel):
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


    @staticmethod
    def _load_config(file_path: str) -> FullConfigModel:
        with open(file_path, 'r') as f:
            return FullConfigModel(**json.load(f))

    def _verify_browser_type(self):
        if self.browser != "chrome":
            raise ValueError(f"[red]|ERROR| Browser type '{self.browser}' is not allowed. Allowed types: 'chrome'")
