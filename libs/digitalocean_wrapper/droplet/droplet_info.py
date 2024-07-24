# -*- coding: utf-8 -*-
from typing import Optional
from rich import print

import digitalocean
from functools import wraps

def droplet_exists(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):

        if not self.droplet:
            return print("[red]|ERROR| Droplet was not found.")
        elif not isinstance(self.droplet, digitalocean.Droplet):
            return print("[red]|ERROR| Droplet must be of type digitalocean.Droplet")

        return method(self, *args, **kwargs)

    return wrapper

class DropletInfo:
    def __init__(self, droplet: digitalocean.Droplet, load_droplet: bool = True):
        self.droplet = droplet
        self._load_droplet() if load_droplet else None

    @droplet_exists
    def get_status(self) -> Optional[str]:
        return self.droplet.status

    @droplet_exists
    def get_basic_info(self):
        info = {
            "ID": self.droplet.id,
            "Name": self.droplet.name,
            "Memory": self.droplet.memory,
            "VCPUs": self.droplet.vcpus,
            "Disk": self.droplet.disk,
            "Region": self.droplet.region['name'],
            "Image": self.droplet.image['slug'],
            "Size": self.droplet.size_slug,
            "IP Address": self.droplet.ip_address,
            "Status": self.droplet.status,
            "Created At": self.droplet.created_at
        }
        return info

    @droplet_exists
    def get_id(self):
        return self.droplet.id

    @droplet_exists
    def get_name(self) -> str:
        return self.droplet.name

    @droplet_exists
    def get_ip_address(self) -> str:
        return self.droplet.ip_address

    @droplet_exists
    def get_created_at_date(self) -> str:
        return self.droplet.created_at

    @droplet_exists
    def get_networks(self) -> list:
        return self.droplet.networks

    @droplet_exists
    def get_snapshots(self) -> list:
        return [snapshot.name for snapshot in self.droplet.get_snapshots()]

    @droplet_exists
    def get_actions(self) -> list:
        actions = self.droplet.get_actions()
        return [{"id": action.id, "type": action.type, "status": action.status} for action in actions]

    def _load_droplet(self) -> None:
        try:
            self.droplet.load()
        except digitalocean.baseapi.DataReadError as e:
            print(f"[red]|ERROR| Droplet retrieval error: {e}")
            self.droplet = None
