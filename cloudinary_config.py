import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import os

load_dotenv()

def initialize_cloudinary():
    """Initialize Cloudinary with credentials from environment variables"""
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )

def upload_image(file_path, public_id=None, folder=None):
    """Upload an image to Cloudinary
    
    Args:
        file_path: Path to the image file
        public_id: Optional custom public ID for the image
        folder: Optional folder name in Cloudinary
        
    Returns:
        dict: Upload response including URLs and other metadata
    """
    options = {
        'use_filename': True,
        'unique_filename': True,
        'overwrite': True,
        'resource_type': "auto"
    }
    
    if folder:
        options['folder'] = folder
    if public_id:
        options['public_id'] = public_id

    try:
        # Upload the image
        result = cloudinary.uploader.upload(file_path, **options)
        return {
            'public_id': result['public_id'],
            'url': result['secure_url'],
            'thumbnail_url': cloudinary.utils.cloudinary_url(
                result['public_id'],
                width=300,
                height=300,
                crop='fill'
            )[0]
        }
    except Exception as e:
        print(f"Failed to upload image to Cloudinary: {str(e)}")
        raise

def delete_image(public_id):
    """Delete an image from Cloudinary
    
    Args:
        public_id: The public ID of the image to delete
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result
    except Exception as e:
        print(f"Failed to delete image from Cloudinary: {str(e)}")
        raise
