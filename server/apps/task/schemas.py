from pydantic import Field
from typing import Optional

from commons.schemas import BaseResponse


class UploadResponse(BaseResponse):
    task_id: Optional[str] = Field('', title="任务id")
