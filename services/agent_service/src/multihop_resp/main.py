from fastapi import FastAPI
from . import resp_api

app = FastAPI()
app.include_router(resp_api.router) 