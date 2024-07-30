# -*- coding: utf-8 -*-
import time

from ssh_wrapper import Ssh, SshException
from ssh_wrapper.data import CommandOutput
from rich.console import Console

from test.puppeteer_test.test_tools.linux_script_demon import LinuxScriptDemon

console = Console()
print = console.print

class SshExecuter:
    """
    Class to manage the execution of commands on a remote server via SSH, particularly focusing on controlling
    and monitoring Linux service scripts.

    Attributes:
        ssh (Ssh): An instance of the SSH connection handler.
        linux_service (LinuxScriptDemon): An instance of the Linux service script manager.
    """

    def __init__(self, ssh: Ssh, linux_service: LinuxScriptDemon):
        self.ssh = ssh
        self.linux_service = linux_service

    def start_script_service(self):
        """
        Start the Linux service script by cleaning the journal logs and executing the start commands.
        """
        self.exec_cmd(f"sudo rm /var/log/journal/*/*.journal")  # clean journal
        for cmd in self.linux_service.start_demon_commands():
            self.exec_cmd(cmd)

    def change_service_dir_access(self):
        """
        Change the access permissions of the Linux service directory.
        """
        for cmd in self.linux_service.change_service_dir_access_cmd():
            self.exec_cmd(cmd,)

    def wait_ssh_up(self):
        ...

    def wait_execute_service(self, timeout: int = None, interval: int | float = 0.5):
        """
        Wait for the Linux service to execute, periodically checking its status and outputting logs.

        :param timeout: Maximum time to wait for the service to execute. If None, wait indefinitely.
        :param interval: Interval in seconds between status checks. Defaults to 0.5 seconds.
        :raises SshException: If the waiting time exceeds the specified timeout.
        """
        line = '-' * 90
        demon_name = self.linux_service.name
        msg = f"[cyan]|INFO| Waiting for execute {demon_name}"
        print(f"[bold cyan]{line}\n|INFO| Wait executing script\n{line}")

        start_time = time.time()

        with console.status(msg) as status:
            while self.exec_cmd(f'systemctl is-active {demon_name}', stdout=False).stdout.lower() == 'active':
                status.update(f"{msg}\n{self._get_demon_log()}")

                time.sleep(interval)

                if isinstance(timeout, int) and (time.time() - start_time) >= timeout:
                    raise SshException(f'[bold red]|WARNING| The service {demon_name} waiting time has expired.')

            print(f"[blue]{line}\n|INFO| Service {demon_name} log:\n{line}\n\n{self._get_demon_log(1000)}\n{line}")

    def _get_demon_log(self, line_num: str | int = 20) -> str:
        """
        Retrieve the log entries for the service from the journal.

        :param line_num: Number of log lines to retrieve. Defaults to 20.
        :return: The service log entries.
        """
        command = f'sudo journalctl -n {line_num} -u {self.linux_service.name}'
        return self.exec_cmd(command, stdout=False, stderr=False).stdout

    def exec_cmd(self, cmd: str, stdout=True, stderr=True) -> CommandOutput:
        """
        Execute a command on the remote server via SSH.

        :param cmd: The command to execute.
        :param stdout: Output the standard output. Defaults to True.
        :param stderr: Output the standard error. Defaults to True.
        :return: The output of the executed command.
        """
        return self.ssh.exec_command(cmd, stdout=stdout, stderr=stderr)
