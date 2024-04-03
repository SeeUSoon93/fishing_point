from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from databases import Database

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
database = Database("sqlite:///fishing_db.db")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/main")
def go_main():
    return FileResponse("index.html")

@app.get("/location/{pointName}")
async def get_location(pointName: str):
    query = "SELECT xCoordi, yCoordi FROM fishingPoint WHERE pointName = :pointName"
    result = await database.fetch_one(query=query, values={"pointName": pointName})
    if result is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return JSONResponse(content={"latitude": result["xCoordi"], "longitude": result["yCoordi"]})
