# -*- coding: utf-8 -*-
import json
from os import getcwd
from os.path import join
import re

from pydantic import BaseModel
from .decorators import singleton


class ConfigModel(BaseModel):
    """
    A Pydantic model for validating the configuration parameters.

    Attributes:
        DROPLET_NAME (str): The name assigned to the DigitalOcean droplet.
        DROPLET_REGION (str): The region where the DigitalOcean droplet will be created.
        DROPLET_IMAGE (str): The image (operating system) to be used for the DigitalOcean droplet.
        DROPLET_SIZE (str): The size specification for the DigitalOcean droplet.
        DEFAULT_USER (str): The default user account to be used for accessing the droplet.
        SSH_DO_USER_NAME (str): The name of the SSH key user configured on DigitalOcean.
        DO_PROJECT_NAME (str): The name of the project in DigitalOcean under which the droplet will be organized.
    """
    DROPLET_NAME: str
    DROPLET_REGION: str
    DROPLET_IMAGE: str
    DROPLET_SIZE: str
    DEFAULT_USER: str
    DO_PROJECT_NAME: str


@singleton
class DropletConfig:
    """
    Configuration class for DigitalOcean droplet.

    Attributes:
        name (str): The full name of the droplet.
        region (str): The region where the droplet will be created.
        image (str): The image (operating system) to be used for the droplet.
        size (str): The size specification for the droplet.
        default_user (str): The default user account for the droplet.
        ssh_do_user_name (str): The name of the SSH key user configured on DigitalOcean.
        do_project_name (str): The name of the project in DigitalOcean under which the droplet will be organized.
        droplet_name_pattern (str): The pattern that the droplet name must follow.
    """
    def __init__(self, config_path: str = join(getcwd(), 'configs', 'droplet_config.json')):
        self.config_path = config_path
        self.droplet_name_pattern = "droplets-starter-"
        self._config = self._load_config(self.config_path)
        self.name = self._get_droplet_name()
        self.region = self._config.DROPLET_REGION
        self.image = self._config.DROPLET_IMAGE
        self.size = self._config.DROPLET_SIZE
        self.default_user = self._config.DEFAULT_USER
        self.do_project_name = self._config.DO_PROJECT_NAME
        self._verify_droplet_name_pattern()

    def _get_droplet_name(self) -> str:
        """
        Generates and returns the full name for the droplet.

        :return: The full name of the droplet.
        """
        droplet_name = re.sub(r'[^a-zA-Z0-9.-]', '-', self._config.DROPLET_NAME.strip())
        return f"{self.droplet_name_pattern}{droplet_name}"

    @staticmethod
    def _load_config(file_path: str) -> ConfigModel:
        """
        Loads the configuration from a JSON file and returns a ConfigModel instance.

        :param file_path: The path to the configuration JSON file.
        :return: An instance of ConfigModel containing the loaded configuration.
        """
        with open(file_path, 'r') as f:
            return ConfigModel(**json.load(f))

    def _verify_droplet_name_pattern(self):
        """
        Verifies that the droplet name follows the required pattern.

        :raises ValueError: If the droplet name does not contain 'droplets-starter'.
        """
        if 'droplets-starter' not in self.name:
            raise ValueError("|ERROR| The droplet name pattern must contain 'droplets-starter'")
