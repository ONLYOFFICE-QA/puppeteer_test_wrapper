# -*- coding: utf-8 -*-
import json
from os import getcwd
from os.path import join
from pydantic import BaseModel
from .decorators import singleton



class BrowserConfigModel(BaseModel):
    headless: bool
    slowMo: int
    executablePath: str


class FullConfigModel(BaseModel):
    browser: str
    url: str
    config: BrowserConfigModel


@singleton
class PuppeteerFireFoxConfig:
    def __init__(self, config_path: str = join(getcwd(), 'configs', 'puppeteer_firefox_config.json')):
        self.config_path = config_path
        self._config = self._load_config(self.config_path)
        self.browser = self._config.browser
        self.ds_url = self._config.url
        self.config = self._config.config
        self._verify_browser_type()

    @staticmethod
    def _load_config(file_path: str) -> FullConfigModel:
        with open(file_path, 'r') as f:
            return FullConfigModel(**json.load(f))

    def _verify_browser_type(self):
        if self.browser != "firefox":
            raise ValueError(f"[red]|ERROR| Browser type '{self.browser}' is not allowed. Allowed types: 'firefox'")
