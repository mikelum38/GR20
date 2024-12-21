import requests
import os
from dotenv import load_dotenv
import uuid
from PIL import Image
import io
from typing import Optional, Dict, Any
import magic

load_dotenv()

class SupabaseStorage:
    def __init__(self):
        """Initialize Supabase Storage client"""
        self.base_url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        self.bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'photos')
        self.headers = {
            'Authorization': f"Bearer {self.key}",
            'apikey': self.key
        }

    def upload_image(self, file_path: str, folder: Optional[str] = None) -> Dict[str, Any]:
        """Upload an image to Supabase Storage"""
        try:
            # Vérifier le type de fichier
            file_type = magic.from_file(file_path, mime=True)
            if not file_type.startswith('image/'):
                raise ValueError(f"Le fichier n'est pas une image : {file_type}")

            # Redimensionner l'image si nécessaire
            with Image.open(file_path) as img:
                # Conserver le format original
                output = io.BytesIO()
                img.save(output, format=img.format)
                file_data = output.getvalue()

            # Construire le chemin de stockage
            filename = os.path.basename(file_path)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            storage_path = unique_filename if not folder else f"{folder}/{unique_filename}"

            # Upload vers Supabase
            url = f"{self.base_url}/storage/v1/object/{self.bucket_name}/{storage_path}"
            response = requests.post(
                url,
                headers=self.headers,
                data=file_data
            )
            response.raise_for_status()

            # Construire l'URL publique
            public_url = f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/{storage_path}"
            
            return {
                "path": storage_path,
                "url": public_url
            }

        except Exception as e:
            print(f"Erreur lors de l'upload : {str(e)}")
            raise

    def delete_image(self, path: str) -> bool:
        """Delete an image from Supabase Storage"""
        try:
            url = f"{self.base_url}/storage/v1/object/{self.bucket_name}/{path}"
            response = requests.delete(
                url,
                headers=self.headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression : {str(e)}")
            return False

# Create singleton instance
storage = SupabaseStorage()
