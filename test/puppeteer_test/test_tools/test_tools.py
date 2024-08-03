# -*- coding: utf-8 -*-
import os
import shutil
import time

from host_tools import Dir
from rich.console import Console
from ssh_wrapper import Ssh, Sftp, ServerData
from typing import Union

from digitalocean_wrapper import DigitalOceanWrapper
from data import DropletConfig, PuppeteerChromeConfig, droplet_exists, SSHConfig
from .document_server import DocumentServer
from .Uploader import Uploader
from .paths import Paths
from .linux_script_demon import LinuxScriptDemon
from .puppeteer_run_script import PuppeteerRunScript
from .report import Report
from .ssh_executer import SshExecuter
from .digitalocean_ssh_key import DigitalOceanSshKey


console = Console()
print = console.print


class TestTools:
    """
    A class to manage testing tools and operations for setting up and running Puppeteer scripts on a DigitalOcean droplet.
    """

    def __init__(
            self,
            puppeteer_config: Union[PuppeteerChromeConfig],
            flags: list = None
    ):
        """
        Initialize the TestTools with Puppeteer configuration and optional flags.
        :param puppeteer_config: Configuration for Puppeteer, specifying the browser and other settings.
        :param flags: A list of flags to pass to the Puppeteer script. Defaults to None.
        """
        self.ssh_config = SSHConfig()
        self.path = Paths()
        self.puppeteer_config = puppeteer_config
        self.ds = DocumentServer(self.puppeteer_config.ds_url)
        self.ds.check_example_is_up()

        self.do = DigitalOceanWrapper()
        self.droplet_config = DropletConfig()

        self.linux_service = LinuxScriptDemon(self.path.remote_puppeter_run_sh, user=self.droplet_config.default_user)
        self.puppeteer_run_script = PuppeteerRunScript(self.puppeteer_config, flags=flags)

        self.do_ssh_keys_id = DigitalOceanSshKey(self.droplet_config, self.do).get_keys_id()
        self.ds_version = self.ds.get_version()
        self.report = Report(version=self.ds_version, browser=self.puppeteer_config.browser)

        self.droplet = None
        self.retry_num = 2

        self._prepare_tmp_dir()


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
            ssh_keys=self.do_ssh_keys_id,
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
            uploader = Uploader(sftp, self.puppeteer_config, self.linux_service, self.puppeteer_run_script)

            if not ssh_executer.check_service_status():
                uploader.upload_test_files()
                ssh_executer.start_script_service()

    @droplet_exists
    def wait_execute_script(self, active_status: str = 'active') -> None:
        """
        Waits for the execution of the specified Linux service on the droplet.

        This method continuously checks the status of the specified Linux service on the droplet,
        waiting for it to change from the active status. If the service becomes inactive or deactivates,
        it prints the service's log, exit code, and exit status code.

        :param active_status: The status indicating that the service is active. Default is 'active'.
        """
        wait_interval = self.ssh_config.wait_execution_time or 60
        msg = f"[cyan]|INFO| Waiting for execute {self.linux_service.name}. Wait interval: {wait_interval} seconds"
        line = '-' * 90
        print(f"[bold cyan]{line}\n{msg}\n{line}")

        with console.status(msg) as status:
            while True:
                with Ssh(ServerData(self.get_droplet_ip(), self.droplet_config.default_user)) as ssh:
                    ssh_executer = SshExecuter(ssh, linux_service=self.linux_service)
                    out = ssh_executer.get_service_status()
                    service_status = out.stdout.lower() if out.stdout else None

                    if service_status and service_status != active_status.lower():
                        return print(
                            f"[blue]{line}\n|INFO| Service {self.linux_service.name} log:\n"
                            f"{line}\n\n{ssh_executer.get_demon_log(1000)}\n{line}\n\n"
                            f"[green]|INFO||{ssh.server.ip}| Service [cyan]{self.linux_service.name}[/] "
                            f"deactivated with status [cyan]{service_status}[/]. "
                            f"Exit Code: [cyan]{ssh_executer.get_service_exit_code()}[/] "
                            f"Exit Status Code: [cyan]{ssh_executer.get_service_exit_status()}[/]"
                        )

                    status.update(f"{msg}\n{ssh_executer.get_demon_log(line_num=20)}")
                    time.sleep(wait_interval)

    @droplet_exists
    def download_report(self):
        """
        Downloads a report from the droplet using SFTP.
        """
        with Sftp(ServerData(self.get_droplet_ip(), self.droplet_config.default_user)) as sftp:
            self.report.download(sftp)

    def handle_report(self):
        """
        Processing the report
        """
        self.report.convert_paths_to_relative()

    def _prepare_tmp_dir(self) -> None:
        """
        Create a temporary directory for storing script and other files.

        If the directory already exists, it will be deleted first. The deletion process will handle any permission issues by
        changing the permissions of the files and directories to ensure they can be removed.

        :return: None
        """
        if os.path.isdir(self.path.tmp_dir):
            onerror_handler = lambda func, path, exc_info: (os.chmod(path, 0o777), func(path))
            shutil.rmtree(self.path.tmp_dir, onerror=onerror_handler)

        Dir.create(self.path.tmp_dir, stdout=False)
