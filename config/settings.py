from tomllib import load as toml_load
from jhu.security import HashAPI,JWTAPI
from enum import Enum


class AuthType(int,Enum):
    """用户鉴权认证类型

    PASSWORD:密码
    DINGTALK:钉钉
    FEISHU:飞书
    """
    PASSWORD=0
    DINGTALK=1
    FEISHU=2

class UserStatus(int,Enum):
    """用户状态

    DISABLE:禁用状态
    ENABLE:启用状态
    """
    DISABLE=0
    ENABLE=1


class Settings():
    def __init__(self) -> None:
        with open('eromodapi/config.toml','rb') as f:
            data = toml_load(f)
        self.__config = data

    @property
    def config(self):
        return self.__config

settings = Settings()
hash_api = HashAPI(settings.config.get('hash_key',''))
jwt_api = JWTAPI(settings.config.get('jwt_key',''),60*24*7)