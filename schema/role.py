from pydantic import BaseModel
from sqlalchemy import select,update,delete,and_,alias
from sqlalchemy.orm.session import Session
from eromodapi.model.user import User #noqa
from eromodapi.model.org import Org #noaa
from eromodapi.model.role import Role,RoleUser,RoleSettings #noqa
from eromodapi.schema.base import ORM,Rsp,RspError,Pagination #noqa



class RoleCreate(BaseModel):
    name:str
    org_id:int
    status:int = RoleSettings.status_enable
    remark:str = ''

class RoleUserCreate(BaseModel):
    role_id:int
    user_id:int
    status:int = RoleSettings.user_status_enable


class RoleList(Pagination):
    name:str=''
    org_id:int|None = None
    status:int|None = None

class RoleUserList(Pagination):
    role_id:int


class RoleAPI:
    def chk_unique(self,db:Session,name:str,org_id:int,except_id:int=None)->Rsp|None:
        """判断角色是否唯一
        """

        if except_id:
            expression = Role.id == id
        else:
            expression = None

        rules = [
            ("角色名已被使用",and_(Role.name == name, Role.org_id == org_id))
        ]

        return ORM.unique_chk(db,rules,expression)
    
    def create_role(self,db:Session,crt_id:int,data:RoleCreate)->Rsp:
        """创建角色
        """

        if rsp := self.chk_unique(db,name=data.name,org_id=data.org_id):
            return rsp

        # 是否已存在角色
        create_info = ORM.insert_info(crt_id)
        role = RoleCreate(**data.model_dump(),**create_info)
        try:
            db.add(role)
            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(500,data=f'{e}')

        return Rsp()

    def get_list(self,db:Session,data:RoleList)->Rsp:
        """获取角色列信息
        """
        stmt = select(
            Role.id,Role.name,Role.status,Role.org_id,Role.remark,Role.upd_dt,
            User.nick_name.label('upd_nick_name'),
            User.real_name.label('upd_real_name'),
            Org.name.label('org_name'),
        ).join(User, Role.upd_id == User.id).join(Org, Role.org_id == Org.id)

        if data.name:
            stmt = stmt.where(Role.name.contains(data.name))
        
        if data.status != None:
            stmt = stmt.where(Role.status == data.status)

        result = ORM.pagination(db,stmt,page_idx=data.page_idx,page_size=data.page_size,order=[Role.crt_dt.desc()])

        return Rsp(data=result)
    
    def get_user_list(self,db:Session,data:RoleUserList)->Rsp:
        """获取角色用户列表信息
        """
        stmt = select(
            RoleUser.id,
            User.nick_name,
            User.real_name,
            User.phone).join_from(
                RoleUser,
                User,
                RoleUser.user_id == User.id,
                isouter=True).where(
                    RoleUser.role_id == data.role_id)
        
        result = ORM.pagination(db,stmt,page_idx=data.page_idx,page_size=data.page_size)

        return Rsp(data=result)

role_api = RoleAPI()
