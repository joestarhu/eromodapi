from fastapi import APIRouter,Depends
from eromodapi.schema.user import user_api,UserCreate,UserList,PasswordLogin #noqa
from eromodapi.api.base import get_db #noqa


api = APIRouter(prefix='/user')


@api.post('/login',summary='用户密码登录')
def login(*,db=Depends(get_db),data:PasswordLogin):
    return user_api.password_login(db,data)

@api.post('/create',summary='新增用户')
def create(data:UserCreate):
    pass


@api.get('/list',summary='获取用户列表数据')
def get_list():
    pass    
