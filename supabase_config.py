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
            
            # Open and optimize the image
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Create an in-memory buffer
                buffer = io.BytesIO()
                
                # Save with optimization
                img.save(buffer, format='JPEG', optimize=True, quality=85)
                buffer.seek(0)
                
                # Prepare the file for upload
                files = {'file': (storage_path, buffer, 'image/jpeg')}
                
                # Upload to Supabase Storage
                response = requests.post(
                    f"{self.base_url}/storage/v1/object/{self.bucket_name}/{storage_path}",
                    headers=self.headers,
                    files=files
                )
                
                if response.status_code != 200:
                    raise Exception(f"Upload failed: {response.status_code} - {response.text}")
                
                # Get public URL
                public_url = f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/{storage_path}"
                
                return {
                    'path': storage_path,
                    'url': public_url,
                    'size': os.path.getsize(file_path)
                }
                
        except Exception as e:
            print(f"Failed to upload image to Supabase Storage: {str(e)}")
            raise

    def delete_image(self, file_path: str) -> bool:
        """Delete an image from Supabase Storage
        
        Args:
            file_path: Storage path of the file to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            Exception: If deletion fails
        """
        try:
            response = requests.delete(
                f"{self.base_url}/storage/v1/object/{self.bucket_name}/{file_path}",
                headers=self.headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Delete failed: {response.status_code} - {response.text}")
                
            return True
            
        except Exception as e:
            print(f"Failed to delete image from Supabase Storage: {str(e)}")
            raise

    def get_image_url(self, file_path: str) -> str:
        """Get the public URL for an image
        
        Args:
            file_path: Storage path of the file
            
        Returns:
            str: Public URL of the image
        """
        return f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/{file_path}"

# Create a singleton instance
storage = SupabaseStorage()
