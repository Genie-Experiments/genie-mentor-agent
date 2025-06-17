from pydantic import BaseModel
from typing import Dict, Optional

class DriveIngestRequest(BaseModel):
    folder_id: str
    force_reprocess: Optional[bool] = False

class FileProcessResult(BaseModel):
    filename: str
    status: str
    chunks: Optional[int] = None
    message: Optional[str] = None
    file_type: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str
    details: Dict[str, str]