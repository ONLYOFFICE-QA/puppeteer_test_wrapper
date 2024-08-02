# -*- coding: utf-8 -*-
from rich import print
from functools import wraps
import digitalocean


def singleton(class_):
    __instances = {}

    @wraps(class_)
    def getinstance(*args, **kwargs):
        if class_ not in __instances:
            __instances[class_] = class_(*args, **kwargs)
        return __instances[class_]

    return getinstance

def droplet_exists(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):

        if not self.droplet:
            return print("[red]|ERROR| Droplet was not found.")
        elif not isinstance(self.droplet, digitalocean.Droplet):
            return print("[red]|ERROR| Droplet must be of type digitalocean.Droplet")

        return method(self, *args, **kwargs)

    return wrapper

