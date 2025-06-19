from fastapi import APIRouter, HTTPException, status
from ..schemas.models import DriveIngestRequest, FileProcessResult, HealthCheckResponse
from ..services.drive_ingestion import process_drive_folder
import os
from typing import List

router = APIRouter()

@router.get('/', include_in_schema=False)
async def root():
    return {'message': 'Genie Mentor Agent Data Ingestion Service API'}

@router.get('/health', response_model=HealthCheckResponse)
async def health_check():
    return {
        'status': 'healthy',
        'details': {
            'service': 'data-ingestion',
            'version': '1.0.0'
        }
    }

@router.post('/api/drive-ingest', response_model=List[FileProcessResult])
async def ingest_from_drive(request: DriveIngestRequest):
    persist_path = os.getenv('CHROMA_DB_PATH', './chroma_db')
    tracker_txt = os.getenv('KB_PROCESSED_FILES', './tracking/KB_processed_files_history.txt')

    try:
        return process_drive_folder(
            folder_id=request.folder_id,
            persist_directory=persist_path,
            tracker_txt=tracker_txt,
            force_reprocess=request.force_reprocess
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Drive ingestion failed: {str(e)}'
        )

def register_routes(app):
    app.include_router(router)
