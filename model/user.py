from sqlalchemy import String,Integer,Boolean,UniqueConstraint,ForeignKey
from sqlalchemy.orm import mapped_column as mc, Mapped as M
from eromodapi.model.base import ModelBase #noqa

class UserSettings:
    # 用户状态
    status_disbale:int=0
    status_enable:int=1 

    # 验证类型
    auth_password:int=0
    auth_dingtalk:int=1



class User(ModelBase):
    __tablename__ = 't_user'
    __table_args__ = (
        {'comment': '用户信息'}
    )

    acct:M[str] = mc(String(64),unique=True,nullable=True,comment='用户账户,唯一')
    phone:M[str] = mc(String(16), unique=True,nullable=True,comment='手机号,唯一')
    nick_name:M[str] = mc(String(64),default='',comment='用户昵称')
    real_name:M[str] = mc(String(64),default='',comment='用户实名')
    status:M[int] = mc(Integer, default=UserSettings.status_enable, comment='用户状态 0:停用,1:启用')
    avatar:M[str] = mc(String(1024), default='', comment='用户头像url地址')
    deleted:M[bool] = mc(Boolean, default=False, comment='逻辑数据删除标志,逻辑删除时,将账号和手机号置为null')

class UserAuth(ModelBase):
    __tablename__ = 't_user_auth'
    __table_args__ = (
        UniqueConstraint('user_id', 'type', 'appid', name='uni_user_auth'),
        {'comment': '用户鉴权信息'}
    )

    user_id:M[int] = mc(ForeignKey("t_user.id", ondelete='cascade'), comment='用户ID')
    type:M[int] = mc(Integer,default=UserSettings.auth_password,comment='鉴权类型, 0:密码,1:钉钉')
    appid:M[str] = mc(String(256),default='',comment='鉴权类型的appid,比如微信的小程序ID,钉钉的H5应用ID')
    value:M[str] = mc(String(256),default='',comment='鉴权值,比如密码或其他身份标识')
