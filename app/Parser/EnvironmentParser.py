import dotenv
from typing import Iterable


class EnvironmentParser:
    DEBUG: bool = False

    def __init__(self, file: str = '.env') -> None:
        self.__file_env = file
        self.__raw_env = dotenv.dotenv_values(file)
        self.DEBUG = False if not self.get_env('DEBUG') else (
            True if self.get_env('DEBUG').lower() in ('true', '1', 1 ) else False
        )

    def get_env(self, key) -> str:
        for index, value in self.__raw_env.items():
            if index == key:
                return value
    def all(self)-> Iterable[str]:
        for key, value in self.__raw_env.items():
            yield key, value

    def __getattr__(self, attribute):
        if attribute in self.__raw_env:
            return self.get_env(attribute)
        else:
            raise AttributeError('The attribute “%s” does not exist in “%s” file' % (attribute, self.__file_env))

    def __str__(self) -> str:
        environmentItems: str = "Environment Variables:"
        for k, value in self.__raw_env.items():
            environmentItems += "\n\t" + k + " => " + value
        return str(self.__class__) + "\n" + environmentItems
