from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import home, home_data, filterling, detail_data
from app.db.database import database

app = FastAPI()

# 라우터
app.include_router(home.router)
app.include_router(home_data.router)
app.include_router(filterling.router)
app.include_router(detail_data.router)

# static 파일 서비스 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# DB 연결
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

