#!/usr/bin/env python3
"""
Setup Supabase storage bucket for diagrams
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_storage_bucket():
    """Create and configure the diagrams storage bucket"""
    
    print("=" * 60)
    print("SUPABASE BUCKET SETUP")
    print("=" * 60)
    
    # Get credentials - use service key for admin operations
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not SUPABASE_SERVICE_KEY:
        print("\n❌ SUPABASE_SERVICE_KEY not found in environment")
        print("   Using ANON key instead (may have limited permissions)")
        SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"\n1. Connecting to Supabase...")
    print(f"   URL: {SUPABASE_URL}")
    
    # Create client with service role key for admin operations
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("   ✅ Connected successfully")
    except Exception as e:
        print(f"   ❌ Failed to connect: {e}")
        return False
    
    # Check existing buckets
    print("\n2. Checking existing buckets...")
    try:
        buckets = supabase.storage.list_buckets()
        print(f"   Found {len(buckets)} existing bucket(s):")
        for bucket in buckets:
            print(f"   - {bucket.get('name')} (public: {bucket.get('public', False)})")
        
        # Check if diagrams bucket exists
        bucket_exists = any(b.get('name') == 'diagrams' for b in buckets)
        
        if bucket_exists:
            print("\n   ✅ 'diagrams' bucket already exists")
            return True
            
    except Exception as e:
        print(f"   ❌ Error listing buckets: {e}")
    
    # Create diagrams bucket
    print("\n3. Creating 'diagrams' bucket...")
    try:
        result = supabase.storage.create_bucket(
            'diagrams',
            options={
                'public': True,  # Make it public for easy access
                'file_size_limit': 10485760,  # 10MB limit
                'allowed_mime_types': ['image/svg+xml', 'image/png', 'image/jpeg']
            }
        )
        print("   ✅ Bucket 'diagrams' created successfully!")
        print(f"   Result: {result}")
        
    except Exception as e:
        error_str = str(e)
        if "already exists" in error_str.lower():
            print("   ℹ️ Bucket already exists")
        else:
            print(f"   ❌ Failed to create bucket: {e}")
            return False
    
    # Test upload to bucket
    print("\n4. Testing file upload...")
    try:
        test_svg = """<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="200" fill="#4CAF50"/>
            <text x="100" y="100" text-anchor="middle" fill="white" font-size="24">
                SUPABASE TEST
            </text>
        </svg>"""
        
        test_filename = "test_setup.svg"
        
        # Upload test file
        response = supabase.storage.from_('diagrams').upload(
            test_filename,
            test_svg.encode('utf-8'),
            file_options={"content-type": "image/svg+xml", "upsert": "true"}
        )
        
        print(f"   ✅ Test file uploaded successfully!")
        
        # Get public URL
        public_url = supabase.storage.from_('diagrams').get_public_url(test_filename)
        print(f"   Public URL: {public_url}")
        
    except Exception as e:
        print(f"   ❌ Upload test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ BUCKET SETUP COMPLETE!")
    print("=" * 60)
    print("\nYour Supabase storage is ready for diagram storage.")
    print(f"Bucket name: diagrams")
    print(f"Access: Public")
    print(f"Test file URL: {public_url if 'public_url' in locals() else 'N/A'}")
    
    return True

if __name__ == "__main__":
    setup_storage_bucket()