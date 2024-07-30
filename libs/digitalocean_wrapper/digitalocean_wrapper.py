# -*- coding: utf-8 -*-
from typing import Optional

import digitalocean

from .auth import Token
from .digitalocean_prodjects import DigitalOceanProjects
from .droplet import Droplet


class DigitalOceanWrapper:

    def __init__(self):
        self.__token = Token().get()
        self.manager = digitalocean.Manager(token=self.__token)
        self.project = DigitalOceanProjects(manager=self.manager)
        self.droplet = Droplet(do_token=self.__token, manager=self.manager, project=self.project)

    def get_ssh_keys(self) -> list[digitalocean.SSHKey]:
        return self.manager.get_all_sshkeys()

    def get_all_ssh_keys_id(self) -> list:
        ssh_keys = self.get_ssh_keys()
        if ssh_keys:
            return [key.id for key in ssh_keys]
        return []

    def get_ssh_key_id_by_name(self, ssh_key_name: str) -> Optional[int]:
        ssh_keys = self.get_ssh_keys()

        for ssh_key in ssh_keys if ssh_keys else []:
            if ssh_key.name.lower() == ssh_key_name.lower():
                return ssh_key.id

        print(f"[red]|ERROR| Ssh key id for {ssh_key_name} was not found.")
        return None
