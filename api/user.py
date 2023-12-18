from fastapi import APIRouter,Depends
from eromodapi.schema.user import user_api,UserCreate,UserList,PasswordLogin #noqa
from eromodapi.api.base import get_db,get_user #noqa


api = APIRouter(prefix='/user')


@api.post('/login',summary='用户密码登录')
def login(*,db=Depends(get_db),data:PasswordLogin):
    return user_api.password_login(db,data)

@api.post('/create',summary='新增用户')
def create(*,user=Depends(get_user),data:UserCreate):
    return user_api.create_user(user['db'],user['id'],data)

@api.get('/list',summary='获取用户列表数据')
def get_list(*,user=Depends(get_user),page_idx:int=1,page_size:int=10,nick_name:str=None,phone:str=None,status:int=None):
    data = UserList(page_idx=page_idx,page_size=page_size,nick_name=nick_name,phone=phone,status=status)
    return user_api.get_user_list(user['db'],data)

@api.get('/detail',summary='获取用户详情')
def get_list(*,user=Depends(get_user),id:int):
    return user_api.get_user_detail(user['db'],id)
