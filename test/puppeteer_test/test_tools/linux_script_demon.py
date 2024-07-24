# -*- coding: utf-8 -*-
from posixpath import join
from tempfile import gettempdir

class LinuxScriptDemon:
    services_dir = join('/etc', 'systemd', 'system')

    def __init__(self, exec_script_path: str, user: str, name: str = 'my_script.service'):
        self.exec_script_path = exec_script_path
        self.name = name
        self.user = user

    def generate(self) -> str:
        return f'''\
    [Unit]
    Description=CustomBashScript

    [Service]
    Type=simple
    ExecStart=/bin/bash {self.exec_script_path}
    User={self.user}

    [Install]
    WantedBy=multi-user.target\
    '''.strip()

    def start_demon_commands(self) -> list:
        return [
            f'chmod +x {self.exec_script_path}',
            'sudo systemctl daemon-reload',
            f'sudo systemctl start {self.name}'
        ]

    def change_service_dir_access_cmd(self) -> list:
        return [
            f'sudo chown {self.user}:{self.user} {self.services_dir}',
            f'sudo chmod u+w {self.services_dir}'
        ]

    def create(self, save_path: str = None) -> str:
        _save_path = save_path or join(gettempdir(), self.name)
        with open(_save_path, mode='w', newline='') as file:
            file.write('\n'.join(line.strip() for line in self.generate().split('\n')))
        return _save_path
