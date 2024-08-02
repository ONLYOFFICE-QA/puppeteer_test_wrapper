# -*- coding: utf-8 -*-
from os.path import dirname, basename
from typing import Optional
from rich import print


from digitalocean_wrapper import DigitalOceanWrapper
from rich.prompt import Prompt

from data import DropletConfig


class DigitalOceanSshKeyError(Exception):
    """
    Exception raised when there is an error retrieving or creating an SSH key on DigitalOcean.
    """
    pass

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
        self.local_ssh_key_path = self.do.ssh_key.default_pub_key_path
        self.local_pub_key = self._get_local_public_key()

    def get_keys_id(self) -> list:
        """
        Retrieve the list of SSH key IDs to be used for the DigitalOcean droplet.

        :return: A list of SSH key IDs.
        :raises DigitalOceanSshKeyError: If no SSH key ID can be retrieved or created.
        """
        ssh_key = self.get_id_by_pub_key() or self.create_ssh_key()
        if ssh_key:
            return [ssh_key]

        raise DigitalOceanSshKeyError(f"|ERROR| Cannot get digitalocean's ssh key id")

    def get_id_by_pub_key(self) -> Optional[int]:
        """
        Retrieve the SSH key ID by the default public key.

        :return: The SSH key ID if found; None otherwise.
        """
        ssh_key = self.do.ssh_key.get_by_pub_key(public_key=self.local_pub_key)

        if not ssh_key:
            return None

        print(
            f"[green]|INFO| For a key on the path: "
            f"[cyan]~/{basename(dirname(self.local_ssh_key_path))}/{basename(self.local_ssh_key_path)}[/], "
            f"DigitalOcean key will be used: [cyan]{ssh_key.name}[/]"
        )

        return ssh_key.id

    def create_ssh_key(self) -> Optional[int]:
        """
        Create a new SSH key on DigitalOcean using the default public key.

        :return: The SSH key ID if created; None otherwise.
        """
        ssh_key_name = self._get_ssh_key_name()

        if Prompt.ask(self._generate_creation_msg(ssh_key_name), choices=["Y", "N"], default='y').lower() == 'y':
            ssh_key = self.do.ssh_key.create(key_name=ssh_key_name, public_key=self.local_pub_key)
            return ssh_key.id if ssh_key else None

        return None

    def _get_ssh_key_name(self) -> str:
        """
        Prompt the user to enter a name for the SSH key to be added to DigitalOcean.

        The method ensures that the name entered by the user does not conflict with existing SSH key names
        on DigitalOcean. It repeatedly prompts the user until a unique name is provided.

        :return: A unique SSH key name that does not already exist on DigitalOcean.
        """
        existing_keys = set(self.do.ssh_key.get_all_ssh_key_names())

        while True:
            ssh_key_name = Prompt.ask(
                f"[red]Enter the name of the ssh key at path [cyan]{self.local_ssh_key_path}[/] to add to DigitalOcean"
            )
            if ssh_key_name in existing_keys:
                print(f"[bold red]|ERROR| A key named [cyan]{ssh_key_name}[/] already exists. Enter another name.")
            else:
                return ssh_key_name

    def _generate_creation_msg(self, ssh_key_name: str) -> str:
        """
        Generate a confirmation message for creating a new SSH key on DigitalOcean.

        :param ssh_key_name: The name to be assigned to the new SSH key.
        :return: The confirmation message.
        """
        return (
            f"[red]|INFO| Create an SSH Key named [cyan]{ssh_key_name}[/] "
            f"with public ssh key from path [cyan]{self.local_ssh_key_path}[/] on DigitalOcean?"
        )

    def _get_local_public_key(self):
        """
        Retrieve the contents of the local SSH public key.

        :return: The contents of the local SSH public key.
        :raises DigitalOceanSshKeyError: If the SSH public key is not found or is empty.
        """
        pub_key = self.do.ssh_key.read_default_pub_key(stderr=True)
        if not pub_key:
            raise DigitalOceanSshKeyError(
                f"|ERROR| SSH public key not found or empty at path {self.do.ssh_key.default_pub_key_path}"
            )
        return pub_key
