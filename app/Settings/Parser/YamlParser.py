import os, yaml
from typing import Self


class YamlParser:
    __yaml_files: list = []
    __config: dict = {}

    def __init__(self, path: str = 'config/'):
        self.path = path
        self.set_yaml_file_to_load(self.path)

    def set_yaml_file_to_load(self, path: str) -> Self:
        if os.path.isdir(path):
            for element in os.listdir(path):
                full_path = os.path.join(path, element)
                if os.path.isdir(full_path):
                    self.__load_files(full_path)
                if full_path.endswith(".yaml"):
                    self.__yaml_files.append(full_path)

        elif os.path.isfile(path) and path.endswith(".yaml"):
            self.__yaml_files.append(path)

        self.__set_yaml_config()
        return self

    def __set_yaml_config(self) -> Self:
        for yaml_file in self.__yaml_files:
            with open(yaml_file, 'r') as stream:
                self.__config.update(yaml.safe_load(stream))
        return self

    def __str__(self):
        return str(self.__class__) + "\nYAML::\n" + str(yaml.dump(self.__config, indent=4))

    def __getattr__(self, attribute):
        if attribute in self.__config:
            return self.__config[attribute]
        else:
            raise AttributeError(
                'The attribute “%s” does not exist in any .yaml subfile in the “%s” directory' % (attribute, self.path))
