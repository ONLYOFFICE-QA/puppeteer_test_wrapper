from invoke import task
from rich.prompt import Prompt
from rich import print
from digitalocean_wrapper import DigitalOceanWrapper

from data import DropletConfig
from test import PuppeteerTest


@task
def run_test(
        c,
        save_droplet: bool = False,
        retries: int = None,
        threads: int = None,
        url_param: str = None,
        params: int = None,
        prcache: bool = None
):
    puppeteer_flags = {
        "retries": retries,
        "threads": threads,
        "url_param": url_param,
        "params": params,
        "prcache": prcache
    }

    PuppeteerTest(flags=puppeteer_flags).run(save_droplet=save_droplet)

@task
def create_droplet(c):
    PuppeteerTest().test.create_test_droplet()

@task
def delete_droplet(c):
    do = DigitalOceanWrapper()
    droplet_config = DropletConfig()

    droplet = do.droplet.get_by_name(droplet_config.name)

    if not droplet:
        return print(f"[red]|INFO| The Droplet [cyan]{droplet_config.name}[/] was not found")

    msg = (
        f"[red]|WARNING| Will be deleted droplet: "
        f"[cyan]{droplet.name}[/] ip: [cyan]{droplet.ip_address}[/] want to continue?"
    )

    if Prompt.ask(msg, choices=["Y", "N"], default='n').upper() == "Y":
        do.droplet.delete(droplet)
