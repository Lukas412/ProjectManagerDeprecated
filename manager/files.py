import os
import itertools


class File:

    def __init__(self, path: str):
        self.path: str = path
        self.name: str = os.path.basename(path)
        self.type: str = os.path.splitext(path)[1][1:]


class Directory:

    def __init__(self, path: str):
        self.path: str = path

        self.files: list = []
        self.directories: list = []

        for file_name in os.listdir(path):
            if os.path.isfile(os.path.join(path, file_name)):
                file: File = File(os.path.join(path, file_name))
                self.files.append(file)

            else:
                self.directories.append(Directory(os.path.join(path, file_name)))

    def __iter__(self):
        for file in itertools.chain(*map(iter, self.directories)):
            yield file

        for file in self.files:
            yield file
