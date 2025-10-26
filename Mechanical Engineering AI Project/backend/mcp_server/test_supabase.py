"""
Test Supabase Connection
Verify that our Supabase database is working correctly
"""

import os
from supabase import create_client, Client
from config import get_config

def test_supabase_connection():
    """Test basic Supabase connection"""
    print("Testing Supabase Connection...")
    
    try:
        # Get configuration
        config = get_config()
        
        print(f"Supabase URL: {config.supabase_url}")
        print(f"Supabase Key: {config.supabase_key[:20]}...")
        
        # Create Supabase client
        supabase: Client = create_client(config.supabase_url, config.supabase_key)
        print("✅ Supabase client created successfully")
        
        # Test basic query - get agents
        print("\nTesting database query...")
        result = supabase.table("agents").select("*").execute()
        
        print(f"✅ Query successful! Found {len(result.data)} agents:")
        for agent in result.data:
            print(f"  - {agent['agent_id']} ({agent['agent_type']}) - {agent['status']}")
        
        # Test insert operation
        print("\nTesting insert operation...")
        test_agent = {
            "agent_id": "test-connection-001",
            "agent_type": "test",
            "capabilities": ["connection_test"],
            "version": "1.0.0",
            "status": "active"
        }
        
        insert_result = supabase.table("agents").insert(test_agent).execute()
        print("✅ Insert operation successful!")
        
        # Test update operation
        print("\nTesting update operation...")
        update_result = supabase.table("agents").update({
            "status": "inactive"
        }).eq("agent_id", "test-connection-001").execute()
        print("✅ Update operation successful!")
        
        # Test delete operation
        print("\nTesting delete operation...")
        delete_result = supabase.table("agents").delete().eq("agent_id", "test-connection-001").execute()
        print("✅ Delete operation successful!")
        
        print("\n🎉 All Supabase operations working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def test_materials_project_integration():
    """Test Materials Project API integration"""
    print("\n" + "="*50)
    print("Testing Materials Project API Integration...")
    
    try:
        from mp_api.client import MPRester
        
        # Test Materials Project API
        with MPRester(config.materials_project_api_key) as mpr:
            print("✅ Materials Project API connected")
            
            # Test material search
            docs = mpr.materials.summary.search(material_ids=["mp-149"])
            if docs:
                doc = docs[0]
                print(f"✅ Material found: {doc.material_id} - {doc.formula_pretty}")
                
                # Test storing in Supabase
                material_data = {
                    "material_id": doc.material_id,
                    "formula": doc.formula_pretty,
                    "formula_pretty": doc.formula_pretty,
                    "space_group": doc.symmetry.symbol if hasattr(doc, 'symmetry') else None,
                    "api_response": doc.dict()
                }
                
                result = supabase.table("materials").insert(material_data).execute()
                print("✅ Material stored in Supabase successfully!")
                
                return True
            else:
                print("❌ No materials found")
                return False
                
    except Exception as e:
        print(f"❌ Materials Project integration failed: {e}")
        return False

if __name__ == "__main__":
    print("Materials Project MCP Server - Supabase Connection Test")
    print("="*60)
    
    # Test Supabase connection
    supabase_success = test_supabase_connection()
    
    # Test Materials Project integration
    if supabase_success:
        materials_success = test_materials_project_integration()
        
        if materials_success:
            print("\n🎉 All tests passed! Supabase integration is working!")
        else:
            print("\n⚠️ Supabase works but Materials Project integration failed")
    else:
        print("\n❌ Supabase connection failed - check your credentials")
    
    print("\n" + "="*60)
    print("Test completed!")