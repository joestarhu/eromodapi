from fastapi import APIRouter,Depends,Query
from eromodapi.schema.account import account_api,AccountCreate,AccountUpdate,AccountDelete,AccountList #noqa
from eromodapi.api.base import get_user,get_page #noqa

api = APIRouter(prefix='/account')


@api.get('/list',summary='获取账号列表数据')
def get_list(*,user=Depends(get_user),page=Depends(get_page),nick_name:str=Query(default=None,description='用户昵称'),phone:str=Query(default=None,description='手机号'),status:int=Query(default=None,description='用户状态')):
    data = AccountList(nick_name=nick_name,phone=phone,status=status,**page)
    return account_api.get_list(user['db'],data)


@api.get('/detail',summary='获取账号详情')
def get_list(*,user=Depends(get_user),id:int):
    return account_api.get_detail(user['db'],id)


@api.post('/create',summary='新增账号')
def create(*,user=Depends(get_user),data:AccountCreate):
    return account_api.create(user['db'],user['act_info'],data)


@api.post('/update',summary='修改账号')
def update(*,user=Depends(get_user),data:AccountUpdate):
    return account_api.update(user['db'],user['act_info'],data)


@api.post('/delete',summary='删除账号')
def delete(*,user=Depends(get_user),data:AccountDelete):
    return account_api.delete(user['db'],user['act_info'],data)
