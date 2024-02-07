from fastapi import APIRouter,Depends,Query
from eromodapi.schema.role import role_api,RoleCreate,RoleList,RoleUserList  #noqa
from eromodapi.api.base import get_user,get_page,get_db #noqa

api = APIRouter(prefix='/role')

@api.get('/list',summary='获取角色列表数据')
def get_list(*,user=Depends(get_user),page=Depends(get_page),name:str=Query(default='',description='角色名'),org_id:int=Query(default=None,description='组织ID'),status:int=Query(default=None,description='角色状态')):
    data = RoleList(**page,name=name,status=status,org_id=org_id)
    return role_api.get_list(user['db'],data)

@api.get('/user',summary='获取角色用户信息')
# def get_users(*,user=Depends(get_user),page=Depends(get_page),role_id:int=Query(description='角色ID')):
def get_users(*,db=Depends(get_db),page=Depends(get_page),role_id:int=Query(description='角色ID')):
    data = RoleUserList(**page,role_id=role_id)
    return role_api.get_user_list(db,data)
    return role_api.get_user_list(user['db'],data)