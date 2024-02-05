from fastapi import APIRouter,Depends,Query
from eromodapi.api.base import get_user,get_page #noqa
from eromodapi.schema.org import org_api,OrgList,OrgCreate,OrgUpdate,OrgDelete #noqa


api = APIRouter(prefix='/org')


# @api.get('/all',summary='获取组织信息')
# def get_all(*,user=Depends(get_user)):
#     data = OrgList(page_size=0)
#     return org_api.get_root(user['db'],data)


@api.post('/create',summary='创建组织')
def create_org(*,user=Depends(get_user),data:OrgCreate):
    root = OrgCreate(**data.model_dump())
    return org_api.create_org(user['db'],user['id'],root)

@api.post('/update',summary='更新组织')
def update_org(*,user=Depends(get_user),data:OrgUpdate):
    return org_api.update_org(user['db'],user['id'],data)

@api.post('/delete',summary='删除组织')
def delete_org(*,user=Depends(get_user),data:OrgDelete):
    return org_api.delete_org(user['db'],user['id'],data)

# @api.post('/delete',summary='删除组织部门')
# def create_org(*,user=Depends(get_user),data:OrgDelete):
#     return org_api.delete_org(user['db'],user['id'],data)

@api.get('/list',summary='获取组织列表信息')
def get_list(*,user=Depends(get_user),page=Depends(get_page),name:str=Query(default='',description='组织名称')):
    data = OrgList(**page,name=name)
    return org_api.get_list(user['db'],data)

@api.get('/detail',summary='获取组织或部门详情')
def get_detail(*,user=Depends(get_user),id:int):
    return org_api.get_org_detail(user['db'],id)

# @api.get('/children',summary='获取子部门信息')
# def get_children(*,user=Depends(get_user),id:int):
#     return org_api.get_org_children(user['db'],id)