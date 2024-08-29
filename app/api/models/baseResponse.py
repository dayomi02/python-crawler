from pydantic import BaseModel, Field


# 기본 response 포멧
class BaseResponse(BaseModel):
    code: int = Field(default=200, description="응답 코드")
    message: str = Field(default="성공", description="응답 메세지")
    result: object = Field(default="", description="응답 객체")