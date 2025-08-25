#!/usr/bin/env python3
"""
Setup Supabase RLS Policies and Database Tables
This script creates all necessary tables and configures RLS policies
"""

import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv()

async def setup_supabase_policies():
    """Setup all Supabase tables and RLS policies"""
    
    print("=" * 60)
    print("SUPABASE POLICY SETUP")
    print("=" * 60)
    
    # Get credentials - use service key for admin operations
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not SUPABASE_SERVICE_KEY:
        print("\n❌ SUPABASE_SERVICE_KEY not found!")
        print("   This script requires the service role key for admin operations.")
        print("   Please add SUPABASE_SERVICE_KEY to your .env file")
        return False
    
    print(f"\n1. Connecting to Supabase...")
    print(f"   URL: {SUPABASE_URL}")
    
    try:
        # Create client with service role key
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("   ✅ Connected with service role key")
    except Exception as e:
        print(f"   ❌ Failed to connect: {e}")
        return False
    
    # SQL statements for creating tables
    create_tables_sql = """
    -- Create diagram_metadata table
    CREATE TABLE IF NOT EXISTS public.diagram_metadata (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        diagram_id TEXT NOT NULL UNIQUE,
        session_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        diagram_type TEXT NOT NULL,
        url TEXT,
        generation_method TEXT,
        request_params JSONB,
        metadata JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Create diagram_sessions table
    CREATE TABLE IF NOT EXISTS public.diagram_sessions (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        session_id TEXT NOT NULL UNIQUE,
        user_id TEXT NOT NULL,
        diagram_count INTEGER DEFAULT 0,
        last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        metadata JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_diagram_metadata_session_id ON public.diagram_metadata(session_id);
    CREATE INDEX IF NOT EXISTS idx_diagram_metadata_user_id ON public.diagram_metadata(user_id);
    CREATE INDEX IF NOT EXISTS idx_diagram_metadata_created_at ON public.diagram_metadata(created_at);
    CREATE INDEX IF NOT EXISTS idx_diagram_sessions_user_id ON public.diagram_sessions(user_id);
    CREATE INDEX IF NOT EXISTS idx_diagram_sessions_last_activity ON public.diagram_sessions(last_activity);
    """
    
    # Execute table creation
    print("\n2. Creating database tables...")
    try:
        # Using RPC to execute raw SQL
        result = supabase.rpc('exec_sql', {'query': create_tables_sql}).execute()
        print("   ✅ Tables created successfully")
    except Exception as e:
        # If RPC doesn't exist, try direct execution
        try:
            # Alternative approach using postgrest
            from postgrest import APIError
            # We'll create tables by checking if they exist first
            
            # Check if tables exist by trying to query them
            try:
                supabase.table('diagram_metadata').select('id').limit(1).execute()
                print("   ℹ️ Table 'diagram_metadata' already exists")
            except:
                print("   ⚠️ Cannot create tables via API - please run SQL in dashboard")
                
            try:
                supabase.table('diagram_sessions').select('id').limit(1).execute()
                print("   ℹ️ Table 'diagram_sessions' already exists")
            except:
                print("   ⚠️ Cannot create tables via API - please run SQL in dashboard")
                
        except Exception as e2:
            print(f"   ⚠️ Could not create tables automatically: {e}")
            print("   Please create tables manually in Supabase SQL Editor")
    
    # Enable RLS on tables
    enable_rls_sql = """
    -- Enable RLS on tables
    ALTER TABLE public.diagram_metadata ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.diagram_sessions ENABLE ROW LEVEL SECURITY;
    
    -- Also ensure storage.objects has RLS enabled
    ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;
    """
    
    print("\n3. Enabling Row Level Security...")
    try:
        supabase.rpc('exec_sql', {'query': enable_rls_sql}).execute()
        print("   ✅ RLS enabled on tables")
    except:
        print("   ⚠️ Please enable RLS manually in Supabase dashboard")
    
    # Create RLS policies for storage
    storage_policies_sql = """
    -- Drop existing policies if they exist
    DROP POLICY IF EXISTS "Allow anonymous uploads to diagrams" ON storage.objects;
    DROP POLICY IF EXISTS "Allow public read access to diagrams" ON storage.objects;
    DROP POLICY IF EXISTS "Allow anonymous updates to diagrams" ON storage.objects;
    DROP POLICY IF EXISTS "Allow anonymous deletes from diagrams" ON storage.objects;
    
    -- Create new policies for storage.objects
    CREATE POLICY "Allow anonymous uploads to diagrams" ON storage.objects
        FOR INSERT 
        TO anon
        WITH CHECK (bucket_id = 'diagrams');
    
    CREATE POLICY "Allow public read access to diagrams" ON storage.objects
        FOR SELECT
        TO anon, authenticated
        USING (bucket_id = 'diagrams');
    
    CREATE POLICY "Allow anonymous updates to diagrams" ON storage.objects
        FOR UPDATE
        TO anon
        USING (bucket_id = 'diagrams')
        WITH CHECK (bucket_id = 'diagrams');
    
    CREATE POLICY "Allow anonymous deletes from diagrams" ON storage.objects
        FOR DELETE
        TO anon
        USING (bucket_id = 'diagrams');
    """
    
    print("\n4. Creating storage RLS policies...")
    try:
        supabase.rpc('exec_sql', {'query': storage_policies_sql}).execute()
        print("   ✅ Storage policies created")
    except:
        print("   ⚠️ Please create storage policies manually")
    
    # Create RLS policies for diagram_metadata
    metadata_policies_sql = """
    -- Drop existing policies if they exist
    DROP POLICY IF EXISTS "Enable insert for anon users" ON public.diagram_metadata;
    DROP POLICY IF EXISTS "Enable select for anon users" ON public.diagram_metadata;
    DROP POLICY IF EXISTS "Enable update for anon users" ON public.diagram_metadata;
    DROP POLICY IF EXISTS "Enable delete for anon users" ON public.diagram_metadata;
    
    -- Create policies for diagram_metadata
    CREATE POLICY "Enable insert for anon users" ON public.diagram_metadata
        FOR INSERT 
        TO anon
        WITH CHECK (true);
    
    CREATE POLICY "Enable select for anon users" ON public.diagram_metadata
        FOR SELECT
        TO anon
        USING (true);
    
    CREATE POLICY "Enable update for anon users" ON public.diagram_metadata
        FOR UPDATE
        TO anon
        USING (true)
        WITH CHECK (true);
    
    CREATE POLICY "Enable delete for anon users" ON public.diagram_metadata
        FOR DELETE
        TO anon
        USING (true);
    """
    
    print("\n5. Creating diagram_metadata RLS policies...")
    try:
        supabase.rpc('exec_sql', {'query': metadata_policies_sql}).execute()
        print("   ✅ Metadata policies created")
    except:
        print("   ⚠️ Please create metadata policies manually")
    
    # Create RLS policies for diagram_sessions
    sessions_policies_sql = """
    -- Drop existing policies if they exist
    DROP POLICY IF EXISTS "Enable insert for anon users" ON public.diagram_sessions;
    DROP POLICY IF EXISTS "Enable select for anon users" ON public.diagram_sessions;
    DROP POLICY IF EXISTS "Enable update for anon users" ON public.diagram_sessions;
    DROP POLICY IF EXISTS "Enable delete for anon users" ON public.diagram_sessions;
    
    -- Create policies for diagram_sessions
    CREATE POLICY "Enable insert for anon users" ON public.diagram_sessions
        FOR INSERT
        TO anon
        WITH CHECK (true);
    
    CREATE POLICY "Enable select for anon users" ON public.diagram_sessions
        FOR SELECT
        TO anon
        USING (true);
    
    CREATE POLICY "Enable update for anon users" ON public.diagram_sessions
        FOR UPDATE
        TO anon
        USING (true)
        WITH CHECK (true);
    
    CREATE POLICY "Enable delete for anon users" ON public.diagram_sessions
        FOR DELETE
        TO anon
        USING (true);
    """
    
    print("\n6. Creating diagram_sessions RLS policies...")
    try:
        supabase.rpc('exec_sql', {'query': sessions_policies_sql}).execute()
        print("   ✅ Session policies created")
    except:
        print("   ⚠️ Please create session policies manually")
    
    # Test the setup
    print("\n7. Testing the configuration...")
    
    # Test 1: Try to insert a test record
    try:
        test_data = {
            'diagram_id': f'test-{os.urandom(8).hex()}',
            'session_id': 'test-session',
            'user_id': 'test-user',
            'diagram_type': 'test',
            'url': 'https://test.example.com/test.svg',
            'generation_method': 'test',
            'metadata': {'test': True}
        }
        
        result = supabase.table('diagram_metadata').insert(test_data).execute()
        print("   ✅ Test insert successful")
        
        # Clean up test data
        if result.data and len(result.data) > 0:
            test_id = result.data[0]['id']
            supabase.table('diagram_metadata').delete().eq('id', test_id).execute()
            print("   ✅ Test data cleaned up")
            
    except Exception as e:
        print(f"   ⚠️ Test insert failed: {e}")
        print("   This might be normal if tables don't exist yet")
    
    # Test 2: Try to upload a test file to storage
    try:
        test_svg = """<svg width="100" height="100">
            <circle cx="50" cy="50" r="40" fill="green"/>
            <text x="50" y="55" text-anchor="middle" fill="white">RLS TEST</text>
        </svg>"""
        
        test_filename = f"rls_test_{os.urandom(4).hex()}.svg"
        
        # Try upload with anon client
        anon_supabase = create_client(SUPABASE_URL, os.getenv('SUPABASE_ANON_KEY'))
        response = anon_supabase.storage.from_('diagrams').upload(
            test_filename,
            test_svg.encode('utf-8'),
            file_options={"content-type": "image/svg+xml", "upsert": "true"}
        )
        print("   ✅ Storage test successful with anon key")
        
        # Clean up test file
        anon_supabase.storage.from_('diagrams').remove([test_filename])
        print("   ✅ Test file cleaned up")
        
    except Exception as e:
        print(f"   ⚠️ Storage test failed: {e}")
        print("   You may need to apply policies manually in the dashboard")
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    
    print("""
Next Steps:
1. If any steps showed warnings, please complete them in Supabase dashboard
2. Go to: https://app.supabase.com
3. Navigate to SQL Editor and run the SQL commands shown above
4. After manual setup, run your tests again

To manually create everything, copy and run this SQL in Supabase SQL Editor:
""")
    
    # Print complete SQL for manual execution
    print("\n--- COPY BELOW TO SQL EDITOR ---\n")
    print(create_tables_sql)
    print(enable_rls_sql)
    print(storage_policies_sql)
    print(metadata_policies_sql)
    print(sessions_policies_sql)
    print("\n--- END OF SQL ---")
    
    return True

async def main():
    """Run the setup"""
    success = await setup_supabase_policies()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)