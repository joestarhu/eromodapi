from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import select,update,delete,and_,or_,alias
from sqlalchemy.orm.session import Session
# from eromodapi.config.settings import settings,hash_api,jwt_api,AuthType,UserStatus #noqa
from eromodapi.model.usercenter import User,Org #noqa
from eromodapi.schema.base import ORM,Rsp,RspError,Pagination #noqa


class OrgList(Pagination):
    name:str = ''


class OrgRootCreate(BaseModel):
    name:str
    remark:str=''

class OrgCreate(OrgRootCreate):
    parent_id:int|None=None

# class OrgDelete(BaseModel):
#     id:int

# class OrgInfo(BaseModel):
#     name:str
#     remark:str = ''


class OrgAPI():
    def get_root_list(self,db:Session,data:OrgList)->Rsp:
        """获取根组织信息
        """
        stmt = select(Org.id,Org.name,Org.remark,Org.u_dt,User.nick_name.label('u_nick_name')).join_from(Org,User,and_(
            Org.u_id == User.id,Org.deleted == False, Org.parent_id == None
        ))

        if data.name != '':
            stmt = stmt.where(Org.name.contains(data.name))

        data = ORM.pagination(db,stmt,page_idx=data.page_idx,page_size=data.page_size,order=[Org.u_dt.desc()])
        return Rsp(data=data)

    def create_org(self,db:Session,c_id:int,data:OrgCreate)->Rsp:
        """创建组织
        """
        # Unique Check
        stmt = select(Org.id).where(and_(Org.deleted==False, Org.name==data.name, Org.parent_id==data.parent_id))
        if ORM.counts(db,stmt) > 0:
            return Rsp(code=1,message='已经存在同名组织或部门')

        # 根组织
        org = Org(**data.model_dump(),c_id=c_id,u_id=c_id)

        try:
            db.add(org)
            if data.parent_id != None:
                # Graph Build Relation
                ...
            
            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(data=f'{e}')

        return Rsp()
    

    def get_org_detail(self,db:Session,id:int):
        """获取详情
        """
        stmt = select(Org.id,Org.name,Org.remark,Org.parent_id).where(and_(Org.deleted == False,Org.id == id))
        result = ORM.one(db,stmt)
        return Rsp(data=result)


org_api = OrgAPI()