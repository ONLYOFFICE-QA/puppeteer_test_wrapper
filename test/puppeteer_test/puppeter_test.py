# -*- coding: utf-8 -*-
from test.puppeteer_test.test_tools import TestTools
from rich import print
from data import PuppeteerChromeConfig


class PuppeteerTest:

    def __init__(self, flags: dict = None):
        self.puppeteer_config = PuppeteerChromeConfig()
        self.test = TestTools(puppeteer_config=self.puppeteer_config, flags=flags)

    def run(self, save_droplet: bool = False) -> None:
        print(
            f"[green]|INFO| The test is run on the Document Server version: "
            f"[red]{self.test.ds_version}[/]. Browser: [red]{self.test.puppeteer_config.browser}"
        )

        self.test.create_test_droplet()
        self.test.move_to_user_project()
        self.test.run_script_on_droplet()
        self.test.wait_execute_script()
        self.test.download_report()
        self.test.handle_report()
        self.test.delete_test_droplet() if not save_droplet else None
