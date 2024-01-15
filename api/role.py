from fastapi import APIRouter,Depends
# from eromodapi.schema.role import role_api,RoleList #noqa
from eromodapi.api.base import get_user #noqa


api = APIRouter(prefix='/role')



# @api.get('/list',summary='获取角色列表数据')
# def get_list(*,user=Depends(get_user),page_idx:int=1,page_size:int=10,name:str=None,org_id:int=None):
#     data = RoleList(page_idx=page_idx,page_size=page_size,name=name,org_id=org_id)
#     return role_api.get_list(user['db'],data)

# @api.get('/detail',summary='获取角色详情')
# def get_detail(*,user=Depends(get_user),id:int):
#     pass
