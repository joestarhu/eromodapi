from sqlalchemy import String,Integer,BigInteger,Boolean,UniqueConstraint,ForeignKey,DateTime
from sqlalchemy.orm import mapped_column as mc, Mapped as M
from eromodapi.model.base import ModelBase #noqa

# class Service(ModelBase):
#     __tablename__ = 't_service'
#     __table_args__ = (
#         {'comment':'应用服务信息'}
#     )

#     name:M[str] = mc(String(64),comment='应用服务名称')
#     remark:M[str] = mc(String(512),comment='备注')

# class ServiceAuth(ModelBase):
#     __tablename__ = 't_service_auth'
#     __table_args__ = (
#         {'comment':'应用服务授权信息'}
#     )

#     service_id:M[int] = mc(ForeignKey('t_service.id',ondelete='cascade'),comment='应用服务ID')
#     auth_type:M[int] = mc(Integer,default=1,comment='授权类型;0:个人,1:组织')
#     auth_id:M[int] = mc(BigInteger,comment='授权对象ID')
#     auth_expire_time = mc(DateTime, comment='授权截止日期')

# class ServiceRole(ModelBase):
#     __tablename__ = 't_service_role'
#     __table_args__ = (
#         {'comment':'应用服务角色信息'}
#     )

#     service_id:M[int] = mc(ForeignKey('t_service.id',ondelete='cascade'),comment='应用服务ID')
#     role_id:M[int] = mc(ForeignKey('t_role.id',ondelete='cascade'),comment='角色ID')
#     data_scope:M[int] = mc(Integer,default=0,comment='数据权限;0:本人,1:本部门,2:本部门及以下,3:本组织')
