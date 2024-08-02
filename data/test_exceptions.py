# -*- coding: utf-8 -*-
from rich import print

class TestException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        print(f"[bold red]{self.__class__.__name__}[/bold red] {self.message}")
        return ''


class DigitalOceanSshKeyError(TestException):
    """
    Exception raised when there is an error retrieving or creating an SSH key on DigitalOcean.
    """
    pass

class PuppeteerChromeConfigError(TestException): ...

class DocumentServerError(TestException): ...
