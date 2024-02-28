from sqlalchemy import String,Integer,Boolean,ForeignKey,UniqueConstraint
from sqlalchemy.orm import mapped_column as mc, Mapped as M
from eromodapi.model.base import ModelBase #noqa



class App(ModelBase):
    __tablename__ = 't_app'
    __table_args__ = (
        {'comment':'应用信息'}
    )

    name:M[str] = mc(String(64),comment='应用名')
    remark:M[str] = mc(String(512),default='',comment='备注信息')


class AppService(ModelBase):
    __tablename__ = 't_app_service'
    __table_args__ = (
        UniqueConstraint('app_id','name',name='uni_app_service'),
        {'comment':'应用服务'}
    )

    app_id:M[int] = mc(ForeignKey("t_app.id", ondelete='cascade'), comment='所属应用ID')
    name:M[str] = mc(String(64),comment='应用服务标签')
    remark:M[str] = mc(String(512),default='',comment='备注信息')
