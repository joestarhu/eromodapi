from pydantic import BaseModel,Field
from sqlalchemy import select,update,delete,and_,alias
from sqlalchemy.orm.session import Session
from eromodapi.config.settings import settings,hash_api,jwt_api #noqa
from eromodapi.model.user import User,UserAuth,UserSettings #noqa
from eromodapi.model.org import Org,OrgUser,OrgSettings #noqa
from eromodapi.model.role import Role,RoleUser,RoleSettings #noqa
from eromodapi.schema.base import ORM,Rsp,RspError,Pagination #noqa


class PasswordLogin(BaseModel):
    """账密登录
    """
    acct:str = Field(description='账号')
    passwd:str = Field(description='密码')

class SelectOrg(BaseModel):
    """选择组织
    """
    org_id:int = Field(description='组织ID')


class AuthAPI:
    def jwt_encode(self,user_id,nick_name,avatar='',user_orgs:list=[],login_org:int=None)->str:
        """JWT编码
        """
        return jwt_api.encode(user_id=user_id,nick_name=nick_name,avatar=avatar,user_orgs=user_orgs,login_org=login_org)

    def jwt_decode(self,token:str)->dict:
        """JWT解码
        """

        try:
            jwt_data = jwt_api.decode(token)
        except Exception as e:
            raise RspError(401,'无效的用户token',f'{e}')

        payload = {}

        for kw in ["user_id","nick_name","user_orgs","login_org"]:
            payload[kw] = jwt_data.get(kw,None)
        return payload

    def select_org(self,payload:dict,data:SelectOrg)->Rsp:
        """选择登录组织(更新JWT)
        """
        payload['login_org']=data.org_id
        jwt = self.jwt_encode(**payload)
        return Rsp(data=dict(jwt=jwt))

    def password_login(self,db:Session,data:PasswordLogin)->Rsp:
        """账密登录
        """

        try:
            plain_text = hash_api.decrypt(data.passwd)
        except Exception as e:
            raise RspError(400,'解密用户密码失败',f'{e}')
        
        # 获取账号基本信息
        stmt =  select(
            User.id,
            User.nick_name,
            User.status,
            UserAuth.value).join_from(
                User, UserAuth,
                and_(
                    User.id == UserAuth.user_id,
                    User.deleted == False,
                    UserAuth.type == UserSettings.auth_password
                )
            ).where(
                User.acct == data.acct
            )
        
        user = ORM.one(db,stmt)

        if not user or hash_api.verifty(plain_text,user['value']) == False:
            return Rsp(code=1,message='账号或密码错误')
        
        if user['status'] != UserSettings.status_enable:
            return Rsp(code=1,message='账号已被停用')
        

        # 获取用户权限



        
        # 获取用户组织信息
        stmt = select(
            Org.id,
            Org.name).join_from(
                Org,OrgUser,
                and_(
                    Org.id == OrgUser.org_id,
                    Org.deleted == False,
                    Org.status == OrgSettings.status_enable,
                    OrgUser.status == OrgSettings.user_status_enable
                )
            ).where(
                OrgUser.user_id == user['id']
            )
        
        user_orgs = ORM.all(db,stmt)

        # 当用户仅属于一个组织的时候,默认取这个组织作为登录组织
        if len(user_orgs) == 1:
            login_org = user_orgs[0]['id']
        else:
            login_org = None 

        # 获取应用角色数据
        jwt = self.jwt_encode(user_id=user['id'],nick_name=user['nick_name'],user_orgs=user_orgs,login_org=login_org)
        return Rsp(data=dict(jwt=jwt))



auth_api = AuthAPI()