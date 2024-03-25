from typing import Generator
from fastapi import Depends,Query
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from eromodapi.schema.user import user_api #noqa
from eromodapi.model.base import SessionLocal #noqa

def get_db()->Generator:
    """获取关系型数据库会话
    """
    with SessionLocal() as session:
        yield session


oauth2_schema=OAuth2PasswordBearer(tokenUrl='/user/login')
def get_user(token=Depends(oauth2_schema),db=Depends(get_db))->dict:
    """获取已登录的用户信息
    """
    user = user_api.jwt_decode(db,token)
    return dict(db=db,**user)


def get_page(page_idx:int=Query(default=1,description='页数'),page_size:int=Query(default=10,description='每页数量'))->dict:
    """获取分页数据
    """
    return dict(page_idx=page_idx,page_size=page_size)


def access_chk(user:dict,services:str)->None:
    """判断用户是否具备访问权限
    """
    pass
    # if not user['roles']:
    #     raise HTTPException(403,detail='用户无权访问')


