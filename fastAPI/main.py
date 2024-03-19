from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
# python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 9090

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/main")
def go_main():
    return FileResponse("index.html")