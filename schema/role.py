from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import select,update,delete,and_,alias
from sqlalchemy.orm.session import Session
# from eromodapi.config.settings import settings,hash_api,jwt_api,AuthType,UserStatus #noqa
from eromodapi.model.usercenter import User,UserAuth,Role,UserRole,Org #noqa
from eromodapi.schema.base import ORM,ORMBase,Rsp,RspError,Pagination #noqa


class RoleList(Pagination):
    name:str | None = None
    org_id:int | None =None


# class RoleAPI(ORMBase):
#     def get_list(self,db:Session,data:RoleList) -> Rsp:
#         """获取角色列表
#         """
#         stmt = select(Role.id,Role.name,Role.status,Role.type,Role.remark,Role.u_dt,User.nick_name.label('u_nick_name'),Org.name.label('org_name')).join(
#             User,Role.u_id == User.id,isouter=True
#         ).join(
#             Org, Role.org_id == Org.id, isouter=True
#         )

#         if data.name:
#             stmt = stmt.where(Role.name.contains(data.name))

#         if data.org_id != None:
#             stmt = stmt.where(Role.org_id == data.org_id)

#         data = self.orm_pagination(db,stmt,page_idx=data.page_idx,page_size=data.page_size)
#         return Rsp(data=data)

# role_api = RoleAPI()
