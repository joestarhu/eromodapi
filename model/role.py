from sqlalchemy import String,Integer,UniqueConstraint,BigInteger,Boolean
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

    org_id:M[int] = mc(BigInteger,comment='组织ID,与t_org.id一致')
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

    role_id:M[int] = mc(BigInteger,comment='角色ID,与t_role.id一致')
    user_id:M[int] = mc(BigInteger,comment='用户账户ID,与t_user.id一致')
    user_status:M[int] = mc(Integer, default=RoleSettings.user_status_enable, comment='角色用户状态 0:停用,1:启用')

