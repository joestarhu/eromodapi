from fastapi import APIRouter,Depends,Query
from eromodapi.api.base import get_user,get_page #noqa
from eromodapi.schema.org import org_api,OrgList,OrgCreate,OrgUpdate,OrgDelete #noqa


api = APIRouter(prefix='/org')

@api.post('/create',summary='创建组织')
def create_org(*,user=Depends(get_user),data:OrgCreate):
    root = OrgCreate(**data.model_dump())
    return org_api.create(user['db'],user['act'],root)

@api.post('/update',summary='更新组织')
def update_org(*,user=Depends(get_user),data:OrgUpdate):
    return org_api.update(user['db'],user['act'],data)

@api.post('/delete',summary='删除组织')
def delete_org(*,user=Depends(get_user),data:OrgDelete):
    return org_api.delete(user['db'],user['act'],data)

@api.get('/list',summary='获取组织列表信息')
def get_list(*,user=Depends(get_user),page=Depends(get_page),name:str=Query(default='',description='组织名称'),status:int=Query(default=None,description='组织状态')):
    data = OrgList(**page,name=name,status=status)
    return org_api.get_list(user['db'],data)

@api.get('/detail',summary='获取组织详情')
def get_detail(*,user=Depends(get_user),id:int):
    return org_api.get_detail(user['db'],id)
