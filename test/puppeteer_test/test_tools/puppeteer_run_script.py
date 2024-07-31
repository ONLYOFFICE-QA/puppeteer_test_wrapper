# -*- coding: utf-8 -*-
from typing import Union
from rich import print
from data import PuppeteerFireFoxConfig, PuppeteerChromeConfig

from posixpath import join, basename, dirname
from tempfile import gettempdir

from .file_paths import FilePaths

class PuppeteerRunScript:
    """
    A class to generate and manage the execution of a bash script that installs necessary dependencies,
    sets up the environment, and runs a Puppeteer script for testing.
    """

    def __init__(
            self,
            config: Union[PuppeteerFireFoxConfig, PuppeteerChromeConfig],
            script_dir: str = None,
            script_name: str = None,
            flags: dict = None
    ):
        """
        Initialize the PuppeteerRunScript with configuration, optional script directory, script name, and flags.
        :param config: Configuration for Puppeteer, specifying the browser type and other settings.
        :param script_dir: The directory where the script will be saved. Defaults to a temporary directory.
        :param script_name: The name of the script file. Defaults to a predefined name.
        :param flags: A dictionary of flags to pass to the Puppeteer script. Defaults to None.
        """
        self.path = FilePaths()
        self.file_name = script_name or self.path.puppeter_run_sh_name
        self.home_dir = self.path.remote_home_dir
        self.flags = flags
        self.script_path = join(script_dir or gettempdir(), self.file_name)
        self.config = config

    @property
    def generate(self):
        """
        Generate the content of the bash script for setting up and running the Puppeteer test.
        :return: The generated bash script content as a string.
        """
        puppeteer_run_cmd = f"python3 run.py '{self.path.remote_puppeter_config_file}'{self._get_flags()}"
        print(f"[green]|INFO| Puppeteer run cmd: [cyan]{puppeteer_run_cmd}[/]")

        return f"""\
#!/bin/bash
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y curl git zip unzip

# NodeJs installation
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

{self._browser_installation()}

# Cloning puppeteer repositories
cd '{self.home_dir}'
git clone https://github.com/ONLYOFFICE/build_tools.git


mkdir '{dirname(self.path.remote_puppeteer_dir)}'
rm -rf '{self.path.remote_puppeteer_dir}'
unzip '{self.path.remote_puppeteer_archive}' -d '{self.path.remote_puppeteer_dir}'

# Run Puppeteer test
cd '{self.path.remote_puppeteer_engine}'
python3 ./install.py
{puppeteer_run_cmd}

# Archive results
rm {self.path.remote_result_archive}
cd {self.path.remote_puppeteer_dir}
zip -r '{self.path.remote_result_archive}' {basename(self.path.remote_report_dir)} > /dev/null 2>&1\
        """.strip()

    def create(self):
        """
        Create the bash script file with the generated content.
        :return: The path to the created bash script file.
        """
        with open(self.script_path, mode='w', newline='') as file:
            file.write('\n'.join(line.strip() for line in self.generate.split('\n')))
        return self.script_path

    def _browser_installation(self):
        """
        Determines the browser installation commands based on the configuration.

        :return: A string representing the browser installation commands.
        """
        if self.config.browser.lower() == 'firefox':
            return """\
            # FireFox installation
            sudo apt-get install firefox -y\
            """
        else:
            return """\
            # GoogleChrome installation
            wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
            sudo apt-get install ./google-chrome-stable_current_amd64.deb -y\
            """

    def _get_flags(self):
        """
        Generate a string of flags to pass to the Puppeteer script.
        :return: A string of flags to be appended to the Puppeteer run command.
        """
        if not self.flags:
            return ''

        filtered_flags = {k: v for k, v in self.flags.items() if v is not None}
        flags_string = " ".join(f"--{k} {v}" for k, v in filtered_flags.items())
        return ' ' + flags_string
