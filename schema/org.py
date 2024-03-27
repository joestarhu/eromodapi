from uuid import uuid4
from pydantic import BaseModel,Field
from sqlalchemy import select,update,and_,alias
from sqlalchemy.orm.session import Session
from eromodapi.model.user import User #noqa
from eromodapi.model.org import Org,OrgUser,OrgSettings #noqa
from eromodapi.model.role import Role,RoleUser #noqa
from eromodapi.schema.base import ORM,Rsp,RspError,Pagination,ActInfo #noqa


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


class OrgAPI:
    def chk_unique(self,db:Session,name:str,except_id:int=None)->Rsp|None:
        """唯一性判断
        """
        if except_id is None:
            expression = None
        else:
            expression = Org.id != except_id

        rules = [
            ('组织名称已被使用',and_(Org.name==name,Org.deleted == False)),
        ]

        return ORM.unique_chk(db,rules,expression)
    
    def create(self,db:Session,act:ActInfo,data:OrgCreate)->Rsp:
        """新增组织
        """
        if rsp := self.chk_unique(db,name=data.name):
            return rsp
        
        insert_info = ORM.insert_info(act.user_id)
        org = Org(**data.model_dump(),**insert_info)        

        try:
            db.add(org)
            db.flush()

            # 为组织初始化超级管理员角色
            r = Role(name='超级管理员',remark='组织初始化角色',org_id=org.id,admin_flg=True,**insert_info)
            db.add(r)
            db.flush()

            # 将管理员加入组织
            ou = OrgUser(org_id=org.id,user_id = data.owner_id,**insert_info)
            db.add(ou)

            # 为组织初始化的管理者追加超级管理员角色
            ru = RoleUser(role_id = r.id, user_id = data.owner_id,**insert_info)
            db.add(ru)
            db.commit()

        except Exception as e:
            db.rollback()
            raise RspError(data=f'{e}')

        return Rsp()

    def update(self,db:Session,act:ActInfo,data:OrgUpdate)->Rsp:
        """修改组织
        """
        if data.id == 1:
            return Rsp(code=1,message='系统初始组织不可操作')
        
        if rsp := self.chk_unique(db,name=data.name,except_id=data.id):
            return rsp
        
        update_info = ORM.update_info(act.user_id)
        stmt = update(Org).where(
            Org.id == data.id
        ).values(
            **data.model_dump(exclude_unset=True),**update_info
        )
        ORM.commit(db,stmt)

        return Rsp()
    
    def delete(self,db:Session,act:ActInfo,data:OrgDelete)->Rsp:
        """删除组织(仅做逻辑删除)
        """
        if data.id == 1:
            return Rsp(code=1,message='系统初始组织不可操作')

        update_info = ORM.update_info(act.user_id)
        stmt = update(Org).where(Org.id == data.id).values(name=str(uuid4()),deleted=True,**update_info)
        ORM.commit(db,stmt)
        
        return Rsp()

    def get_list(self,db:Session,data:OrgList):
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

        if data.status is not None:
            stmt = stmt.where(Org.status == data.status)

        if data.name != '':
            stmt = stmt.where(Org.name.contains(data.name))

        data = ORM.pagination(db,stmt,data.page_idx,data.page_size,[Org.upd_dt.desc()])
        return Rsp(data=data)

    def get_detail(self,db:Session,id:int):
        """获取组织详情
        """
        stmt = select(
            Org.id,Org.owner_id,Org.name,Org.status,Org.remark,
            User.phone,User.nick_name.label('owner_name')
        ).join_from(Org,User,and_(Org.deleted == False, Org.owner_id == User.id)
                    ).where(
                        Org.id == id
                    )
        # stmt = select(Org.id,Org.owner_id,Org.name,Org.status,Org.remark).where(and_(Org.deleted == False,Org.id == id))
        result = ORM.one(db,stmt)
        return Rsp(data=result)


org_api = OrgAPI()
