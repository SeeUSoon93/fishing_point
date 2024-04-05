from fastapi import APIRouter
from app.db.database import database
from typing import List

router = APIRouter()

# 목록 조회 함수
async def fetch_distinct_column(column: str, table: str) -> List[str]:
    query = f"SELECT DISTINCT {column} FROM {table}"
    result_list = await database.fetch_all(query=query)
    return [result[column] for result in result_list]

# 사이드바 목록 불러오는 메서드
@router.get("/sidebar_data")
async def get_sidebar_data():
    state_list = await fetch_distinct_column('state', 'point_table')
    fish_list = await fetch_distinct_column('UniqueFishSpecies', 'fish_table')
    
    return {"state_list": state_list, "fish_list": fish_list}

# 전체 포인트 정보 불러오는 메서드
@router.get("/point_data")
async def get_point_data():
    query = "SELECT * FROM point_table"
    result = await database.fetch_all(query=query)
    point_data = {key: [getattr(row, key) for row in result] for key in result[0].keys()}

    return point_data