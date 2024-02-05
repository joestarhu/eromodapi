from typing import Generator
from fastapi import Depends,Query
from fastapi.security import OAuth2PasswordBearer
from eromodapi.schema.user import user_api #noqa
from eromodapi.model.base import SessionLocal #noqa

def get_db()->Generator:
    """获取关系型数据库会话
    """
    with SessionLocal() as session:
        yield session


oauth2_schema=OAuth2PasswordBearer(tokenUrl='/user/login')
def get_user(token=Depends(oauth2_schema),db=Depends(get_db))->dict:
    """获取已登录的用户信息,并校验用户的合法性..
    """
    user = user_api.jwt_decode(db,token)
    return dict(id=user['user_id'],db=db)


def get_page(page_idx:int=Query(default=1,description='页数'),page_size:int=Query(default=10,description='每页数量'))->dict:
    """获取分页数据
    """
    return dict(page_idx=page_idx,page_size=page_size)