from sqlalchemy import String,Integer,Boolean,BigInteger,UniqueConstraint
from sqlalchemy.orm import mapped_column as mc, Mapped as M
from eromodapi.model.base import ModelBase #noqa

class OrgSettings:
    # 组织状态
    status_disbale:int=0
    status_enable:int=1 

    user_status_disable:int = 0
    user_status_enable:int = 1



class Org(ModelBase):
    __tablename__ = 't_org'
    __table_args__ = (
        {'comment': '组织信息'}
    )

    owner_id:M[int] = mc(BigInteger,comment='组织拥有者ID,与t_user.id一致')
    name:M[str] = mc(String(64),unique=True,comment='组织名')
    remark:M[str] = mc(String(512),default='',comment='备注信息')
    status:M[int] = mc(Integer,default=OrgSettings.status_enable,comment='组织状态 0:停用,1:启用')
    deleted:M[bool] = mc(Boolean, default=False, comment='逻辑数据删除标志')


class OrgUser(ModelBase):
    __tablename__ = 't_org_user'
    __table_args__ = (
        UniqueConstraint('org_id','user_id',name='uni_org_user'),
        {'comment':'组织用户信息'}
    )

    org_id:M[int] = mc(BigInteger,comment='组织ID,与t_org.id一致')
    user_id:M[int] = mc(BigInteger,comment='用户账户ID,与t_user.id一致')
    status:M[int] = mc(Integer,default=OrgSettings.user_status_enable,comment='组织用户状态 0:停用,1:启用')

# class Dept(ModelBase):
#     __tablename__ = 't_dept'
#     __table_args__ = (
#         {'comment': '部门信息'}
#     )

#     name:M[str] = mc(String(64),comment='部门名')
#     org_id:M[int] = mc(ForeignKey("t_org.id", ondelete='restrict'), comment='所属组织ID')
#     remark:M[str] = mc(String(512),default='',comment='备注信息')