import sys
import os

# 현재 파일의 부모 디렉토리를 sys.path에 추가하여 모듈 경로를 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from app.api.router.api import router

app = FastAPI()
app.include_router(router, prefix="/v1")

# @app.get("/crawler/excel-to-mongo")
# def excel_to_mongo():
#     from app.api.service.excel_to_mongo import main
#     main();

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)