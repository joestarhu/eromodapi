from datetime import datetime
from math import ceil
from typing import Any, Dict,List
from pydantic import BaseModel,Field
from fastapi import HTTPException
from sqlalchemy import select,func,Select
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.orm.session import Session

class Rsp(BaseModel):
    """请求成功返回信息
    """
    code:int = Field(default=0,description='请求结果代码;0表示成功')
    message:str = Field(default='成功',description='请求结果消息描述')
    data:Any = None


class RspError(HTTPException):
    """请求失败返回信息
    """
    def __init__(self,code:int=500,message:str='服务器内部错误,请重试或联系管理员',data:Any=None,headers:Dict[str,str] | None = None) -> None:
        rsp = Rsp(code=code,message=message,data=data)
        super().__init__(code, rsp.model_dump(), headers)


class Pagination(BaseModel):
    """分页请求参数
    """
    page_idx:int = Field(default=1,description='页数ID')
    page_size:int = Field(default=10,description='每页数量')


def orm_wrapper(func):
    def wrapper(*args,**kw):
        try:
            return func(*args,**kw)
        except RspError as e:
            raise e
        except Exception as e:
            raise RspError(data=f'{e}')

    return wrapper  


class ORM:
    @staticmethod
    def commit(db:Session,stmt):
        try:
            db.execute(stmt)
            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(data=f'{e}')

    @staticmethod
    def insert_info(id:int)->dict:
        """构建数据新增信息
        """
        now =datetime.now()
        return dict(crt_id=id,upd_id=id,crt_dt=now,upd_dt=now)

    @staticmethod
    def update_info(id:int)->dict:
        """构建数据更新信息
        """
        now =datetime.now()
        return dict(upd_id=id,upd_dt=now)


    @orm_wrapper
    @staticmethod
    def unique_chk(db:Session,rules:list,except_expression:BinaryExpression=None)->Rsp|None:
        base_stmt = select(1)

        if except_expression:
            base_stmt = base_stmt.where(except_expression)

        for errmsg, condition in rules:
            stmt = base_stmt.where(condition)
            if ORM.counts(db,stmt) > 0 :
                return Rsp(code=1,message=errmsg)

    @orm_wrapper
    @staticmethod
    def all(db:Session,stmt:Select)->List[dict]:
        """获取所有数据
        """
        ds = db.execute(stmt).mappings()
        return [dict(**data) for data in ds]

    @orm_wrapper
    @staticmethod
    def one(db:Session,stmt:Select)->dict|None:
        """获取第一行数据
        """
        ds = ORM.all(db,stmt)
        return ds[0] if ds else None

    @orm_wrapper
    @staticmethod
    def counts(db:Session,stmt:Select)->int:
        """获取数据量
        """
        return db.scalar(stmt.with_only_columns(func.count('1')))

    @orm_wrapper
    @staticmethod
    def pagination(db:Session,stmt:Select,page_idx:int=1,page_size:int=10,order:list=None)->dict:
        """分页查询数据
        """
        if page_size < 1:
            page_size = 1

        match(page_idx):
            case page_idx if page_idx > 0:
                offset = (page_idx - 1) * page_size
            case _:
                offset = 0
                page_idx = 1

        total = ORM.counts(db,stmt)
        page_total = ceil(total / page_size)

        pagination = dict(page_idx=page_idx, page_size=page_size,page_total=page_total,total=total)

        # 配置排序条件
        if order:
            stmt = stmt.order_by(*order)

        # 配置分页条件
        stmt = stmt.offset(offset).limit(page_size)
        records = ORM.all(db,stmt)
        data=dict(records=records, pagination=pagination)
    
        return data