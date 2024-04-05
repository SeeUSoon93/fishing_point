from fastapi import APIRouter, Query
from typing import List
from app.db.database import database

router = APIRouter()

@router.get("/filterling")
async def get_filterling_data(states: List[str] = Query(None), species: List[str] = Query(None)):
    query = "SELECT * FROM point_table"

    if species :
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

    if results:
        filterling_data = {key: [getattr(row, key) for row in results] for key in results[0].keys()}
        return filterling_data
    return {"error": "not found"}