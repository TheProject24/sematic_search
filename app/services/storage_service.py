from supabase import create_client, Client
from app.core.config import settings
import uuid

class CloudStorage:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        self.bucket = settings.BUCKET_NAME

    async def upload_file(self, file_bytes: bytes, filename: str, user_id: str) -> str:
        file_id = str(uuid.uuid4())
        file_path = f"{user_id}/{file_id}_{filename}"

        res = self.supabase.storage.from_(self.bucket).upload(
            path=file_path,
            file=file_bytes,
            file_options = {"content-type": "application/pdf"}
        )

        return file_path
    def get_download_url(self, file_path: str):
        return self.supabase.storage.from_(self.bucket).create_signed_url(file_path, 60)
    
cloud_storage = CloudStorage()