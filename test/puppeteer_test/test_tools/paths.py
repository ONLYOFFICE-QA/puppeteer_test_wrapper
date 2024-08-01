# -*- coding: utf-8 -*-
from os import getcwd
from posixpath import join, basename
from data.decorators import singleton


@singleton
class Paths:
    """
    A singleton class that defines various file paths used in the Puppeteer test environment.
    """
    remote_home_dir: str = '/root'
    puppeter_run_sh_name: str = 'puppeteer_run.sh'
    puppeter_config_file_name: str = 'puppeteer_config.json'
    puppeteer_archive_name: str = 'puppeteer.zip'

    tmp_dir: str = join(getcwd(), 'tmp')

    local_dep_test = join(tmp_dir, 'Dep.Tests')
    local_puppeteer_dir = join(local_dep_test, 'puppeteer')

    local_report_dir: str = join(getcwd(), 'Reports')
    local_puppeter_config_file: str = join(getcwd(), puppeter_config_file_name)
    local_puppeteer_archive = join(tmp_dir, puppeteer_archive_name)

    remote_puppeteer_dir: str = join(remote_home_dir, 'Dep.Tests', 'puppeteer')
    remote_puppeter_config_file: str = join(remote_home_dir, basename(local_puppeter_config_file))
    remote_puppeter_run_sh: str = join(remote_home_dir,  puppeter_run_sh_name)
    remote_report_dir: str = join(remote_puppeteer_dir, 'out')
    remote_result_archive: str = join(remote_home_dir, 'result.zip')
    remote_puppeteer_archive: str = join(remote_home_dir, puppeteer_archive_name)
    remote_puppeteer_engine: str = join(remote_puppeteer_dir, 'engine')
