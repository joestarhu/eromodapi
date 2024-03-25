from fastapi import APIRouter,Depends,Query
from eromodapi.schema.user import user_api,UserCreate,UserUpdate,UserDelete,UserList,PasswordLogin,SelectOrg #noqa
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


@api.post('/create',summary='新增用户')
def create(*,user=Depends(get_user),data:UserCreate):
    access_chk(user,UserServices.create)
    return user_api.create_user(user['db'],user['id'],data)


@api.post('/update',summary='修改用户')
def update(*,user=Depends(get_user),data:UserUpdate):
    access_chk(user,UserServices.update)
    return user_api.update_user(user['db'],user['id'],data)


@api.post('/delete',summary='删除用户')
def delete(*,user=Depends(get_user),data:UserDelete):
    access_chk(user,UserServices.delete)
    return user_api.delete_user(user['db'],user['id'],data)

@api.get('/login_user',summary='获取登录用户信息')
def get_login_user(*,user=Depends(get_user)):
    return user_api.get_user_detail(user['db'],user['id'])