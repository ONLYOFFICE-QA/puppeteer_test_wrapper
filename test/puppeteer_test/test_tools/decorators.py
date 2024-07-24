# -*- coding: utf-8 -*-
from functools import wraps
from rich import print

import digitalocean


def droplet_exists(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):

        if not self.droplet:
            return print("[red]|ERROR| Droplet was not found.")
        elif not isinstance(self.droplet, digitalocean.Droplet):
            return print("[red]|ERROR| Droplet must be of type digitalocean.Droplet")

        return method(self, *args, **kwargs)

    return wrapper
