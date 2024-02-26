from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel,Field
from sqlalchemy import select,update,delete,and_,or_,alias
from sqlalchemy.orm.session import Session
from eromodapi.model.user import User #noqa
from eromodapi.model.org import Org,OrgSettings #noqa
from eromodapi.schema.base import ORM,Rsp,RspError,Pagination #noqa


class OrgCreate(BaseModel):
    name:str = Field(description='组织名称')
    owner_id:int = Field(description='组织拥有者用户ID')
    status:int = Field(default=OrgSettings.status_enable,description='组织状态')
    remark:str = Field(default='',description='组织备注信息')


class OrgUpdate(BaseModel):
    id:int
    name:str
    owner_id:int
    status:int
    remark:str


class OrgDelete(BaseModel):
    id:int


class OrgList(Pagination):
    name:str = ''
    status:int|None = None


class OrgAPI():
    def chk_org_unique(self,db:Session,name:str,except_id:int=None)->Rsp|None:
        """判断组织是否重复
        """

        if except_id:
            expression = Org.id != except_id
        else:
            expression = None

        rules = [
            ('组织名称已被使用',and_(Org.name == name,Org.deleted == False))
        ]

        return ORM.unique_chk(db,rules,expression)

    def create_org(self,db:Session,crt_id:int,data:OrgCreate)->Rsp:
        """创建组织
        """

        if rsp := self.chk_org_unique(db,data.name):
            return rsp

        insert_info = ORM.insert_info(crt_id)
        org = Org(**data.model_dump(),**insert_info)

        try:
            db.add(org)
            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(data=f'{e}')

        return Rsp()
    
    def update_org(self,db:Session,crt_id:int,data:OrgUpdate)->Rsp:
        """更新组织
        """
        if data.id == 1:
            return Rsp(code=1,message='系统初始组织不可操作')
        
        condtion = and_(Org.id == data.id, Org.deleted == False)
        stmt = select(Org.id).where(condtion)
        if ORM.counts(db,stmt) == 0:
            return Rsp(code=1,message='不存在该组织')

        if rsp := self.chk_org_unique(db,name=data.name,except_id=data.id):
            return rsp

        update_info = ORM.update_info(crt_id)
        stmt = update(Org).where(condtion).values(**data.model_dump(exclude_unset=True),**update_info)
        ORM.commit(db,stmt)
        return Rsp()

    def delete_org(self,db:Session,crt_id:int,data:OrgDelete)->Rsp:
        """删除组织(仅做逻辑删除)
        """

        if data.id == 1:
            return Rsp(code=1,message='系统初始组织不可操作')

        update_info = ORM.update_info(crt_id)
        stmt = update(Org).where(Org.id == data.id).values(name=str(uuid4()),deleted=True,**update_info)
        ORM.commit(db,stmt)
        
        return Rsp()

    def get_list(self,db:Session,data:OrgList)->Rsp:
        """获取组织列表
        """
        owner_user = alias(User)

        stmt = select(
            Org.id,Org.name,Org.remark,Org.status,Org.upd_dt,
            owner_user.c.nick_name.label('owner_name'),
            User.nick_name.label('upd_nick_name')
        ).join_from(Org,User,and_(Org.upd_id == User.id,Org.deleted == False)
        ).join(
            owner_user,Org.owner_id == owner_user.c.id
        )

        if data.status != None:
            stmt = stmt.where(Org.status == data.status)

        if data.name != '':
            stmt = stmt.where(Org.name.contains(data.name))

        data = ORM.pagination(db,stmt,data.page_idx,data.page_size,[Org.upd_dt.desc()])
        return Rsp(data=data)

    def get_org_detail(self,db:Session,id:int)->Rsp:
        """获取详情
        """
        stmt = select(Org.id,Org.owner_id,Org.name,Org.status,Org.remark).where(and_(Org.deleted == False,Org.id == id))
        result = ORM.one(db,stmt)
        return Rsp(data=result)

org_api = OrgAPI()