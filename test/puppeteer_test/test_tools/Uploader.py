# -*- coding: utf-8 -*-
import os
from os.path import basename
from rich import print

from host_tools import File, Shell
from ssh_wrapper import Sftp
from posixpath import join
from typing import Union


from data import PuppeteerFireFoxConfig, PuppeteerChromeConfig
from .file_paths import FilePaths
from .linux_script_demon import LinuxScriptDemon
from tempfile import gettempdir

from .puppeteer_run_script import PuppeteerRunScript


class Uploader:
    """
    A class to manage the uploading of necessary files for running Puppeteer tests on a remote server.
    """
    dep_test_path = os.path.join(os.getcwd(), 'Dep.Tests')
    dep_test_repo = 'git@github.com:ONLYOFFICE/Dep.Tests.git'
    puppeteer_path = join(dep_test_path, 'puppeteer')

    def __init__(
            self,
            sftp: Sftp,
            puppeteer_config: Union[PuppeteerFireFoxConfig, PuppeteerChromeConfig],
            linux_service: LinuxScriptDemon,
            puppeteer_run_script: PuppeteerRunScript,
            tmp_dir: str = None
    ):
        """
        Initialize the Uploader with necessary configurations and paths.

        :param sftp: An instance of Sftp for handling file transfers.
        :param puppeteer_config: Configuration for Puppeteer, specifying the browser and other settings.
        :param linux_service: An instance of LinuxScriptDemon for managing the Linux service.
        :param puppeteer_run_script: An instance of PuppeteerRunScript for managing the Puppeteer script.
        :param tmp_dir: Temporary directory for storing files before upload. Defaults to system temp directory.
        """
        self.paths = FilePaths()
        self.sftp = sftp
        self.linux_service = linux_service
        self.puppeteer_run_script = puppeteer_run_script
        self.tmp_dir = tmp_dir or gettempdir()
        self.remote_service_path = join(self.linux_service.services_dir, self.linux_service.name)
        self.puppeteer_config = puppeteer_config

    def upload_test_files(self):
        """
        Upload all necessary files for running Puppeteer tests to the remote server.
        """
        self._upload_puppeteer(self.sftp)
        self._upload(self.puppeteer_config.config_path, self.paths.remote_puppeter_config_file)
        self._upload(self.puppeteer_run_script.create(), self.paths.remote_puppeter_run_sh)
        self._upload(self._create_run_script_service(), self.remote_service_path)

    def _upload(self, local_path: str, remote_path: str) -> None:
        """
        Upload a single file to the remote server.
        :param local_path: The path to the local file.
        :param remote_path: The destination path on the remote server.
        """
        self.sftp.upload_file(local=local_path, remote=remote_path, stdout=True)

    def _create_run_script_service(self) -> str:
        """
        Create the systemd service file for running the Puppeteer script.
        :return: The path to the created service file.
        """
        return self.linux_service.create(save_path=join(self.tmp_dir, self.linux_service.name))

    def _upload_puppeteer(self, sftp: Sftp) -> None:
        """
        Prepare and upload the Puppeteer repository to the remote server.
        :param sftp: An instance of Sftp for handling file transfers.
        """
        self._get_puppeteer()
        puppeteer_archive = join(self.tmp_dir, basename(self.paths.remote_puppeteer_archive))

        File.compress(self.puppeteer_path, puppeteer_archive, stdout=True)
        sftp.upload_file(puppeteer_archive, self.paths.remote_puppeteer_archive)

    def _get_puppeteer(self) -> None:
        """
        Clone or update the Dep.Tests repository to ensure the Puppeteer directory is up to date.
        """
        if not os.path.isdir(self.dep_test_path):
            print(f"[green]|INFO| Downloading [cyan]Dep.Tests[/] repo to {self.dep_test_path}")
            Shell.call(f"git clone {self.dep_test_repo} {self.dep_test_path} --depth 1")
            Shell.call(f"cd {self.dep_test_path} && git submodule update --init puppeteer/files")
        else:
            print(f"[green]|INFO| Update {basename(self.dep_test_path)} repo")
            Shell.call(f"cd {self.dep_test_path} && git pull")
            Shell.call(f"cd {self.dep_test_path} && git submodule update --init puppeteer/files")
