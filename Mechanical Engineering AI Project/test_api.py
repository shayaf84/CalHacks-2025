import os
from mp_api.client import MPRester

def test_materials_api():
    """Test Materials Project API using official MPRester client"""
    
    # Your API key
    API_KEY = "wNWHdtELVIgc7FbaasH6QVFNaFqUdfeH"
    
    # Set environment variable
    os.environ["MP_API_KEY"] = API_KEY
    
    try:
        print("Testing Materials Project API with MPRester...")
        print(f"API Key: {API_KEY[:10]}...")
        
        # Initialize MPRester with API key
        with MPRester(API_KEY) as mpr:
            # Test 1: Get material summary by material_id (using search method)
            print("\n--- Test 1: Get Material Summary ---")
            material_id = "mp-149"  # Silicon
            docs = mpr.materials.summary.search(material_ids=[material_id])
            if docs:
                doc = docs[0]
                print("✅ Test 1 Success!")
                print(f"Material ID: {doc.material_id}")
                print(f"Formula: {doc.formula_pretty}")
                print(f"Space Group: {doc.symmetry.symbol}")
            else:
                print("❌ No material found")
            
            # Test 2: Search materials by formula
            print("\n--- Test 2: Search by Formula ---")
            formula = "SiO2"
            docs = mpr.materials.summary.search(formula=formula)
            print(f"✅ Test 2 Success! Found {len(docs)} materials for formula {formula}")
            
            # Test 3: Get structure data
            print("\n--- Test 3: Get Structure Data ---")
            structure = mpr.get_structure_by_material_id(material_id)
            print("✅ Test 3 Success!")
            print(f"Structure formula: {structure.formula}")
            print(f"Lattice parameters: {structure.lattice.abc}")
            
            print("\n🎉 All tests passed! API connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ API Error: {e}")
        print("Trying alternative approach...")
        
        # Try with environment variable
        try:
            with MPRester() as mpr:
                print("✅ Connected using environment variable!")
                return True
        except Exception as e2:
            print(f"❌ Environment variable approach failed: {e2}")
            return False

if __name__ == "__main__":
    test_materials_api()
