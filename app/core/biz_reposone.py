from fastapi.responses import JSONResponse
from typing import Any, Optional



# 目前先不区分 code/status_code 区别，后续需要更复杂的业务逻辑时再区分
class BizResponse(JSONResponse):
    def __init__(
        self, data: Optional[Any] = None, msg: str = "success", status_code: int = 200, 
    ):
        
        # 目前先让 HTTP 状态码作为业务状态码保持一致即可
        code = status_code
        content = {
            "data": data,
            "msg": msg,
            "code": code
        }
        super().__init__(content=content, status_code=status_code)

