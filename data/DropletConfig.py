# -*- coding: utf-8 -*-
import json
from os import getcwd
from os.path import join

from pydantic import BaseModel
from .decorators import singleton


class ConfigModel(BaseModel):
    DROPLET_NAME: str
    DROPLET_REGION: str
    DROPLET_IMAGE: str
    DROPLET_SIZE: str
    DEFAULT_USER: str
    SSH_DO_USER_NAME: str
    DO_PROJECT_NAME: str


@singleton
class DropletConfig:
    def __init__(self, config_path: str = join(getcwd(), 'configs', 'droplet_config.json')):
        self._config = self._load_config(config_path)
        self.name = f"droplets-starter-{self._config.DROPLET_NAME.strip()}"
        self.region = self._config.DROPLET_REGION
        self.image = self._config.DROPLET_IMAGE
        self.size = self._config.DROPLET_SIZE
        self.default_user = self._config.DEFAULT_USER
        self.ssh_do_user_name = self._config.SSH_DO_USER_NAME
        self.do_project_name = self._config.DO_PROJECT_NAME
        self._verify_droplet_name_pattern()

    @staticmethod
    def _load_config(file_path: str) -> ConfigModel:
        with open(file_path, 'r') as f:
            return ConfigModel(**json.load(f))

    def _verify_droplet_name_pattern(self):
        if 'droplets-starter' not in self.name:
            raise ValueError("|ERROR| The droplet name pattern must contain 'droplets-starter'")
