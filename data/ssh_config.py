# -*- coding: utf-8 -*-
import json
from os import getcwd
from os.path import join

from pydantic import BaseModel
from .decorators import singleton

class SSHConfigModel(BaseModel):
    wait_execution_time: int

@singleton
class SSHConfig:

    def __init__(self, config_path: str = join(getcwd(), 'configs', 'ssh_config.json')):
        self.config_path = config_path
        self._config = self._load_config(self.config_path)

    @property
    def wait_execution_time(self) -> int:
        return self._config.wait_execution_time

    @staticmethod
    def _load_config(file_path: str) -> SSHConfigModel:
        """
        Loads the configuration from a JSON file and returns a ConfigModel instance.

        :param file_path: The path to the configuration JSON file.
        :return: An instance of ConfigModel containing the loaded configuration.
        """
        with open(file_path, 'r') as f:
            return SSHConfigModel(**json.load(f))
