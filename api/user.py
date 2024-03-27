from fastapi import APIRouter,Depends,Query
# from eromodapi.schema.user import user_api,UserCreate,UserUpdate,UserDelete,UserList,PasswordLogin,SelectOrg #noqa
from eromodapi.api.base import get_db,get_user,get_page,access_chk #noqa

api = APIRouter(prefix='/user')


class UserServices:
    """用户功能权限
    """
    create:str = 'user_create'
    update:str = 'user_update'
    delete:str = 'user_delete'
    lists:str = 'user_list'
    detail:str = 'user_detail'


# @api.get('/login_user',summary='获取登录用户信息')
# def get_login_user(*,user=Depends(get_user)):
#     return user_api.get_user_detail(user['db'],user['id'])