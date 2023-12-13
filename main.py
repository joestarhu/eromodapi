from fastapi import FastAPI
from tomllib import load as toml_load
from eromodapi.config.settings import settings
app = FastAPI()

@app.get('/')
def toml_hello():
    return settings.config['mysql']



