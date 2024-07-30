# -*- coding: utf-8 -*-
from typing import Optional
from rich import print

import digitalocean

class DigitalOceanProjects:

    def __init__(self, manager: digitalocean.Manager):
        self.manager = manager

    def get_all_resources(self, project: "digitalocean.Project | str | int"):
        return self._get_project(project).get_all_resources()

    def get_all(self) -> list[digitalocean.Project]:
        return self.manager.get_all_projects()

    def get_id(self, project: "digitalocean.Project | str | int") -> int:
        return self._get_project(project).id

    def get_name(self, project: "digitalocean.Project | int"):
        return self._get_project(project).name

    def get_by_name(self, project_name: str) -> Optional[digitalocean.Project]:
        for project in self.get_all():
            if project.name == project_name:
                return project
        return None

    def get_by_id(self, project_id: int) -> digitalocean.Project:
        return self.manager.get_project(project_id=project_id)

    def get_info(self, project: "digitalocean.Project | str | int") -> dict:
        _project = self._get_project(project)
        return {
            "ID": _project.id,
            "Name": _project.name,
            "Purpose": _project.purpose,
            "Environment": _project.environment,
            "Description": _project.description,
            "Created At": _project.created_at
        }

    def assign_resource(self, project: "digitalocean.Project | str | int", resources) -> Optional[bool]:
        project = self._get_project(project)
        return project.assign_resource(resources) if project else None

    def _get_project(self, project: "digitalocean.Project | str | int") -> Optional[digitalocean.Project]:
        if isinstance(project, digitalocean.Project):
            return project
        elif isinstance(project, str):
            return self.get_by_name(project_name=project)
        elif isinstance(project, int):
            return self.get_by_id(project)
        else:
            return print(f"[red]|ERROR| Can't get project by {project}")
