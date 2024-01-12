from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import select,update,delete,and_,alias
from sqlalchemy.orm.session import Session
from eromodapi.config.settings import settings,hash_api,jwt_api,AuthType,UserStatus #noqa
from eromodapi.model.usercenter import User,UserAuth #noqa
from eromodapi.schema.base import ORM,Rsp,RspError,Pagination #noqa


class UserCreate(BaseModel):
    acct:str
    nick_name:str
    real_name:str = ''
    phone:str|None = None
    status:int = UserStatus.ENABLE.value
    avatar:str = ''

class UserUpdate(BaseModel):
    id:int
    acct:str
    nick_name:str
    real_name:str = ''
    phone:str|None = None
    status:int = 1
    avatar:str = ''

class UserDelete(BaseModel):
    id:int

class UserList(Pagination):
    nick_name:str | None = None
    phone:str | None = None
    status:int | None = None

class PasswordLogin(BaseModel):
    acct:str
    passwd:str



class UserAPI:
    def jwt_decode(self,db:Session,token:str)->dict:
        """JWT token解码, 获取用户信息,权限等内容

        Args:
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
        if result['status'] == UserStatus.DISABLE:
            raise RspError(401,'账号已被禁用')
        
        # 获取角色信息

        return data
    
    def chk_required_field(self,acct:str,nick_name:str)->Rsp|None:
        """检查必填字段是否

        Args:
            acct:str 账号
            nick_name:str 昵称
        
        Returns:
            Success:None 成功
            Failed:Rsp 返回错误信息
        """
        if not acct:
            return Rsp(code=1,message='账号不允许为空')
        if not nick_name:
            return Rsp(code=1,message='用户昵称不允许为空')

    def chk_user_unique(self,db:Session,acct:str='',phone:str='',except_id:int=None)->Rsp|None:
        """检查必填字段是否

        Args:
            db:Session 数据库会话对象
            acct:str 账号
            phone:str 手机号
            except_id:int 需排除的ID,用于修改数据
        
        Returns:
            Success:None 成功
            Failed:Rsp 返回错误信息
        """

        # 逻辑删除用户不在范围内
        base_stmt = select(User.id).where(User.deleted == False)

        # 需被排除的用户
        if except_id:
            base_stmt = base_stmt.where(User.id != except_id)


        # 唯一性判断条件
        rules = [
            ('账号已被使用',and_(User.acct==acct,User.acct !='')),
            ('手机号已被使用',and_(User.phone == phone, User.phone != '')),
        ]

        # 唯一性检测
        for errmsg, condition in rules:
            stmt = base_stmt.where(condition)
            if ORM.counts(db,stmt) > 0 :
                return Rsp(code=1,message=errmsg)

    def create_user(self,db:Session,c_id:int,data:UserCreate)->Rsp:
        """创建用户
        """
        if data.phone == '':
            data.phone = None

        u = User(**data.model_dump(),c_id=c_id,u_id=c_id)

        # 数据完整性检测
        chk_funcs = [
            # 必填字段
            self.chk_required_field(data.acct,data.nick_name),
            # 唯一性检测
            self.chk_user_unique(db,data.acct,data.phone),
        ]

        try:
            # 数据完整性检测
            for result in chk_funcs:
                if result:
                    return result

            db.add(u)
            db.flush()

            # 默认密码 hash加密后存入数据库
            default_passwd = settings.config['default_passwd']
            hash_passwd = hash_api.hash_text(default_passwd)

            # 认证信息
            a = UserAuth(user_id=u.id, type=AuthType.PASSWORD.value,value=hash_passwd,c_id=c_id,u_id=c_id)
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

        # 数据完整性检测
        chk_funcs = [
            # 必填字段
            self.chk_required_field(data.acct,data.nick_name),
            # 唯一性检测
            self.chk_user_unique(db,data.acct,data.phone,data.id),
        ]

        try:
            # 监测必填字段,是否唯一
            for result in chk_funcs:
                if result:
                    return result
                
            now = datetime.now()
            stmt = update(User).where(User.id == data.id).values(
                nick_name=data.nick_name,real_name=data.real_name,phone=data.phone,status=data.status,
                u_dt=now,u_id=u_id)
            db.execute(stmt)
            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(data=f'{e}')

        return Rsp()

    def delete_user(self,db:Session,u_id:int,data:UserDelete)->Rsp:
        """删除用户信息
        """

        # 不允许操作系统初始用户
        if data.id == 1:
            return Rsp(code=1,message='系统初始用户不可操作')
        
        try:
            now = datetime.now()
            for stmt in [
                # 物理删除该用户的认证信息
                delete(UserAuth).where(UserAuth.user_id == data.id),
                # 逻辑删除用户的基础信息,释放账号和手机号,可供其他账号使用
                update(User).where(User.id == data.id).values(deleted=True,u_id = u_id, acct=None,phone=None,u_dt=now)]:
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
                UserAuth.type == AuthType.PASSWORD.value
            )
        ).where(
            User.acct == data.acct
        )

        result = ORM.one(db,stmt)      

        if not result or hash_api.verifty(plain_text,result['value']) == False:
            return Rsp(code=1,message='账号或密码错误')
        
        if result['status'] != UserStatus.ENABLE.value:
            return Rsp(code=1,message='该账户已被停用')
            
        jwt = jwt_api.encode(user_id=result['id'])
        
        return Rsp(data=dict(jwt=jwt))


user_api = UserAPI()