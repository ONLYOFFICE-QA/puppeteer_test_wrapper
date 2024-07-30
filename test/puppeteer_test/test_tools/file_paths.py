# -*- coding: utf-8 -*-
from os import getcwd
from posixpath import join, basename
from data.decorators import singleton


@singleton
class FilePaths:
    remote_home_dir = '/root'
    puppeter_run_sh_name = 'puppeteer_run.sh'
    puppeter_config_file_name = 'puppeteer_config.json'

    local_report_dir = join(getcwd(), 'Reports')
    local_puppeter_config_file = join(getcwd(), puppeter_config_file_name)

    remote_puppeteer_dir = join(remote_home_dir, 'Dep.Tests', 'puppeteer')
    remote_puppeter_config_file = join(remote_home_dir, basename(local_puppeter_config_file))
    remote_puppeter_run_sh = join(remote_home_dir,  puppeter_run_sh_name)
    remote_report_dir = join(remote_puppeteer_dir, 'out')
    remote_result_archive = join(remote_home_dir, 'result.zip')
    remote_puppeteer_archive = join(remote_home_dir, 'puppeteer.zip')
    remote_puppeteer_engine = join(remote_puppeteer_dir, 'engine')
