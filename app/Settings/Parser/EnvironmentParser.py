import dotenv


class EnvironmentParser:

    def __init__(self, file: str = '.env') -> None:
        self.__file_env = file
        self.__raw_env = dotenv.dotenv_values(file)

    def get_env(self, key) -> str:
        for index, value in self.__raw_env.items():
            if index == key:
                return value

    def __getattr__(self, attribute):
        if attribute in self.__raw_env:
            return self.get_env(attribute)
        else:
            raise AttributeError('The attribute “%s” does not exist in “%s” file'% (attribute, self.__file_env))

    def __str__(self) -> str:
        environmentItems: str = "Environment Variables:"
        for k, value in self.__raw_env.items():
            environmentItems += "\n\t" + k + " => " + value
        return str(self.__class__) + "\n" + environmentItems
