# -*- coding: utf-8 -*-
import json
from os import getcwd
from os.path import join

from pydantic import BaseModel
from .decorators import singleton

class SSHConfigModel(BaseModel):
    """
    Data model for SSH configuration.

    Attributes:
        wait_execution_time (int): The time (in seconds) to wait for SSH commands to complete.
    """
    wait_execution_time: int

@singleton
class SSHConfig:
    """
    Singleton class to manage SSH configuration.

    This class loads the SSH configuration from a JSON file and provides access to configuration properties.

    Attributes:
        config_path (str): Path to the SSH configuration JSON file.
    """

    def __init__(self, config_path: str = join(getcwd(), 'configs', 'ssh_config.json')):
        self.config_path = config_path
        self._config = self._load_config(self.config_path)

    @property
    def wait_execution_time(self) -> int:
        """
        Gets the time (in seconds) to wait for SSH commands to complete.

        :return: The wait execution time.
        """
        return self._config.wait_execution_time

    @staticmethod
    def _load_config(file_path: str) -> SSHConfigModel:
        """
        Loads the SSH configuration from a JSON file and returns an instance of SSHConfigModel.

        :param file_path: The path to the SSH configuration JSON file.
        :return: An instance of SSHConfigModel containing the loaded configuration.
        :raises FileNotFoundError: If the file specified by file_path does not exist.
        :raises json.JSONDecodeError: If the JSON file is not correctly formatted.
        :raises TypeError: If the JSON file does not conform to SSHConfigModel schema.
        """
        try:
            with open(file_path, 'r') as f:
                return SSHConfigModel(**json.load(f))

        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from file {file_path}: {e}")

        except TypeError as e:
            raise ValueError(f"Configuration file does not match SSHConfigModel schema: {e}")
