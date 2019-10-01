import json

from .project import Project


class Manager:

    def __init__(self):
        with open("config.json") as file:
            config = json.load(file)

        self.project = Project('TestProject')
        self.project.load(config)

        self.project.sort_files()
