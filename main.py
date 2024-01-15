from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from eromodapi.config.settings import settings #noqa
from eromodapi.api import user,role,org


app = FastAPI()


# 跨域设定CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user.api,tags=['统一用户中心'])
app.include_router(org.api,tags=['统一用户中心'])
# app.include_router(role.api,tags=['统一用户中心'])

