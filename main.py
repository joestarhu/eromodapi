from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from eromodapi.config.settings import settings #noqa
from eromodapi.api import user,org #noqa

def init_application()->FastAPI:
    """初始化FastAPI对象
    """

    app = FastAPI(**settings.fastapi_kwargs)

    # 跨域设定CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(user.api,tags=['用户'])
    app.include_router(org.api,tags=['组织'])

    return app

app = init_application()
