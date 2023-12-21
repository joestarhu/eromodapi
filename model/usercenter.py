from sqlalchemy import String,Integer,BigInteger,Boolean,UniqueConstraint,ForeignKey
from sqlalchemy.orm import mapped_column as mc, Mapped as M
from eromodapi.model.base import ModelBase #noqa


class User(ModelBase):
    __tablename__ = 't_user'
    __table_args__ = (
        {'comment': '用户信息'}
    )

    acct:M[str] = mc(String(64),unique=True,nullable=True,comment='用户账户,唯一')
    phone:M[str] = mc(String(16), unique=True,nullable=True,comment='手机号,唯一')
    nick_name:M[str] = mc(String(64),default='',comment='用户昵称')
    real_name:M[str] = mc(String(64),default='',comment='用户实名')
    status:M[int] = mc(Integer, default=1, comment='用户状态 0:停用,1:启用')
    avatar:M[str] = mc(String(1024), default='', comment='用户头像url地址')
    deleted:M[bool] = mc(Boolean, default=False, comment='逻辑数据删除标志,逻辑删除时,将账号和手机号置为null')

class UserAuth(ModelBase):
    __tablename__ = 't_user_auth'
    __table_args__ = (
        UniqueConstraint('user_id', 'type', 'appid', name='uni_user_auth'),
        {'comment': '用户鉴权信息'}
    )

    user_id:M[int] = mc(ForeignKey("t_user.id", ondelete='cascade'), comment='用户ID')
    type:M[int] =mc(Integer,default=0,comment='鉴权类型,如密码,微信,钉钉等')
    appid:M[str] = mc(String(256),default='',comment='鉴权类型的appid,比如微信的小程序ID,钉钉的H5应用ID')
    value:M[str] = mc(String(256),default='',comment='鉴权值,比如密码或其他身份标识')

class Org(ModelBase):
    __tablename__ = 't_org'
    __table_args__ = (
        UniqueConstraint('name', 'parent',  name='uni_org'),
        {'comment': '组织信息'}
    )

    name:M[str] = mc(String(64),default='',comment='组织名')
    parent:M[int] = mc(BigInteger,nullable=True,comment='所属父节点')
    remark:M[str] = mc(String(512),default='',comment='备注信息')
    deleted:M[bool] = mc(Boolean, default=False, comment='逻辑数据删除标志')

class OrgUser(ModelBase):
    __tablename__ = 't_org_user'
    __table_args__ = (
        UniqueConstraint('user_id', 'org_id',  name='uni_org_user'),
        {'comment': '组织用户信息'}
    )

    org_id:M[int] = mc(ForeignKey("t_org.id", ondelete='cascade'), comment='组织ID')
    user_id:M[int] = mc(ForeignKey("t_user.id", ondelete='cascade'), comment='用户ID')


class Role(ModelBase):
    __tablename__ = 't_role'
    __table_args__ = (
        UniqueConstraint('name', 'org_id',  name='uni_role'),
        {'comment': '角色信息'}
    )

    name:M[str] = mc(String(64),default='',comment='角色名')
    org_id:M[int] = mc(ForeignKey("t_org.id", ondelete='cascade'), comment='组织ID')
    remark:M[str] = mc(String(512),default='',comment='备注信息')
    status:M[int] = mc(Integer, default=1, comment='角色状态 0:停用,1:启用') 


class RoleUser(ModelBase):
    __tablename__ = 't_role_user'
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id',  name='uni_role_user'),
        {'comment': '角色用户信息'}
    )    

    role_id:M[int] = mc(ForeignKey("t_role.id", ondelete='cascade'), comment='角色ID')
    user_id:M[int] = mc(ForeignKey("t_user.id", ondelete='cascade'), comment='用户ID')