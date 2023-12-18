from math import ceil
from typing import Any, Dict
from pydantic import BaseModel
from fastapi import HTTPException
from sqlalchemy import select,func
from sqlalchemy.orm.session import Session

class Rsp(BaseModel):
    """请求成功返回信息
    """
    code:int = 0
    message:str = '成功'
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
    page_idx:int = 1
    page_size:int = 10



class ORMBase:
    def orm_counts(self,db:Session,stmt) -> int:
        """根据执行的SQL语句,查询数量
        """
        total_stmt = select(func.count("1")).select_from(stmt.subquery())
        return db.scalar(total_stmt)
        
    def orm_one(self,db:Session,stmt)->dict:
        """获取第一行数据
        """
        data = db.execute(stmt).mappings().first()
        if data:
            data = dict(data)
        return data

    def orm_all(self,db:Session,stmt)->dict:
        """查询所有数据
        """
        result = db.execute(stmt).mappings()
        return [dict(**v) for v in result]
    
    def orm_pagination(self,db:Session,stmt,page_idx:int=1,page_size:int=10)->dict:
        """分页查询数据
        """
        # 至少查询1条数据
        if page_size < 1:
            page_size = 1

        # 分页ID必须从1开始
        match(page_idx):
            case page_idx if page_idx > 0:
                offset = (page_idx - 1) * page_size
            case _:
                offset = 0
                page_idx = 1
            
        # 获取总数据量以及总页数
        total = self.orm_counts(db,stmt)
        page_total = ceil(total/page_size)

        pagination = dict(page_idx=page_idx, page_size=page_size,
                        page_total=page_total, total=total)

        # 获取分页数据
        stmt = stmt.offset(offset).limit(page_size)
        records = self.orm_all(db, stmt)

        return dict(records=records, pagination=pagination)
    