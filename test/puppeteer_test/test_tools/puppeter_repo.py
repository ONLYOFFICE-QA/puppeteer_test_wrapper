# -*- coding: utf-8 -*-
from host_tools import Shell
from rich import print

from .paths import Paths

class PuppeterRepo:
    dep_test_repo = 'git@github.com:ONLYOFFICE/Dep.Tests.git'
    puppeter_files_repo = 'git@github.com:ONLYOFFICE-data/pp-files.git'

    def __init__(self):
        self.path = Paths()

    def clone(self) -> None:
        self.clone_dep_test()
        self.clone_test_files()

    def clone_dep_test(self) -> None:
        """
        Clone the Dep.Tests repository
        """
        print(f"[green]|INFO| Cloning [cyan]Dep.Tests[/] repository to {self.path.local_dep_test}")
        Shell.call(f"git clone {self.dep_test_repo} {self.path.local_dep_test} --depth 1")

    def clone_test_files(self) -> None:
        """
        Clone the pp-files repository
        """
        print(f"[green]|INFO| Cloning [cyan]Puppeter Files[/] repository to {self.path.local_puppeteer_files_dir}")
        Shell.call(f"git clone {self.puppeter_files_repo} {self.path.local_puppeteer_files_dir}")
