from fastapi import APIRouter, HTTPException, status
from ..schemas.models import DriveIngestRequest, FileProcessResult, HealthCheckResponse
from ..services.drive_ingestion import process_drive_folder
from fastapi import UploadFile, File
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import io
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

@router.post('/api/trigger-ingestion', response_model=List[FileProcessResult])
async def ingest_from_drive(request: DriveIngestRequest):
    try:
        folder_id=os.getenv('KB_DATA_STORAGE_DRIVE_ID')
        persist_path = os.getenv('CHROMA_DB_PATH')
        tracker_txt = os.getenv('KB_PROCESSED_FILES')

        return process_drive_folder(
            folder_id=folder_id,
            persist_directory=persist_path,
            tracker_txt=tracker_txt,
            force_reprocess=request.force_reprocess
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Drive ingestion failed: {str(e)}'
        )


@router.post("/api/upload-file", status_code=200)
async def upload_file_to_drive(file: UploadFile = File(...)):
    try:
        # Load service account credentials
        credentials_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        if not credentials_path:
            raise Exception("Service account file path not configured.")
        creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/drive"]
        )

        drive_service = build("drive", "v3", credentials=creds)
        folder_id = os.getenv('KB_DATA_STORAGE_DRIVE_ID')
        if not folder_id:
            raise Exception("Google Drive folder ID not set.")

        # Check if a file with the same name already exists in the folder
        query = f"name = '{file.filename}' and '{folder_id}' in parents and trashed = false"
        response = drive_service.files().list(q=query, fields="files(id, name)").execute()
        if response.get("files"):
            return {
                "message": f"A file named '{file.filename}' already exists in the target folder.",
                "file_exists": True
            }

        # Read file content
        contents = await file.read()
        fh = io.BytesIO(contents)

        # Upload file
        file_metadata = {
            "name": file.filename,
            "parents": [folder_id]
        }
        media = MediaIoBaseUpload(fh, mimetype=file.content_type)

        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name"
        ).execute()

        return {
            "message": "File uploaded successfully.",
            "file_id": uploaded_file.get("id"),
            "file_name": uploaded_file.get("name"),
            "file_exists": False
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


def register_routes(app):
    app.include_router(router)
