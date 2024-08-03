# -*- coding: utf-8 -*-
import time
from typing import Optional
from ssh_wrapper import Ssh
from ssh_wrapper.data import CommandOutput
from rich.console import Console

from .linux_script_demon import LinuxScriptDemon

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

    def get_service_exit_code(self) -> Optional[int]:
        """
        Retrieves the exit code of the service's main process.

        :return: The exit code of the service's main process if available; None otherwise.
        """
        cmd = f"systemctl show -p ExecMainCode {self.linux_service.name}"
        output = self.exec_cmd(cmd, stdout=False).stdout

        if '=' in output:
            _, exit_code = output.split('=', 1)
            return int(exit_code.strip())

        return None

    def get_service_exit_status(self) -> Optional[int]:
        """
        Retrieves the exit status code of the service's main process.

        :return: The exit status code of the service's main process if available; None otherwise.
        """
        cmd = f"systemctl show -p ExecMainStatus {self.linux_service.name}"
        output = self.exec_cmd(cmd, stdout=False).stdout

        if '=' in output:
            _, exit_code = output.split('=', 1)
            return int(exit_code.strip())

        return None

    def change_service_dir_access(self):
        """
        Change the access permissions of the Linux service directory.
        """
        for cmd in self.linux_service.change_service_dir_access_cmd():
            self.exec_cmd(cmd,)

    def get_service_status(self) -> CommandOutput:
        """
        Retrieves the status of the specified Linux service.

        This method uses the `systemctl` command to check whether the service managed by
        `self.linux_service.name` is active.

        :return: An instance of `CommandOutput` containing the output of the `systemctl is-active` command.
        """
        return self.exec_cmd(f'systemctl is-active {self.linux_service.name}', stdout=False)

    def check_service_status(self, status: str = 'active') -> bool:
        """
        Checks if the service is in the specified status.('active', 'inactive')

        :param status: The status to check for, default is 'active'.
        :return: True if the service is in the specified status, False otherwise.
        """
        cmd = f'systemctl is-active {self.linux_service.name}'
        return self.exec_cmd(cmd, stdout=False).stdout.lower() == status

    def get_demon_log(self, line_num: str | int = 20) -> str:
        """
        Retrieve the log entries for the service from the journal.

        :param line_num: Number of log lines to retrieve. Defaults to 20.
        :return: The service log entries.
        """
        command = f'sudo journalctl -n {line_num} -u {self.linux_service.name}'
        out = self.exec_cmd(command, stdout=False, stderr=False)
        return out.stdout if out.exit_code == 0 else ''


    def exec_cmd(self, cmd: str, stdout=True, stderr=True) -> CommandOutput:
        """
        Execute a command on the remote server via SSH.

        :param cmd: The command to execute.
        :param stdout: Output the standard output. Defaults to True.
        :param stderr: Output the standard error. Defaults to True.
        :return: The output of the executed command.
        """
        return self.ssh.exec_command(cmd, stdout=stdout, stderr=stderr)
