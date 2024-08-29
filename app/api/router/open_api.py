from fastapi import APIRouter

from starlette.requests import Request
from app.api.service.open_api import OpenApi

router = APIRouter()

@router.get("/to-excel", name = "오픈 api 데이터를 엑셀데이터로 변환")
def models(r: Request, id: str, parameter: str = None): 

    openApi = OpenApi()

    return openApi.to_excel(id, parameter)