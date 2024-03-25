from fastapi import APIRouter,Depends
from eromodapi.schema.auth import auth_api, PasswordLogin,SelectOrg #noqa
from eromodapi.api.base import get_db,oauth2_schema #noqa

api = APIRouter(prefix='/auth')

@api.post('/login',summary='账密登录')
def login(*,db=Depends(get_db),data:PasswordLogin):
    return auth_api.password_login(db=db,data=data)

@api.post('/select_org',summary='选择组织')
def select_org(*,token=Depends(oauth2_schema),data:SelectOrg):
    payload = auth_api.jwt_decode(token)
    return auth_api.select_org(payload=payload,data=data)

