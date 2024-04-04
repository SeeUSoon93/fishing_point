from fastapi import Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import List
from databases import Database
from api.cors import create_app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("myapp")

app = create_app()

app.mount("/static", StaticFiles(directory="static"), name="static")
database = Database("sqlite:///fp.db")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/main")
async def go_main():
    return FileResponse("index.html")

@app.get("/state_data")
async def get_state():
    # point_table에서 위치 목록 불러오기
    query = "SELECT DISTINCT state FROM point_table"    
    results = await database.fetch_all(query=query)
    states = [result["state"] for result in results]

    query2 = "SELECT DISTINCT UniqueFishSpecies FROM fish_table"    
    results2 = await database.fetch_all(query=query2)
    species = [result["UniqueFishSpecies"] for result in results2]

    return JSONResponse(content={"states": states, "species": species})

@app.get("/marker_data")
async def get_marker():
    query = "SELECT fpName, state, city, latitude, longitude, address FROM point_table"
    results = await database.fetch_all(query=query)
    fpNames = [result["fpName"] for result in results]
    states = [result["state"] for result in results]
    citys = [result["city"] for result in results]
    latitudes = [result["latitude"] for result in results]
    longitudes  = [result["longitude"] for result in results]
    addresss = [result["address"] for result in results]

    return JSONResponse(content={"fpNames": fpNames, "states":states, "citys":citys, "latitudes":latitudes, "longitudes":longitudes, "addresss":addresss})


@app.get("/filter")
async def filter_data(states: List[str] = Query(None), species: List[str] = Query(None)):
    query = "SELECT * FROM point_table"

    if species :
        # 물고기 이름을 받아와서 번호 조회
        species_placeholders = ", ".join([f"'{item}'" for item in species])
        species_query = f"SELECT DISTINCT speciesIdx FROM fish_table WHERE UniqueFishSpecies IN ({species_placeholders})"
        species_results = await database.fetch_all(query=species_query)
        species_idxs = [result["speciesIdx"] for result in species_results]

        if species_idxs:
            species_idx_placeholders = ", ".join([str(idx) for idx in species_idxs])
            point_idx_query = f"SELECT DISTINCT pointIdx FROM asso_table WHERE speciesIdx IN ({species_idx_placeholders})"
            point_idx_results = await database.fetch_all(query=point_idx_query)
            point_idxs = [result["pointIdx"] for result in point_idx_results]

            if point_idxs:
                point_idx_placeholders = ", ".join([str(idx) for idx in point_idxs])
                query += f" WHERE pointIdx IN ({point_idx_placeholders})"

    if states:
        states_placeholders = ", ".join([f"'{state}'" for state in states])
        if 'WHERE' in query:
            query += f" AND state IN ({states_placeholders})"
        else:
            query += f" WHERE state IN ({states_placeholders})"   
    
    results = await database.fetch_all(query=query)

    fpNames = [result["fpName"] for result in results]
    stateList = [result["state"] for result in results]
    citys = [result["city"] for result in results]
    latitudes = [result["latitude"] for result in results]
    longitudes  = [result["longitude"] for result in results]
    addresss = [result["address"] for result in results]

    return JSONResponse(content={"fpNames": fpNames, "states":stateList, "citys":citys, "latitudes":latitudes, "longitudes":longitudes, "addresss":addresss})

@app.get("/fp_info/{fpName}")
async def get_fp_info(fpName: str):
    query = "SELECT * FROM point_table WHERE fpName = :fpName"
    result = await database.fetch_one(query=query, values={"fpName": fpName})
    if result:
        return result
    raise HTTPException(status_code=404, detail="Fishing point not found")


