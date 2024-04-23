import sys
sys.stdout.flush()

from fastapi import FastAPI,Response,status,HTTPException,Depends
from . import models,schemas,utils
from .database import engine,SessionLocal,get_db
from .routers import user, auth,admin
from .config import settings
from fastapi.middleware.cors import CORSMiddleware
models.Base.metadata.create_all(bind=engine)

import os



app = FastAPI(title="Shomonnoi_app")



origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.include_router(task_router.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "khela hobe!!!"}
