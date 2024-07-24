from invoke import task
from rich.prompt import Prompt
from rich import print

from test import PuppeteerTest


@task
def run_test(
        c,
        save_droplet: bool = False,
        firefox: bool = False,
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

    PuppeteerTest(firefox=firefox, flags=puppeteer_flags).run(save_droplet=save_droplet)

@task
def create_droplet(c):
    PuppeteerTest().test.create_test_droplet()

@task
def delete_droplet(c):
    test = PuppeteerTest().test
    test.droplet = test.do.droplet.get_by_name(test.droplet_config.name)

    if not test.droplet:
        return print(f"[red]|INFO| The Droplet [cyan]{test.droplet_config.name}[/] was not found")

    msg = (
        f"[red]|WARNING| Will be deleted droplet: "
        f"[cyan]{test.droplet.name}[/] ip: [cyan]{test.droplet.ip_address}[/] want to continue?"
    )

    if Prompt.ask(msg, choices=["Y", "N"], default='n').upper() == "Y":
        test.delete_test_droplet()
