import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def configure_app(app: FastAPI):
    load_dotenv(override=True)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv('ALLOWED_ORIGINS', '*').split(','),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
