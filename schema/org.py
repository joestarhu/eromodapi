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
    root_id:int|None=None

class OrgDelete(BaseModel):
    id:int

# class OrgInfo(BaseModel):
#     name:str
#     remark:str = ''


class OrgAPI():
    def get_root_list(self,db:Session,data:OrgList)->Rsp:
        """获取根组织信息
        """
        stmt = select(Org.id,Org.name,Org.remark,Org.u_dt,User.nick_name.label('u_nick_name')).join_from(Org,User,and_(
            Org.u_id == User.id,Org.deleted == False, Org.root_id == None
        ))

        if data.name != '':
            stmt = stmt.where(Org.name.contains(data.name))

        data = ORM.pagination(db,stmt,page_idx=data.page_idx,page_size=data.page_size,order=[Org.u_dt.desc()])
        return Rsp(data=data)

    def create_org(self,db:Session,c_id:int,data:OrgCreate)->Rsp:
        """创建组织
        """
        # Unique Check
        stmt = select(Org.id).where(and_(Org.deleted==False, Org.name==data.name, Org.root_id==data.root_id))
        if ORM.counts(db,stmt) > 0:
            return Rsp(code=1,message='已经存在同名组织或部门')

        # 根组织
        insert_info = ORM.insert_info(c_id)
        org = Org(**data.model_dump(),**insert_info)

        try:
            db.add(org)
            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(data=f'{e}')

        return Rsp()
    
    def get_org_detail(self,db:Session,id:int)->Rsp:
        """获取详情
        """
        stmt = select(Org.id,Org.name,Org.remark,Org.root_id).where(and_(Org.deleted == False,Org.id == id))
        result = ORM.one(db,stmt)
        return Rsp(data=result)

    def delete_org(self,db:Session,c_id:int,data:OrgDelete)->Rsp:
        """删除组织(仅作逻辑删除)
        """

        if data.id == 1:
            return Rsp(code=1,message='系统初始组织不可操作')

        update_info = ORM.update_info(c_id)
        stmt = update(Org).where(Org.id == data.id).values(deleted=True,**update_info)
        try:
            db.execute(stmt)
            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(data=f'{e}')
        
        return Rsp()


org_api = OrgAPI()