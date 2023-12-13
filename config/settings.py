from tomllib import load as toml_load

class Settings:
    def __init__(self) -> None:
        with open('eromodapi/config.toml','rb') as f:
            data = toml_load(f)
        self.__config = data

    @property
    def config(self):
        return self.__config






settings = Settings()