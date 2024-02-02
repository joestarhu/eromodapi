from typing import Dict,List,Any
from enum import Enum
from pydantic_settings import BaseSettings
from jhu.security import HashAPI,JWTAPI

class BaseAppSettings(BaseSettings):
    """应用基础配置项
    """
    # FastAPI的应用
    debug:bool = False
    docs_url:str = "/docs"
    openapi_prefix:str = ""
    openapi_url:str = "/openapi.json"
    redoc_url:str = "/redoc"
    title:str = "EromodAPI"
    version:str = "1.0.0"

    # 安全
    hash_key:str='0f35268f93594811b1fb81e772a9e256'
    jwt_key:str='egw2zoumjUy1nilQ978ERZouywXbmRIQ64DHCDiPNVk'
    default_passwd:str='qwe321'

    # CORS跨域
    allow_origins:List[str] = ["*"]

    # 存储
    db_rds:str = ''

    class Config:
        # env文件名
        env_file=".env"
        # 额外参数忽略
        extra='ignore'

    @property
    def fastapi_kwargs(self)->Dict[str,Any]:
        return dict(
            debug=self.debug,
            docs_url=self.docs_url,
            openapi_prefix=self.openapi_prefix,
            openapi_url=self.openapi_url,
            redoc_url=self.redoc_url,
            title=self.title,
            version=self.version)

settings = BaseAppSettings()
hash_api = HashAPI(settings.hash_key)
jwt_api = JWTAPI(settings.jwt_key,60*24*7)

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
