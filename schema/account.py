from uuid import uuid4
from pydantic import BaseModel,Field
from sqlalchemy import select,update,delete,and_,alias
from sqlalchemy.orm.session import Session
from eromodapi.config.settings import settings,hash_api #noqa
from eromodapi.model.user import User,UserAuth,UserSettings #noqa
from eromodapi.schema.base import ORM,Rsp,RspError,Pagination,ActInfo #noqa


# 请求参数
class AccountCreate(BaseModel):
    """新增账号
    """
    phone:str = Field(default='',description='手机号,唯一')
    acct:str = Field(description='账户,唯一')
    nick_name:str = Field(description='昵称')
    real_name:str = Field(default='',description='实名')
    status:int = Field(default=UserSettings.status_enable,description='状态')
    avatar:str = Field(default='',description='头像URL')

class AccountUpdate(BaseModel):
    """修改账号
    """
    id:int =  Field(description='用户ID')
    nick_name:str = Field(description='昵称')
    real_name:str = Field(default='',description='实名')
    status:int = Field(description='状态')

class AccountDelete(BaseModel):
    """删除账号
    """
    id:int =  Field(description='用户ID')    


class AccountList(Pagination):
    """获取账号列表
    """
    phone:str | None  = None
    nick_name:str | None = None
    status: int | None = None


class AccountAPI:
    def chk_unique(self,db:Session,acct:str='',phone:str='',except_id:int=None)->Rsp|None:
        """账号唯一性检测

        Args:
            db:Session 数据库会话
            acct:str 账号
            phone:str 手机号
            except_id:int 需排除的ID,用于修改数据
        
        Returns:
            Success:None 成功
            Failed:Rsp 返回错误信息
        """

        if except_id is None:
            expression = None
        else:
            expression = User.id != except_id

        # 唯一性判断条件
        rules = [
            ('账号已被使用', and_(User.acct==acct,User.deleted == False)),
            ('手机号已被使用',and_(User.phone==phone,User.phone != '', User.deleted == False)),
        ]

        return ORM.unique_chk(db,rules,expression)

    def create(self,db:Session,act:ActInfo,data:AccountCreate)->Rsp:
        """新增账号信息
        """
        if rsp := self.chk_unique(db=db,acct=data.acct,phone=data.phone):
            return rsp
        
        insert_info = ORM.insert_info(act.user_id)
        u = User(**data.model_dump(),**insert_info)
        
        try:
            db.add(u)
            db.flush()
            # 默认密码 hash加密后存入数据库
            default_passwd = settings.default_passwd
            hash_passwd = hash_api.hash_text(default_passwd)

            # 认证信息
            a = UserAuth(user_id=u.id, type=UserSettings.auth_password,value=hash_passwd,**insert_info)
            db.add(a)
            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(data=f'{e}')
    
        return Rsp()

    def update(self,db:Session,act:ActInfo,data:AccountUpdate)->Rsp:
        """修改账号信息
        """
        # 初始化用户保护
        if data.id == 1:
            return Rsp(code=1,message='系统初始用户不可修改')
        
        update_info = ORM.update_info(act.user_id)

        stmt = update(User).where(
            User.id == data.id
        ).values(
            nick_name = data.nick_name, real_name = data.real_name, status = data.status, **update_info
        )
        ORM.commit(db,stmt)
        return Rsp()

    def delete(self,db:Session,act:ActInfo,data:AccountDelete)->Rsp:
        """删除账号信息
        """

        # 初始化用户保护
        if data.id == 1:
            return Rsp(code=1,message='系统初始用户不可删除')

        update_info = ORM.update_info(act.user_id)

        try:
            for stmt in [
                # 逻辑删除用户的基础信息,释放账号和手机号,可供其他账号使用
                update(User).where(User.id == data.id).values(deleted=True,acct=str(uuid4()),phone='',**update_info),
                # 物理删除该用户的认证信息
                delete(UserAuth).where(UserAuth.user_id == data.id)
            ]:
                db.execute(stmt)
            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(data=f'{e}')            

        return Rsp()

    def get_list(self,db:Session,data:AccountList)->Rsp:
        """获取账号列表
        """
        b_user=alias(User)
        stmt = select(
            User.id,User.acct,User.nick_name,User.phone,User.status,User.upd_dt,
            b_user.c.nick_name.label('upd_nick_name'),
            b_user.c.real_name.label('upd_real_name'),
        ).join_from(User,b_user, and_(User.upd_id == b_user.c.id,User.deleted == False))

        if data.phone is not None:
            stmt = stmt.where(User.phone.contains(data.phone))

        if data.status is not None:
            stmt = stmt.where(User.status == data.status)

        if data.nick_name is not None:
            stmt = stmt.where(User.nick_name.contains(data.nick_name))

        result = ORM.pagination(db,stmt,page_idx=data.page_idx,page_size=data.page_size,order=[User.crt_dt.desc()])
        return Rsp(data=result)

    def get_detail(self,db:Session,id:int)->Rsp:
        """获取账号详情
        """
        stmt = select(
            User.id,User.phone,User.acct,
            User.nick_name,User.real_name,
            User.status,User.avatar
        ).where(
            and_(User.deleted == False, User.id == id)
        )
        result = ORM.one(db,stmt)
        return Rsp(data=result)


account_api = AccountAPI()
