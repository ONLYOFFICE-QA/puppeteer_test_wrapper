# -*- coding: utf-8 -*-
from os.path import join, expanduser
from io import open as io_open


class Token:
    token_file_path: str = join(expanduser('~'), '.do', 'access_token')

    def get(self):
        return self._read_file(self.token_file_path).strip()

    @staticmethod
    def _read_file(file_path: str, mode: str = 'r', encoding='utf-8') -> str:
        with io_open(file_path, mode, encoding=encoding) as file:
            return file.read()
