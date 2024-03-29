import argparse
import json
import os

from .project import Project


class Manager:

    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='ProjectManager', usage='--help to view the usage',
                                              description='An engine to manage your projects. '
                                                          'It\'s designed to keep the process clean and sorted.',
                                              add_help=True)

        self.parser.add_argument('command', type=str, choices=['backup', 'check', 'init', 'release', 'sort'],
                                 help='command to run')
        self.parser.add_argument('-p', '--path', default='.', type=str, help='path of the project')

        self.args = self.parser.parse_args()

        os.chdir(self.args.path)
        with open(os.path.join(os.path.dirname(__file__), '../config.json')) as file:
            self.config = json.load(file)

        self.run(self.args.command)

    def run(self, command: str):
        if command in ['backup', 'check', 'init', 'release', 'sort']:
            project = Project('.')
            project.load(self.config)

            if command == 'backup':
                project.backup()

            elif command == 'check':
                project.check_files()

            elif command == 'release':
                project.release()

            elif command == 'sort':
                project.sort_files()
