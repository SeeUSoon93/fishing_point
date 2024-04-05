from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/fphome")
async def go_home():
    return FileResponse("app/templates/index.html")