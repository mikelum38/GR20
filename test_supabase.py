import requests
import os
from dotenv import load_dotenv
import json
from PIL import Image
import io
import uuid

load_dotenv()

def create_bucket(headers, base_url, bucket_name):
    """Create a new bucket in Supabase Storage"""
    try:
        response = requests.post(
            f"{base_url}/storage/v1/bucket",
            headers=headers,
            json={
                "name": bucket_name,
                "public": True
            }
        )
        
        if response.status_code in [200, 201]:
            print(f"\nBucket '{bucket_name}' created successfully")
            return True
        else:
            print(f"\nFailed to create bucket: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error creating bucket: {str(e)}")
        return False

def test_policies(headers, base_url):
    """Test bucket policies"""
    try:
        response = requests.get(
            f"{base_url}/storage/v1/policy",
            headers=headers
        )
        print("\nTesting policies:")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Policies: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Failed to get policies: {response.text}")
    except Exception as e:
        print(f"Error getting policies: {str(e)}")

def test_connection():
    try:
        # Initialize headers
        headers = {
            'Authorization': f"Bearer {os.getenv('SUPABASE_KEY')}",
            'apikey': os.getenv('SUPABASE_KEY'),
            'Content-Type': 'application/json'
        }
        
        # Test the connection by listing buckets
        base_url = os.getenv('SUPABASE_URL')
        bucket_url = f"{base_url}/storage/v1/bucket"
        
        print(f"Testing connection to: {bucket_url}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        
        # First, test the general connection
        response = requests.get(
            f"{base_url}/rest/v1/",
            headers=headers
        )
        print(f"\nGeneral API connection test:")
        print(f"Status: {response.status_code}")
        print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        
        # Then test storage specifically
        response = requests.get(
            bucket_url,
            headers=headers
        )
        
        print(f"\nStorage API response:")
        print(f"Status code: {response.status_code}")
        print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            buckets = response.json()
            print("\nConnection to Supabase Storage successful")
            print(f"Available buckets: {json.dumps(buckets, indent=2)}")
            
            # Check if our bucket exists
            bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'photos')
            if any(b['name'] == bucket_name for b in buckets):
                print(f"\nBucket '{bucket_name}' exists")
            else:
                print(f"\nBucket '{bucket_name}' not found in the list.")
                print("Testing bucket directly...")
                
                # Try to access the bucket directly
                bucket_response = requests.get(
                    f"{base_url}/storage/v1/bucket/{bucket_name}",
                    headers=headers
                )
                print(f"Direct bucket access status: {bucket_response.status_code}")
                print(f"Response: {bucket_response.text}")
                
                # Test policies
                test_policies(headers, base_url)
                
                # Attempt to create the bucket if it doesn't exist
                if bucket_response.status_code == 404:
                    print(f"\nBucket '{bucket_name}' not found. Attempting to create it...")
                    create_bucket(headers, base_url, bucket_name)
        else:
            print(f"\nError connecting to Supabase Storage: {response.status_code}")
            print(f"Response body: {response.text}")
            
    except Exception as e:
        print(f"Error connecting to Supabase Storage: {str(e)}")

def create_test_image():
    """Create a test image"""
    img = Image.new('RGB', (100, 100), color='red')
    img_path = 'test_image.jpg'
    img.save(img_path)
    return img_path

def test_image_upload():
    try:
        # Initialize headers
        headers = {
            'Authorization': f"Bearer {os.getenv('SUPABASE_KEY')}",
            'apikey': os.getenv('SUPABASE_KEY')
        }
        
        base_url = os.getenv('SUPABASE_URL')
        bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'photos')
        
        # Create a test image
        test_file_path = create_test_image()
        unique_filename = f"{uuid.uuid4()}.jpg"
        
        print(f"\nTesting image upload to bucket '{bucket_name}'...")
        print(f"File will be stored as: {unique_filename}")
        
        # Try to upload the file
        with open(test_file_path, 'rb') as f:
            files = {'file': (unique_filename, f, 'image/jpeg')}
            response = requests.post(
                f"{base_url}/storage/v1/object/{bucket_name}/{unique_filename}",
                headers=headers,
                files=files
            )
            
            print(f"Upload status code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("Upload successful!")
                # Get the public URL
                public_url = f"{base_url}/storage/v1/object/public/{bucket_name}/{unique_filename}"
                print(f"\nImage public URL: {public_url}")
            else:
                print("Upload failed.")
                
        # Clean up the test file
        os.remove(test_file_path)
            
    except Exception as e:
        print(f"Error during upload test: {str(e)}")

if __name__ == "__main__":
    test_image_upload()
