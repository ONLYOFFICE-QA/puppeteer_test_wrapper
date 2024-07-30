# -*- coding: utf-8 -*-
import time
import digitalocean
from rich import print
from typing import Optional

from .droplet_info import DropletInfo
from ..digitalocean_prodjects import DigitalOceanProjects

class DropletException(Exception): ...

class Droplet:

    def __init__(self, do_token: str, manager: digitalocean.Manager, project: DigitalOceanProjects):
        self.__token = do_token
        self.__manager = manager
        self.__project = project

    def create(
            self,
            name: str,
            region: str,
            size_slug: str,
            image: str,
            ssh_keys: list = None,
            backups: bool = False,
            wait_until_up: bool = False
    ) -> digitalocean.Droplet:

        droplet = digitalocean.Droplet(
            token=self.__token,
            name=name,
            region=region,
            image=image,
            size_slug=size_slug,
            ssh_keys=ssh_keys,
            backups=backups
        )

        droplet.create()
        self.wait_until_status(droplet=droplet, status='active') if wait_until_up else None
        return droplet

    def info(self, droplet: "digitalocean.Droplet | str | int", load: bool = True) -> DropletInfo:
        return DropletInfo(self._get_droplet(droplet), load_droplet=load)

    def wait_until_status(
            self,
            droplet: "digitalocean.Droplet | str | int",
            status: str = 'active',
            interval: int = 10,
            wait_timeout: int = 300
    ) -> None:
        _droplet = self._get_droplet(droplet)
        start_time = time.perf_counter()
        print(f"[green]|INFO| Waiting for droplet [cyan]{_droplet.name}[/] to reach status '[cyan]{status}[/]'.")

        while time.perf_counter() - start_time < wait_timeout:
            current_status = DropletInfo(_droplet, load_droplet=True).get_status()

            if current_status.lower() == status.lower():
                print(
                    f"[green]|INFO| Droplet [cyan]{_droplet.name}[/]. "
                    f"Reached status [cyan]'{status}'[/]. ip: [cyan]`{_droplet.ip_address}`"
                )
                return

            print(
                f"[green]|INFO| Current status of droplet [cyan]{_droplet.name}[/]: "
                f"'[cyan]{current_status}[/]'. Waiting..."
            )

            time.sleep(interval)

        print(
            f"[red]|ERROR| Timeout reached. "
            f"Droplet [cyan]{_droplet.name}[/] did not reach status [cyan]'{status}'[/] within "
            f"[cyan]{wait_timeout}[/] seconds."
        )
        raise DropletException()

    def get_droplet_names(self) -> list[str]:
        return [droplet.name for droplet in self.get_all()]

    @staticmethod
    def delete(droplet: digitalocean.Droplet) -> None:
        if not isinstance(droplet, digitalocean.Droplet):
            return print(f"[red]|ERROR| Can't delete. droplet type must be digitalocean.Droplet")

        info = DropletInfo(droplet).get_basic_info()

        droplet.destroy()

        print(
            f"[bold red]|INFO| Droplet: [cyan]{info['Name']}[/] ip: [cyan]`{info['IP Address']}`[/]\n"
            f"Created At [cyan]{info['Created At']}[/]\n"
            f"has been removed."
        )

    def get_all(self) -> list[digitalocean.Droplet]:
        return self.__manager.get_all_droplets()

    def get_by_name(self, name: str) -> Optional[digitalocean.Droplet]:
        for droplet in self.get_all():
            if droplet.name == name:
                return droplet
        return None

    def get_by_id(self, droplet_id: int) -> Optional[digitalocean.Droplet]:
        try:
            droplet = digitalocean.Droplet(token=self.__token, id=droplet_id)
            droplet.load()
            return droplet
        except digitalocean.baseapi.DataReadError as e:
            print(f"[red]|ERROR| Droplet retrieval error: {e}")
            return None


    def get_project_name_by_droplet(self, droplet: "digitalocean.Droplet | str | int") -> Optional[str]:
        droplet_id = self.info(self._get_droplet(droplet), load=False).get_id()
        for project in self.__project.get_all():
            if f"do:droplet:{droplet_id}" in project.get_all_resources():
                return project.name

    def check_in_project(
            self,
            droplet: "digitalocean.Droplet | str | int",
            project: digitalocean.Project | str | int
    ) -> bool:
        droplet_id = self.info(self._get_droplet(droplet), load=False).get_id()
        return f"do:droplet:{droplet_id}" in self.__project.get_all_resources(project)

    def move_to_project(
            self,
            droplet: digitalocean.Droplet | str | int,
            project: digitalocean.Project | str | int
    ) -> Optional[bool]:
        _droplet_info = DropletInfo(self._get_droplet(droplet))
        project_name = self.__project.get_name(project)

        if self.check_in_project(droplet=droplet, project=project):
            return print(
                f"[magenta]|INFO| Droplet [cyan]{_droplet_info.get_name()}[/] "
                f"is already in project [cyan]{project_name}[/]"
            )

        print(f"[green]|INFO| Move {_droplet_info.get_name()} to {project_name}")
        return self.__project.assign_resource(project, resources=[f'do:droplet:{_droplet_info.get_id()}'])

    def _get_droplet(self, droplet: "digitalocean.Droplet | str | int") -> digitalocean.Droplet:
        if isinstance(droplet, digitalocean.Droplet):
            return droplet
        elif isinstance(droplet, str):
            return self.get_by_name(droplet)
        elif isinstance(droplet, int):
            return self.get_by_id(droplet)
        else:
            print(f"[red]|ERROR| Droplet type mast be string integer or digitalocean.Droplet")
            raise DropletException()
