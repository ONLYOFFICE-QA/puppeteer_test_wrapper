# -*- coding: utf-8 -*-
import os

from posixpath import join

from host_tools.utils import Dir
from rich import print
from ssh_wrapper import Ssh, Sftp, ServerData
from typing import Union

from libs import DigitalOceanWrapper
from data import DropletConfig, PuppeteerFireFoxConfig, PuppeteerChromeConfig
from .document_server import DocumentServer
from .Uploader import Uploader
from .decorators import droplet_exists
from .file_paths import FilePaths
from .linux_script_demon import LinuxScriptDemon
from .puppeteer_run_script import PuppeteerRunScript
from .report import Report
from .ssh_executer import SshExecuter


class TestTools:
    """
    A class to manage testing tools and operations for setting up and running Puppeteer scripts on a DigitalOcean droplet.
    """

    def __init__(
            self,
            puppeteer_config: Union[PuppeteerChromeConfig, PuppeteerFireFoxConfig],
            flags: list = None
    ):
        """
        Initialize the TestTools with Puppeteer configuration and optional flags.
        :param puppeteer_config: Configuration for Puppeteer, specifying the browser and other settings.
        :param flags: A list of flags to pass to the Puppeteer script. Defaults to None.
        """
        self.tmp_dir = self._get_tmp_dir()
        self.puppeteer_config = puppeteer_config
        self.ds = DocumentServer(self.puppeteer_config.ds_url)
        self.do = DigitalOceanWrapper()
        self.droplet_config = DropletConfig()
        self.path = FilePaths()
        self.linux_service = LinuxScriptDemon(self.path.remote_puppeter_run_sh, user=self.droplet_config.default_user)
        self.puppeteer_run_script = PuppeteerRunScript(self.puppeteer_config, script_dir=self.tmp_dir, flags=flags)
        self.ds_version = self.ds.get_version()
        self.report = Report(version=self.ds_version, browser=self.puppeteer_config.browser, tmp_dir=self.tmp_dir)
        self.droplet = None

    def create_test_droplet(self):
        """
        Create a new DigitalOcean droplet for testing if it does not already exist.
        """
        if self.droplet_config.name in self.do.droplet.get_droplet_names():
            self.droplet = self.do.droplet.get_by_name(self.droplet_config.name)
            return print(f"[magenta]|INFO| Droplet [cyan]{self.droplet_config.name}[/] already exists")

        self.droplet = self.do.droplet.create(
            name=self.droplet_config.name,
            size_slug=self.droplet_config.size,
            region=self.droplet_config.region,
            image=self.droplet_config.image,
            ssh_keys=self._get_do_ssh_keys(),
            wait_until_up=True
        )

    @droplet_exists
    def move_to_user_project(self):
        """
        Move the created droplet to a specified project in DigitalOcean.
        """
        if self.droplet_config.do_project_name:
            self.do.droplet.move_to_project(self.droplet, self.droplet_config.do_project_name)

    @droplet_exists
    def delete_test_droplet(self):
        """
        Delete the test droplet from DigitalOcean.
        """
        self.do.droplet.delete(self.droplet)

    @droplet_exists
    def get_droplet_ip(self):
        """
        Get the IP address of the test droplet.
        :return: The IP address of the droplet.
        """
        return self.do.droplet.info(self.droplet, load=True).get_ip_address()

    @droplet_exists
    def run_script_on_droplet(self):
        """
        Upload and run the Puppeteer script on the test droplet.
        """
        _server = ServerData(self.get_droplet_ip(), self.droplet_config.default_user)
        with Ssh(_server) as ssh, Sftp(_server, ssh.connection) as sftp:
            ssh_executer = SshExecuter(ssh, linux_service=self.linux_service)
            uploader = Uploader(sftp, self.puppeteer_config, self.linux_service, self.puppeteer_run_script, self.tmp_dir)

            ssh_executer.change_service_dir_access()
            uploader.upload_test_files()
            ssh_executer.start_script_service()
            ssh_executer.wait_execute_service(interval=1)
            self.report.download(sftp)

    def handle_report(self):
        """
        Processing the report
        """
        self.report.convert_paths_to_relative()

    @staticmethod
    def _get_tmp_dir():
        """
        Create and return a temporary directory for storing script and other files.
        :return: The path to the temporary directory.
        """
        tmp_dir = join(os.getcwd(), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        Dir.delete(tmp_dir, clear_dir=True)
        return tmp_dir

    def _get_do_ssh_keys(self) -> list:
        """
        Retrieve the list of SSH key IDs to be used for the DigitalOcean droplet.
        :return: A list of SSH key IDs.
        """
        if self.droplet_config.ssh_do_user_name:
            ssh_key_id = self.do.get_ssh_key_id_by_name(self.droplet_config.ssh_do_user_name)
            return [ssh_key_id] if ssh_key_id else self.do.get_all_ssh_keys_id()
        return self.do.get_all_ssh_keys_id()
