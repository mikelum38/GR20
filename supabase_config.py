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
        """Upload an image to Supabase Storage
        
        Args:
            file_path: Path to the image file
            folder: Optional folder name within the bucket
            
        Returns:
            dict: Upload response including file path and public URL
            
        Raises:
            ValueError: If file is not a valid image
            Exception: If upload fails
        """
        try:
            # Verify that the file is an image
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(file_path)
            if not file_type.startswith('image/'):
                raise ValueError(f"File is not an image. Detected type: {file_type}")

            # Generate a unique filename with original extension
            file_ext = os.path.splitext(file_path)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            
            # Construct the storage path
            storage_path = f"{folder}/{unique_filename}" if folder else unique_filename
            
            # Read the file
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Upload to Supabase Storage
            url = f"{self.base_url}/storage/v1/object/{self.bucket_name}/{storage_path}"
            response = requests.post(
                url,
                headers=self.headers,
                data=file_data
            )
            response.raise_for_status()

            # Construct the public URL
            public_url = f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/{storage_path}"
            
            return {
                'path': storage_path,
                'url': public_url
            }

        except Exception as e:
            raise Exception(f"Failed to upload image: {str(e)}")

    def delete_image(self, path: str) -> bool:
        """Delete an image from Supabase Storage
        
        Args:
            path: Path to the image in storage
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            Exception: If deletion fails
        """
        try:
            url = f"{self.base_url}/storage/v1/object/{self.bucket_name}/{path}"
            response = requests.delete(
                url,
                headers=self.headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            raise Exception(f"Failed to delete image: {str(e)}")

# Create singleton instance
storage = SupabaseStorage()
