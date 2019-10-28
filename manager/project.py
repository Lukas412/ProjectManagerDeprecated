import os
import json
import shutil

from .files import Directory, StructureMatcher, File, Structure


class Project:

    CONFIG_PATH = '.project_config.json'

    def __init__(self, path: str):
        self.path = path

        self.name = None
        self.description = None
        self.tags = None

        self.extensions = None
        self.structures = None
        self.directory = None

    def load(self, config: dict) -> None:
        self.load_config()

        if 'structure' in config:
            self.load_structure(config['structure'])

        self.load_files()

    def load_config(self) -> None:
        self.name = os.path.basename(os.path.dirname(os.path.join(os.getcwd(), self.path)))
        config_path = os.path.join(self.path, Project.CONFIG_PATH)

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

        if 'description' in config:
            self.description = config['description']

        if 'tags' in config:
            self.tags = config['tags']

    def save_config(self) -> None:
        config_path = os.path.join(self.path, Project.CONFIG_PATH)
        config = {
            'name': self.name,
            'description': self.description,
            'tags': self.tags,
            'files': [file.path for file in self.directory]
        }

        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4, sort_keys=True)

    def load_structure(self, config_structure: dict) -> None:
        self.extensions = {}
        self.structures = {}

        for file_type, file_type_spec in config_structure.items():
            if 'path' not in file_type_spec or 'tags' not in file_type_spec:
                continue

            if 'extensions' in file_type_spec:
                for extension in file_type_spec['extensions']:
                    self.extensions[extension] = {
                        'path': os.path.normpath(file_type_spec['path']),
                        'tags': file_type_spec['tags']
                    }

            if 'structure' in file_type_spec:
                if file_type not in self.structures:
                    self.structures[file_type] = []

                self.structures[file_type].append({
                    'match': StructureMatcher(file_type_spec['structure']),
                    'path': os.path.normpath(file_type_spec['path']),
                    'tags': file_type_spec['tags']
                })

            if 'structures' in file_type_spec:
                if file_type not in self.structures:
                    self.structures[file_type] = []

                for structure in file_type_spec['structures']:
                    self.structures[file_type].append({
                        'match': StructureMatcher(structure),
                        'path': os.path.normpath(file_type_spec['path']),
                        'tags': file_type_spec['tags']
                    })

    def load_files(self) -> None:
        self.directory = Directory(self.path, [self.__class__.CONFIG_PATH], self.extensions, self.structures)

        self.tags = []
        for file in self.directory:
            if type(file) == File:
                for tag in self.extensions[file.type]['tags']:
                    if tag not in self.tags:
                        self.tags.append(tag)

            elif type(file) == Structure:
                for structure in self.structures[file.type]:
                    for tag in structure['tags']:
                        if tag not in self.tags:
                            self.tags.append(tag)

    def check_files(self) -> None:
        for file in self.directory:
            if file.path == os.path.join(self.path, Project.CONFIG_PATH):
                continue

            if type(file) == File:
                path_to = os.path.join(self.path, self.extensions[file.type]['path'], file.name)

                if file.path != path_to:
                    print('move \'{}\' to \'{}\''.format(file.path, path_to))

            elif type(file) == Structure:
                for structure in self.structures[file.type]:
                    path_to = os.path.join(self.path, structure['path'], file.name)

                    if file.path != path_to:
                        print('move \'{}\' to \'{}\''.format(file.path, path_to))

    def sort_files(self) -> None:
        for file in self.directory:
            if file.path == os.path.join(self.path, Project.CONFIG_PATH):
                continue

            if type(file) == File:
                path_to = os.path.join(self.path, self.extensions[file.type]['path'], file.name)

                if file.path != path_to:
                    print('copy \'{}\' to \'{}\''.format(file.path, path_to))

                    os.makedirs(os.path.dirname(path_to), exist_ok=True)
                    shutil.copy(os.path.join('.\\', file.path), path_to)

                    print('remove \'{}\''.format(file.path))
                    os.remove(os.path.join('.\\', file.path))

            elif type(file) == Structure:
                for structure in self.structures[file.type]:
                    path_to = os.path.join(self.path, structure['path'], file.name)

                    if file.path != path_to:
                        print('copy \'{}\' to \'{}\''.format(file.path, path_to))

                        os.makedirs(os.path.dirname(path_to), exist_ok=True)
                        try:
                            shutil.copytree(os.path.join('.\\', file.path), path_to)

                        except FileExistsError:
                            print('copy failed file exists')

                        print('remove \'{}\''.format(file.path))
                        shutil.rmtree(os.path.join('.\\', file.path))

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
