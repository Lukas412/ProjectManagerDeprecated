import os
import json
import shutil

from .files import Directory


class Project:

    CONFIG = '.project_config.json'

    def __init__(self, path: str):
        self.path = path

        self.name = None
        self.description = None
        self.tags = None

        self.structure = None
        self.structure_tags = None
        self.directory = None

    def load(self, config: dict) -> None:
        self.load_config()

        if 'structure' in config:
            self.load_structure(config['structure'])

        self.load_files()

    def load_config(self) -> None:
        config_path = os.path.join(self.path, Project.CONFIG)

        if not os.path.isfile(config_path):
            return

        with open(config_path) as file:
            try:
                config = json.load(file)

            except json.decoder.JSONDecodeError:
                return

            except Exception:
                raise

        if 'name' in config:
            self.name = config['name']

        if not self.name:
            self.name = os.path.basename(self.path)

        if 'description' in config:
            self.description = config['description']

        if 'tags' in config:
            self.tags = config['tags']

    def save_config(self) -> None:
        config_path = os.path.join(self.path, Project.CONFIG)
        config = {'name': self.name, 'description': self.description, 'tags': self.tags}

        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4, sort_keys=True)

    def load_structure(self, structure: dict) -> None:
        def load_structure_paths(current_path: list, structure_path: dict) -> None:
            if '.' in structure_path:
                for structure_path_type in structure_path['.']:
                    for file_type in types[structure_path_type]:
                        if file_type not in files:
                            files[file_type] = []

                        files[file_type].append(os.path.join(*current_path))

            for path in structure_path.keys():
                if path == '.':
                    continue

                next_path = current_path[:]
                next_path.append(path)

                load_structure_paths(next_path, structure_path[path])

        if 'files' not in structure or 'paths' not in structure:
            return

        structure_files = structure['files']
        structure_paths = structure['paths']

        files = {}

        types = {}
        for type_, type_files in structure_files.items():
            types[type_] = type_files["extension"]

        load_structure_paths([], structure_paths)

        structure_tags = {}

        for type_, type_files in structure_files.items():
            for file_extension in type_files["extension"]:
                structure_tags[file_extension] = type_files["tags"]

        self.structure = files
        self.structure_tags = structure_tags

    def load_files(self) -> None:
        self.directory = Directory(self.path)

        self.tags = []
        for file in self.directory:
            if file.type in self.structure_tags:
                for tag in self.structure_tags[file.type]:
                    if tag not in self.tags:
                        self.tags.append(tag)

    def sort_files(self) -> None:
        for file in self.directory:
            if file.type in self.structure:
                delete: bool = True

                for path in self.structure[file.type]:
                    path_to = os.path.join(self.path, path, file.name)

                    if file.path != path_to:
                        print('copy \'{}\' to \'{}\''.format(file.path, path_to))

                        os.makedirs(os.path.dirname(path_to), exist_ok=True)
                        shutil.copy(os.path.join('.\\', file.path), path_to)

                    else:
                        delete = False

                if delete:
                    print('remove \'{}\''.format(file.path))
                    os.remove(os.path.join('.\\', file.path))

        delete = True
        while delete:
            delete = False

            for path, directories, files in os.walk(self.path):
                if not directories and not files:
                    print('remove \'{}\''.format(path))
                    os.rmdir(path)

                    delete = True

    def __del__(self):
        self.save_config()
