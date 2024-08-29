from fastapi import FastAPI
from fastapi import APIRouter

router = APIRouter()

@router.get("/excel-to-mongo", name = "mongo db에 수집")
def excel_to_mongo():
    from app.api.service.excel_to_mongo import main
    
    return main()
