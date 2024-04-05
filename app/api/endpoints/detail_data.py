from fastapi import APIRouter
from app.db.database import database
import requests
import datetime

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

def weather_info(lat: float, lon: float):
    now = datetime.datetime.now()
    today = now.strftime("%Y%m%d")    
    nowTime = now.strftime("%H00")

    weather_response = requests.get(f'''http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst?serviceKey={encodingKey}&numOfRows={numOfRows}&pageNo={pageNo}&base_date={today}&base_time={nowTime}&nx={lat}&ny={lon}''')
    return weather_response.json()
# 날씨 하는중
@router.get("/wether_info/{fpName}")
async def get_wether_info(fpName: str):
    query = "SELECT latitude, longitude FROM point_table WHERE fpName = :fpName"
    result = await database.fetch_one(query=query, values={"fpName": fpName})

    if result:
        latitude = [result['latitude'] for latitude in result]
        longitude = [result['longitude'] for longitude in result]
        weather_result = weather_info(latitude, longitude)
        return weather_result

    return {"error": "not found"}