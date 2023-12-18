from typing import Generator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from eromodapi.schema.user import user_api #noqa
from eromodapi.model.base import SessionLocal #noqa

def get_db()->Generator:
    """获取关系型数据库会话
    """
    with SessionLocal() as session:
        yield session

oauth2_schema=OAuth2PasswordBearer(tokenUrl='token')
def get_user_info(token=Depends(oauth2_schema),db=Depends(get_db))->dict:
    """获取已登录的用户信息
    """
    user = user_api.jwt_decode(token)
    return dict(id=user['id'],db=db)