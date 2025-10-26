"""
Materials Project API Integration
Handles Materials Project API calls, caching, and data processing
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
from mp_api.client import MPRester
import json

from config import get_config
from supabase_db import get_supabase_manager

logger = logging.getLogger(__name__)

class MaterialsProjectAPI:
    """Handles Materials Project API integration"""
    
    def __init__(self):
        self.config = get_config()
        self.supabase_manager = get_supabase_manager()
        self.api_key = self.config.materials_project_api_key
        self.base_url = self.config.materials_project_base_url
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
        
    def _get_mp_client(self):
        """Get Materials Project client"""
        return MPRester(self.api_key)
    
    async def get_material_by_id(self, material_id: str) -> Optional[Dict[str, Any]]:
        """Get material data by ID, with caching"""
        try:
            # Check cache first
            cached_material = self.supabase_manager.get_material(material_id)
            if cached_material:
                logger.info(f"Material {material_id} found in cache")
                return cached_material
            
            # Fetch from Materials Project API
            logger.info(f"Fetching material {material_id} from Materials Project API")
            with self._get_mp_client() as mpr:
                # Get material summary
                docs = mpr.materials.summary.search(material_ids=[material_id])
                if not docs:
                    logger.warning(f"Material {material_id} not found in Materials Project")
                    return None
                
                doc = docs[0]
                
                # Get structure data
                structure = mpr.get_structure_by_material_id(material_id)
                
                # Prepare material data
                material_data = {
                    "material_id": material_id,
                    "formula": doc.formula_pretty,
                    "formula_pretty": doc.formula_pretty,
                    "space_group": doc.symmetry.symbol if hasattr(doc, 'symmetry') else None,
                    "lattice_params": {
                        "a": structure.lattice.a,
                        "b": structure.lattice.b,
                        "c": structure.lattice.c,
                        "alpha": structure.lattice.alpha,
                        "beta": structure.lattice.beta,
                        "gamma": structure.lattice.gamma
                    } if structure else None,
                    "density": str(doc.density) if hasattr(doc, 'density') else None,
                    "band_gap": str(doc.band_gap) if hasattr(doc, 'band_gap') else None,
                    "formation_energy": str(doc.formation_energy_per_atom) if hasattr(doc, 'formation_energy_per_atom') else None,
                    "structure_data": {
                        "sites": [
                            {
                                "species": str(site.specie),
                                "coords": site.frac_coords.tolist()
                            }
                            for site in structure.sites
                        ] if structure else []
                    },
                    "properties": {
                        "volume": str(doc.volume) if hasattr(doc, 'volume') else None,
                        "density": str(doc.density) if hasattr(doc, 'density') else None,
                        "band_gap": str(doc.band_gap) if hasattr(doc, 'band_gap') else None,
                        "formation_energy": str(doc.formation_energy_per_atom) if hasattr(doc, 'formation_energy_per_atom') else None,
                        "is_stable": doc.is_stable if hasattr(doc, 'is_stable') else None,
                        "is_metal": doc.is_metal if hasattr(doc, 'is_metal') else None,
                        "is_magnetic": doc.is_magnetic if hasattr(doc, 'is_magnetic') else None
                    },
                    "api_response": doc.dict()
                }
                
                # Store in cache
                self.supabase_manager.create_material(material_id, doc.formula_pretty, **material_data)
                logger.info(f"Material {material_id} cached successfully")
                
                return material_data
                
        except Exception as e:
            logger.error(f"Failed to get material {material_id}: {e}")
            return None
    
    async def search_materials_by_formula(self, formula: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search materials by formula"""
        try:
            logger.info(f"Searching materials with formula: {formula}")
            with self._get_mp_client() as mpr:
                docs = mpr.materials.summary.search(formula=formula, num_chunks=1, chunk_size=limit)
                
                materials = []
                for doc in docs:
                    material_data = {
                        "material_id": doc.material_id,
                        "formula": doc.formula_pretty,
                        "formula_pretty": doc.formula_pretty,
                        "space_group": doc.symmetry.symbol if hasattr(doc, 'symmetry') else None,
                        "density": str(doc.density) if hasattr(doc, 'density') else None,
                        "band_gap": str(doc.band_gap) if hasattr(doc, 'band_gap') else None,
                        "is_stable": doc.is_stable if hasattr(doc, 'is_stable') else None,
                        "is_metal": doc.is_metal if hasattr(doc, 'is_metal') else None
                    }
                    materials.append(material_data)
                
                logger.info(f"Found {len(materials)} materials for formula {formula}")
                return materials
                
        except Exception as e:
            logger.error(f"Failed to search materials by formula {formula}: {e}")
            return []
    
    async def get_material_properties(self, material_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed material properties"""
        try:
            material = await self.get_material_by_id(material_id)
            if not material:
                return None
            
            return {
                "material_id": material_id,
                "basic_properties": material.get("properties", {}),
                "structure": material.get("structure_data", {}),
                "lattice": material.get("lattice_params", {}),
                "crystal_info": {
                    "space_group": material.get("space_group"),
                    "formula": material.get("formula_pretty")
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get properties for material {material_id}: {e}")
            return None
    
    async def analyze_material_stability(self, material_id: str) -> Optional[Dict[str, Any]]:
        """Analyze material stability"""
        try:
            material = await self.get_material_by_id(material_id)
            if not material:
                return None
            
            properties = material.get("properties", {})
            
            analysis = {
                "material_id": material_id,
                "stability_analysis": {
                    "is_stable": properties.get("is_stable"),
                    "formation_energy": properties.get("formation_energy"),
                    "is_metal": properties.get("is_metal"),
                    "is_magnetic": properties.get("is_magnetic")
                },
                "recommendations": []
            }
            
            # Add recommendations based on properties
            if properties.get("is_stable"):
                analysis["recommendations"].append("Material is thermodynamically stable")
            else:
                analysis["recommendations"].append("Material may be metastable or unstable")
            
            if properties.get("is_metal"):
                analysis["recommendations"].append("Suitable for electrical applications")
            else:
                analysis["recommendations"].append("May be suitable for insulating applications")
            
            if properties.get("band_gap"):
                band_gap = float(properties["band_gap"])
                if band_gap < 1.0:
                    analysis["recommendations"].append("Small band gap - good conductor")
                elif band_gap > 3.0:
                    analysis["recommendations"].append("Large band gap - good insulator")
                else:
                    analysis["recommendations"].append("Medium band gap - semiconductor")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze stability for material {material_id}: {e}")
            return None
    
    async def suggest_applications(self, material_id: str) -> Optional[Dict[str, Any]]:
        """Suggest applications for the material"""
        try:
            material = await self.get_material_by_id(material_id)
            if not material:
                return None
            
            properties = material.get("properties", {})
            applications = []
            
            # Suggest applications based on properties
            if properties.get("is_metal"):
                applications.extend([
                    "Electrical wiring",
                    "Electronics components",
                    "Conductive coatings"
                ])
            
            if properties.get("is_magnetic"):
                applications.extend([
                    "Magnetic storage",
                    "Sensors",
                    "Motors and generators"
                ])
            
            band_gap = properties.get("band_gap")
            if band_gap:
                gap = float(band_gap)
                if gap < 1.0:
                    applications.extend([
                        "Solar cells",
                        "Photodetectors",
                        "LEDs"
                    ])
                elif gap > 3.0:
                    applications.extend([
                        "Insulating materials",
                        "Dielectric applications",
                        "Protective coatings"
                    ])
            
            if properties.get("is_stable"):
                applications.extend([
                    "Structural materials",
                    "Long-term applications",
                    "High-temperature environments"
                ])
            
            return {
                "material_id": material_id,
                "suggested_applications": list(set(applications)),  # Remove duplicates
                "confidence": "High" if len(applications) > 3 else "Medium"
            }
            
        except Exception as e:
            logger.error(f"Failed to suggest applications for material {material_id}: {e}")
            return None
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get Materials Project API status"""
        try:
            with self._get_mp_client() as mpr:
                # Test API with a simple query
                docs = mpr.materials.summary.search(material_ids=["mp-149"], num_chunks=1, chunk_size=1)
                
                return {
                    "status": "healthy",
                    "api_key": self.api_key[:10] + "...",
                    "base_url": self.base_url,
                    "last_test": datetime.utcnow().isoformat(),
                    "test_result": "success" if docs else "no_data"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_key": self.api_key[:10] + "...",
                "base_url": self.base_url,
                "last_test": datetime.utcnow().isoformat()
            }

# Global Materials Project API instance
materials_api = MaterialsProjectAPI()

def get_materials_api() -> MaterialsProjectAPI:
    """Get the global Materials Project API instance"""
    return materials_api