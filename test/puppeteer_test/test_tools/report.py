# -*- coding: utf-8 -*-
from os.path import join, isfile, basename, exists
from rich import print

from host_tools import File, Dir
from tempfile import gettempdir

from ssh_wrapper import Sftp

from .file_paths import FilePaths
from bs4 import BeautifulSoup


class Report:

    def __init__(self, version: str, browser: str, tmp_dir: str = None):
        self.__paths = FilePaths()
        self.dir = join(self.__paths.local_report_dir, version, browser.lower())
        self.path = join(self.dir, 'out', 'report.html')
        self.tmp_dir = tmp_dir or gettempdir()
        self.archive_path = join(self.tmp_dir, basename(self.__paths.remote_result_archive))
        Dir.create(self.dir, stdout=False)


    def download(self, sftp: Sftp) -> None:
        sftp.download_file(self.__paths.remote_result_archive, self.archive_path, stdout=True)
        Dir.delete(self.dir, clear_dir=True, stdout=False) if exists(self.dir) else None
        File.unpacking_zip(self.archive_path, self.dir, delete_archive=True)

    def convert_paths_to_relative(self):
        if not isfile(self.path):
            return print(f"[red]|WARNING| Report not exists {self.path}")

        soup = BeautifulSoup(File.read(self.path), 'html.parser')

        for a in soup.find_all('a', href=True):
            a['href'] = a['href'].replace(self.__paths.remote_report_dir, '.')

        for td in soup.find_all('td'):
            if td.string and 'self.__paths.remote_report_dir' in td.string:
                td.string = td.string.replace(self.__paths.remote_report_dir, '.')

        File.write(self.path, str(soup), encoding='utf-8')
