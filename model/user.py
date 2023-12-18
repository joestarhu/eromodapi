from sqlalchemy import String,Integer,Boolean,UniqueConstraint,ForeignKey
from sqlalchemy.orm import mapped_column as mc, Mapped as M
from eromodapi.model.base import ModelBase #noqa


class User(ModelBase):
    __tablename__ = 't_user'
    __table_args__ = (
        {'comment': '用户信息'}
    )

    acct:M[str] = mc(String(64),default='',comment='用户账户,唯一')
    nick_name:M[str] = mc(String(64),default='',comment='用户昵称')
    real_name:M[str] = mc(String(64),default='',comment='用户实名')
    phone:M[str] = mc(String(16), default='',comment='手机号,唯一')
    status:M[int] = mc(Integer, default=1, comment='用户状态 0:停用,1:启用')
    avatar:M[str] = mc(String(1024), default='', comment='用户头像url地址')
    deleted:M[bool] = mc(Boolean, default=False, comment='逻辑数据删除标志')


class UserAuth(ModelBase):
    __tablename__ = 't_user_auth'
    __table_args__ = (
        UniqueConstraint('user_id', 'type', 'appid', name='uni_user_auth'),
        {'comment': '用户鉴权信息'}
    )

    # 外键约束
    user_id:M[int] = mc(ForeignKey("t_user.id", ondelete='cascade'), comment='用户ID')
    type:M[int] =mc(Integer,default=0,comment='鉴权类型,如密码,微信,钉钉等')
    appid:M[str] = mc(String(256),default='',comment='鉴权类型的appid,比如微信的小程序ID,钉钉的H5应用ID')
    value:M[str] = mc(String(256),default='',comment='鉴权值,比如密码或其他身份标识')
