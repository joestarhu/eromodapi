from enum import Enum
from pydantic import BaseModel,Field
from sqlalchemy import select,update,delete,and_,alias
from sqlalchemy.orm.session import Session
from eromodapi.config.settings import settings,hash_api,jwt_api #noqa
from eromodapi.model.user import User,UserAuth,UserSettings #noqa
# from eromodapi.model.usercenter import User,UserAuth #noqa
from eromodapi.schema.base import ORM,Rsp,RspError,Pagination #noqa



# 请求参数
class UserCreate(BaseModel):
    acct:str = Field(description='账号')
    nick_name:str = Field(description='昵称')
    real_name:str = Field(default='',description='实名')
    phone:str|None = Field(default=None,description='手机号')
    status:int = Field(default=UserSettings.status_enable,description='状态')
    avatar:str = Field(default='',description='头像URL')


class UserUpdate(BaseModel):
    id:int =  Field(description='用户ID')
    acct:str = Field(description='账号')
    nick_name:str = Field(description='昵称')
    real_name:str = Field(default='',description='实名')
    phone:str|None = Field(default=None,description='手机号')
    status:int = Field(description='状态')
    avatar:str = Field(default='',description='头像URL')


class UserDelete(BaseModel):
    id:int =  Field(description='用户ID')


class PasswordLogin(BaseModel):
    acct:str = Field(description='账号')
    passwd:str= Field(description='密码')


class UserList(Pagination):
    nick_name:str | None = None
    phone:str | None = None
    status:int | None = None

class UserAPI:
    def jwt_decode(self,db:Session,token:str)->dict:
        """JWT token解码, 获取用户信息,权限等内容

        Args:
            db:Session 数据库会话
            token:str jwt字符串
        """
        try:
            data = jwt_api.decode(token)
        except Exception as e:
            raise RspError(401,'无效的用户token',f'{e}')
        
        stmt = select(User.status).where(and_(User.id == data['user_id'],User.deleted==False))
        result = ORM.one(db,stmt)

        # 无数据或用户已处于禁用状态,不可继续执行
        if not result:
            raise RspError(401,'账号不存在')
        
        # 用户禁用状态,不允许继续执行
        if result['status'] != UserSettings.status_enable:
            raise RspError(401,'账号已被停用')
        
        # 获取角色信息

        return data

    def chk_user_unique(self,db:Session,acct:str='',phone:str='',except_id:int=None)->Rsp|None:
        """检查必填字段是否

        Args:
            db:Session 数据库会话
            acct:str 账号
            phone:str 手机号
            except_id:int 需排除的ID,用于修改数据
        
        Returns:
            Success:None 成功
            Failed:Rsp 返回错误信息
        """

        # 需被排除的用户
        if except_id:
            expression = User.id != except_id
        else:
            expression = None

        # 唯一性判断条件
        rules = [
            ('账号已被使用',and_(User.acct==acct,User.acct !='',User.deleted == False)),
            ('手机号已被使用',and_(User.phone == phone, User.phone != '',User.deleted == False)),
        ]

        # 唯一性检测
        return ORM.unique_chk(db,rules,expression)

    def create_user(self,db:Session,c_id:int,data:UserCreate)->Rsp:
        """创建用户

        Args:
            db:Session 数据库会话
            c_id:int 操作用户ID
            data:UserCreate 新增用户数据
        """
        if data.phone == '':
            data.phone = None

        insert_info = ORM.insert_info(c_id)
        u = User(**data.model_dump(),**insert_info)

        if rsp := self.chk_user_unique(db,data.acct,data.phone):
            return rsp

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

    def update_user(self,db:Session,u_id:int,data:UserUpdate)->Rsp:
        """修改用户信息
        """
        # 不允许操作系统初始用户
        if data.id == 1:
            return Rsp(code=1,message='系统初始用户不可操作')
        
        if data.phone == '':
            data.phone = None

        if rsp := self.chk_user_unique(db,data.acct,data.phone,data.id):
            return rsp

        update_info = ORM.update_info(u_id)
        stmt = update(User).where(User.id == data.id).values(nick_name=data.nick_name,real_name=data.real_name,phone=data.phone,status=data.status,**update_info)
        ORM.commit(db,stmt)
        return Rsp()

    def delete_user(self,db:Session,u_id:int,data:UserDelete)->Rsp:
        """删除用户信息
        """
        # 不允许操作系统初始用户
        if data.id == 1:
            return Rsp(code=1,message='系统初始用户不可操作')
        
        try:
            update_info = ORM.update_info(u_id)
            for stmt in [
                # 物理删除该用户的认证信息
                delete(UserAuth).where(UserAuth.user_id == data.id),
                # 逻辑删除用户的基础信息,释放账号和手机号,可供其他账号使用
                update(User).where(User.id == data.id).values(deleted=True,acct=None,phone=None,**update_info)]:
                db.execute(stmt)
            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(data=f'{e}')

        return Rsp()

    def get_user_list(self,db:Session,data:UserList)->Rsp:
        """获取用户列表信息
        """
        b_user=alias(User)
        stmt = select(
            User.id,User.acct,User.nick_name,User.phone,User.status,User.u_dt,
            b_user.c.nick_name.label('u_nick_name'),
            b_user.c.real_name.label('u_real_name'),
        ).join_from(User,b_user, and_(User.u_id == b_user.c.id,User.deleted == False))

        if data.status != None:
            stmt = stmt.where(User.status == data.status)

        if data.nick_name:
            stmt = stmt.where(User.nick_name.contains(data.nick_name))

        if data.phone:
            stmt = stmt.where(User.phone.contains(data.phone))

        data = ORM.pagination(db,stmt,page_idx=data.page_idx,page_size=data.page_size,order=[User.c_dt.desc()])

        return Rsp(data=data) 

    def get_user_detail(self,db:Session,id:int)->Rsp:
        """获取用户详情
        """
        stmt = select(User.id,User.acct,User.nick_name,User.real_name,User.phone,User.status,User.avatar).where(and_(User.deleted==False,User.id == id))
        result = ORM.one(db,stmt)
        return Rsp(data=result)

    def password_login(self,db:Session,data:PasswordLogin)->Rsp:
        """密码认证登录
        """

        try:
            plain_text = hash_api.decrypt(data.passwd)
        except Exception as e:
            raise RspError(400,'解密用户密码失败',f'{e}')
        
        stmt = select(User.id,
                      User.nick_name,
                      User.avatar,
                      User.status,
                      UserAuth.value).join_from(
            User,UserAuth,
            and_(
                User.id == UserAuth.user_id,
                User.deleted == False,
                UserAuth.type == UserSettings.auth_password
            )
        ).where(
            User.acct == data.acct
        )

        result = ORM.one(db,stmt)      

        if not result or hash_api.verifty(plain_text,result['value']) == False:
            return Rsp(code=1,message='账号或密码错误')
        
        if result['status'] != UserSettings.status_enable:
            return Rsp(code=1,message='该账户已被停用')
            
        jwt = jwt_api.encode(user_id=result['id'])
        
        return Rsp(data=dict(jwt=jwt))


user_api = UserAPI()