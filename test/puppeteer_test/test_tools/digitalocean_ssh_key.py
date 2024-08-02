# -*- coding: utf-8 -*-
from typing import Optional
from rich import print


from digitalocean_wrapper import DigitalOceanWrapper
from rich.prompt import Prompt

from data import DropletConfig


class DigitalOceanSshKeyError(Exception): ...

class DigitalOceanSshKey:
    """
    Class to manage SSH keys for a DigitalOcean droplet.
    """

    def __init__(self, droplet_config: DropletConfig, digital_ocean: DigitalOceanWrapper):
        """
        Initializes the DigitalOceanSshKey instance.

        :param droplet_config: Configuration object for the droplet.
        :param digital_ocean: Wrapper object to interact with DigitalOcean API.
        """
        self.droplet_config = droplet_config
        self.do = digital_ocean

    def get_keys_id(self) -> list:
        """
        Retrieve the list of SSH key IDs to be used for the DigitalOcean droplet.

        :return: A list of SSH key IDs.
        :raises DigitalOceanSshKeyError: If no SSH key ID can be retrieved or created.
        """
        ssh_key = self._get_id_by_name() or self._get_id_by_pub_key() or self._create_ssh_key()
        if ssh_key:
            return [ssh_key]

        raise DigitalOceanSshKeyError(f"|ERROR| Cannot get digitalocean's ssh key id")

    def _get_id_by_name(self) -> Optional[int]:
        """
        Retrieve the SSH key ID by the configured SSH key name.

        :return: The SSH key ID if found; None otherwise.
        """
        return self.do.ssh_key.get_id_by_name(self.droplet_config.ssh_do_user_name)

    def _get_id_by_pub_key(self) -> Optional[int]:
        """
        Retrieve the SSH key ID by the default public key.

        :return: The SSH key ID if found; None otherwise.
        """
        ssh_key = self.do.ssh_key.get_by_pub_key()
        return ssh_key.id if ssh_key else None

    def _create_ssh_key(self):
        """
        Create a new SSH key on DigitalOcean using the default public key.

        :return: The SSH key ID if created; None otherwise.
        """
        pub_key = self.do.ssh_key.read_default_pub_key(stderr=True)
        if pub_key:
            if self.droplet_config.ssh_do_user_name:
                if Prompt.ask(self._generate_creation_msg(), choices=["Y", "N"], default='y').lower() == 'y':
                    ssh_key = self.do.ssh_key.create(key_name=self.droplet_config.ssh_do_user_name, public_key=pub_key)
                    return ssh_key.id if ssh_key else None

                return None

            return print("|ERROR| You need to specify the name of the SSH key configured on DigitalOcean")

        return None

    def _generate_creation_msg(self) -> str:
        """
        Generate a confirmation message for creating a new SSH key on DigitalOcean.

        :return: The confirmation message.
        """
        return (
            f"[red]|INFO| Create an SSH Key named {self.droplet_config.ssh_do_user_name} "
            f"with public ssh key from path {self.do.ssh_key.default_pub_key_path} on DigitalOcean?"
        )
