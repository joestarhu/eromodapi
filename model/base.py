from datetime import datetime
from sqlalchemy import BigInteger,DateTime,create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker, mapped_column as mc, Mapped as M
from eromodapi.config.settings import settings #noqa

engine = create_engine(settings.config['mysql'],echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class ModelBase(DeclarativeBase):
    """通用Model字段
    """
    id:M[int] = mc(BigInteger,primary_key=True,autoincrement=True,comment='ID')
    c_id:M[int]=mc(BigInteger,nullable=True,comment='创建数据的用户ID')
    u_id:M[int]=mc(BigInteger,nullable=True,comment='更新数据的用户ID')
    c_dt:M[datetime] =mc(DateTime,default=datetime.now(),comment='创建数据的时间')
    u_dt:M[datetime] =mc(DateTime,default=datetime.now(),comment='修改数据的时间')
