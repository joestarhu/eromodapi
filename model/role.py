from sqlalchemy import String,Integer,UniqueConstraint,ForeignKey,Boolean
from sqlalchemy.orm import mapped_column as mc, Mapped as M
from eromodapi.model.base import ModelBase #noqa

class RoleSettings:
    # 角色状态
    status_disbale:int=0
    status_enable:int=1

    # 角色用户状态
    user_status_disable:int = 0
    user_status_enable:int = 1


class Role(ModelBase):
    __tablename__ = 't_role'
    __table_args__ = (
        UniqueConstraint('name','org_id',name='uni_role'),
        {'comment': '角色信息'}
    )

    org_id:M[int] = mc(ForeignKey('t_org.id',ondelete='restrict'),comment='角色所属组织ID')
    name:M[str] = mc(String(64),default='',comment='角色名')
    remark:M[str] = mc(String(512),default='',comment='备注信息')
    status:M[int] = mc(Integer, default=RoleSettings.status_enable, comment='角色状态 0:停用,1:启用') 
    admin_flg:M[bool] = mc(Boolean,default=False,comment='是否管理员角色,管理员角色无数据权限和功能权限的限制')


class RoleUser(ModelBase):
    __tablename__ = 't_role_user'
    __table_args__ =  (
        UniqueConstraint('role_id','user_id',name='uni_role_user'),
        {'comment':'角色用户信息'}
    )

    role_id:M[int] = mc(ForeignKey("t_role.id", ondelete='cascade'), comment='角色ID')
    user_id:M[int] = mc(ForeignKey("t_user.id", ondelete='cascade'), comment='用户ID')
    user_status:M[int] = mc(Integer, default=RoleSettings.user_status_enable, comment='角色用户状态 0:停用,1:启用')

