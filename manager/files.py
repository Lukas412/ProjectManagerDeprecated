import glob
import os
import itertools


class StructureMatcher:

    def __init__(self, structure: dict):
        self.structure = structure

    def match(self, path: str) -> bool:
        for structure_path in self.structure:
            if not glob.glob(os.path.join(path, structure_path)):
                return False
        return True


class File:

    def __init__(self, path: str):
        self.path: str = path
        self.name: str = os.path.basename(path)
        self.type: str = os.path.splitext(path)[1][1:]


class Structure:

    def __init__(self, path: str, type_: str):
        self.path: str = path
        self.name: str = os.path.basename(path)
        self.type: str = type_


class Directory:

    def __init__(self, path: str, extensions: dict, structures: dict):
        self.path: str = path
        self.extensions: dict = extensions
        self.structures: dict = structures

        self.files: list = []
        self.formations: list = []
        self.directories: list = []

        for file_name in os.listdir(path):
            file_path: str = os.path.join(path, file_name)

            if os.path.isfile(file_path) and self.match_extensions(file_path):
                self.files.append(File(file_path))

            elif os.path.isdir(file_path) and self.match_structures(file_path):
                self.formations.append(Structure(file_path, self.match_structures(file_path)))

            else:
                self.directories.append(Directory(os.path.join(path, file_name), extensions, structures))

    def match_extensions(self, path):
        return os.path.splitext(path)[1][1:] in self.extensions

    def match_structures(self, path: str) -> str:
        for structure_type, structure in self.structures.items():
            if structure['match'].match(path):
                return structure_type
        return ''

    def __iter__(self):
        for file in itertools.chain(*map(iter, self.directories)):
            yield file

        for file in self.files:
            yield file

        for formation in self.formations:
            yield formation
