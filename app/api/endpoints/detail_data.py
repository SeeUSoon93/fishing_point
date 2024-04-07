from fastapi import APIRouter
from app.db.database import database
from app.api.method import weather
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/detail_info/{fpName}")
async def get_detail_info(fpName: str):
    point_query = "SELECT * FROM point_table WHERE fpName = :fpName"
    point_result = await database.fetch_one(query=point_query, values={"fpName": fpName})

    if point_result:
        species_query = """
        SELECT UniqueFishSpecies FROM fish_table
        WHERE speciesIdx IN (
            SELECT speciesIdx FROM asso_table WHERE pointIdx = :pointIdx
        )
        """
        species_results = await database.fetch_all(query=species_query, values={"pointIdx": point_result['pointIdx']})
        species = [result['UniqueFishSpecies'] for result in species_results]
        
        result_dict = dict(point_result)
        result_dict["species"] = species

        return result_dict

    return {"error": "not found"}

@router.get("/weather_info/{fpName}")
async def get_weather_info(fpName: str):
    query = "SELECT latitude, longitude FROM point_table WHERE fpName = :fpName"
    result = await database.fetch_one(query=query, values={"fpName": fpName})

    if result:
        weather_result = weather.weather_info(result['latitude'], result['longitude'])
        weather_data = weather_result.to_dict(orient='records')
        return weather_data

    return {"error": "not found"}