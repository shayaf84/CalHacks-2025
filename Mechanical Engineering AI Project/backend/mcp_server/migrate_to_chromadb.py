"""
Data Migration Script: Supabase to ChromaDB
Migrates all data from Supabase PostgreSQL to ChromaDB vector database
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio

# Import our modules
from chromadb_manager import ChromaDBManager
from supabase_db import SupabaseManager
from materials_api import MaterialsProjectAPI

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataMigrationManager:
    """Manages migration from Supabase to ChromaDB"""
    
    def __init__(self):
        """Initialize migration manager"""
        self.chromadb_manager = ChromaDBManager()
        self.supabase_manager = SupabaseManager()
        self.materials_api = MaterialsProjectAPI()
        
        # Migration statistics
        self.stats = {
            'materials_migrated': 0,
            'analysis_results_migrated': 0,
            'synthesis_results_migrated': 0,
            'agent_memory_migrated': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        logger.info("Data Migration Manager initialized")
    
    async def migrate_all_data(self):
        """Migrate all data from Supabase to ChromaDB"""
        self.stats['start_time'] = datetime.now()
        logger.info("Starting data migration from Supabase to ChromaDB...")
        
        try:
            # Test connections
            await self._test_connections()
            
            # Migrate materials data
            await self._migrate_materials()
            
            # Migrate analysis results
            await self._migrate_analysis_results()
            
            # Migrate synthesis results
            await self._migrate_synthesis_results()
            
            # Migrate agent memory
            await self._migrate_agent_memory()
            
            # Verify migration
            await self._verify_migration()
            
            self.stats['end_time'] = datetime.now()
            self._print_migration_summary()
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self.stats['errors'] += 1
            raise
    
    async def _test_connections(self):
        """Test connections to both databases"""
        logger.info("Testing database connections...")
        
        # Test Supabase connection
        try:
            supabase_stats = self.supabase_manager.get_database_stats()
            logger.info(f"Supabase connection successful. Stats: {supabase_stats}")
        except Exception as e:
            logger.error(f"Supabase connection failed: {e}")
            raise
        
        # Test ChromaDB connection
        try:
            chromadb_stats = self.chromadb_manager.get_collection_stats()
            logger.info(f"ChromaDB connection successful. Stats: {chromadb_stats}")
        except Exception as e:
            logger.error(f"ChromaDB connection failed: {e}")
            raise
        
        logger.info("All database connections successful!")
    
    async def _migrate_materials(self):
        """Migrate materials data from Supabase to ChromaDB"""
        logger.info("Starting materials migration...")
        
        try:
            # Get all materials from Supabase
            materials = self.supabase_manager.get_all_materials()
            logger.info(f"Found {len(materials)} materials in Supabase")
            
            for material in materials:
                try:
                    # Convert Supabase material to ChromaDB format
                    material_data = self._convert_material_format(material)
                    
                    # Add to ChromaDB
                    success = self.chromadb_manager.add_material(
                        material['material_id'], 
                        material_data
                    )
                    
                    if success:
                        self.stats['materials_migrated'] += 1
                        logger.info(f"Migrated material: {material['material_id']}")
                    else:
                        logger.error(f"Failed to migrate material: {material['material_id']}")
                        self.stats['errors'] += 1
                        
                except Exception as e:
                    logger.error(f"Error migrating material {material.get('material_id', 'unknown')}: {e}")
                    self.stats['errors'] += 1
            
            logger.info(f"Materials migration completed. Migrated: {self.stats['materials_migrated']}")
            
        except Exception as e:
            logger.error(f"Materials migration failed: {e}")
            raise
    
    async def _migrate_analysis_results(self):
        """Migrate analysis results from Supabase to ChromaDB"""
        logger.info("Starting analysis results migration...")
        
        try:
            # Get all analysis results from Supabase
            analysis_results = self.supabase_manager.get_all_analysis_results()
            logger.info(f"Found {len(analysis_results)} analysis results in Supabase")
            
            for result in analysis_results:
                try:
                    # Convert Supabase result to ChromaDB format
                    analysis_data = self._convert_analysis_format(result)
                    
                    # Add to ChromaDB
                    success = self.chromadb_manager.add_analysis_result(
                        result['analysis_id'], 
                        analysis_data
                    )
                    
                    if success:
                        self.stats['analysis_results_migrated'] += 1
                        logger.info(f"Migrated analysis result: {result['analysis_id']}")
                    else:
                        logger.error(f"Failed to migrate analysis result: {result['analysis_id']}")
                        self.stats['errors'] += 1
                        
                except Exception as e:
                    logger.error(f"Error migrating analysis result {result.get('analysis_id', 'unknown')}: {e}")
                    self.stats['errors'] += 1
            
            logger.info(f"Analysis results migration completed. Migrated: {self.stats['analysis_results_migrated']}")
            
        except Exception as e:
            logger.error(f"Analysis results migration failed: {e}")
            raise
    
    async def _migrate_synthesis_results(self):
        """Migrate synthesis results from Supabase to ChromaDB"""
        logger.info("Starting synthesis results migration...")
        
        try:
            # Get all synthesis results from Supabase
            synthesis_results = self.supabase_manager.get_all_synthesis_results()
            logger.info(f"Found {len(synthesis_results)} synthesis results in Supabase")
            
            for result in synthesis_results:
                try:
                    # Convert Supabase result to ChromaDB format
                    synthesis_data = self._convert_synthesis_format(result)
                    
                    # Add to ChromaDB
                    success = self.chromadb_manager.add_synthesis_result(
                        result['synthesis_id'], 
                        synthesis_data
                    )
                    
                    if success:
                        self.stats['synthesis_results_migrated'] += 1
                        logger.info(f"Migrated synthesis result: {result['synthesis_id']}")
                    else:
                        logger.error(f"Failed to migrate synthesis result: {result['synthesis_id']}")
                        self.stats['errors'] += 1
                        
                except Exception as e:
                    logger.error(f"Error migrating synthesis result {result.get('synthesis_id', 'unknown')}: {e}")
                    self.stats['errors'] += 1
            
            logger.info(f"Synthesis results migration completed. Migrated: {self.stats['synthesis_results_migrated']}")
            
        except Exception as e:
            logger.error(f"Synthesis results migration failed: {e}")
            raise
    
    async def _migrate_agent_memory(self):
        """Migrate agent memory from Supabase to ChromaDB"""
        logger.info("Starting agent memory migration...")
        
        try:
            # Get all agent memory from Supabase
            agent_memory = self.supabase_manager.get_all_agent_memory()
            logger.info(f"Found {len(agent_memory)} agent memory entries in Supabase")
            
            for memory in agent_memory:
                try:
                    # Convert Supabase memory to ChromaDB format
                    memory_data = self._convert_memory_format(memory)
                    
                    # Add to ChromaDB
                    success = self.chromadb_manager.add_agent_memory(
                        memory['memory_id'], 
                        memory_data
                    )
                    
                    if success:
                        self.stats['agent_memory_migrated'] += 1
                        logger.info(f"Migrated agent memory: {memory['memory_id']}")
                    else:
                        logger.error(f"Failed to migrate agent memory: {memory['memory_id']}")
                        self.stats['errors'] += 1
                        
                except Exception as e:
                    logger.error(f"Error migrating agent memory {memory.get('memory_id', 'unknown')}: {e}")
                    self.stats['errors'] += 1
            
            logger.info(f"Agent memory migration completed. Migrated: {self.stats['agent_memory_migrated']}")
            
        except Exception as e:
            logger.error(f"Agent memory migration failed: {e}")
            raise
    
    def _convert_material_format(self, supabase_material: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Supabase material format to ChromaDB format"""
        return {
            'formula': supabase_material.get('formula', ''),
            'space_group': supabase_material.get('space_group', ''),
            'crystal_system': supabase_material.get('crystal_system', ''),
            'band_gap': supabase_material.get('band_gap', 0),
            'density': supabase_material.get('density', 0),
            'applications': supabase_material.get('applications', []),
            'created_at': supabase_material.get('created_at', datetime.now().isoformat()),
            'source': supabase_material.get('source', 'supabase_migration'),
            'properties': supabase_material.get('properties', {}),
            'structure_data': supabase_material.get('structure_data', {})
        }
    
    def _convert_analysis_format(self, supabase_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Supabase analysis format to ChromaDB format"""
        return {
            'material_id': supabase_analysis.get('material_id', ''),
            'analysis_type': supabase_analysis.get('analysis_type', ''),
            'agent_id': supabase_analysis.get('agent_id', ''),
            'description': supabase_analysis.get('description', ''),
            'results': supabase_analysis.get('results', {}),
            'created_at': supabase_analysis.get('created_at', datetime.now().isoformat()),
            'status': supabase_analysis.get('status', 'completed'),
            'parameters': supabase_analysis.get('parameters', {})
        }
    
    def _convert_synthesis_format(self, supabase_synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Supabase synthesis format to ChromaDB format"""
        return {
            'material_id': supabase_synthesis.get('material_id', ''),
            'method': supabase_synthesis.get('method', ''),
            'agent_id': supabase_synthesis.get('agent_id', ''),
            'description': supabase_synthesis.get('description', ''),
            'recommendations': supabase_synthesis.get('recommendations', {}),
            'created_at': supabase_synthesis.get('created_at', datetime.now().isoformat()),
            'success_rate': supabase_synthesis.get('success_rate', 0),
            'conditions': supabase_synthesis.get('conditions', {})
        }
    
    def _convert_memory_format(self, supabase_memory: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Supabase memory format to ChromaDB format"""
        return {
            'agent_id': supabase_memory.get('agent_id', ''),
            'memory_type': supabase_memory.get('memory_type', ''),
            'content': supabase_memory.get('content', ''),
            'created_at': supabase_memory.get('created_at', datetime.now().isoformat()),
            'importance': supabase_memory.get('importance', 0),
            'context': supabase_memory.get('context', {}),
            'tags': supabase_memory.get('tags', [])
        }
    
    async def _verify_migration(self):
        """Verify migration was successful"""
        logger.info("Verifying migration...")
        
        # Get final stats from both databases
        supabase_stats = self.supabase_manager.get_database_stats()
        chromadb_stats = self.chromadb_manager.get_collection_stats()
        
        logger.info(f"Supabase stats: {supabase_stats}")
        logger.info(f"ChromaDB stats: {chromadb_stats}")
        
        # Verify counts match
        verification_passed = True
        
        if supabase_stats.get('materials', 0) != chromadb_stats.get('materials', 0):
            logger.warning(f"Materials count mismatch: Supabase={supabase_stats.get('materials', 0)}, ChromaDB={chromadb_stats.get('materials', 0)}")
            verification_passed = False
        
        if supabase_stats.get('analysis_results', 0) != chromadb_stats.get('analysis_results', 0):
            logger.warning(f"Analysis results count mismatch: Supabase={supabase_stats.get('analysis_results', 0)}, ChromaDB={chromadb_stats.get('analysis_results', 0)}")
            verification_passed = False
        
        if supabase_stats.get('synthesis_results', 0) != chromadb_stats.get('synthesis_results', 0):
            logger.warning(f"Synthesis results count mismatch: Supabase={supabase_stats.get('synthesis_results', 0)}, ChromaDB={chromadb_stats.get('synthesis_results', 0)}")
            verification_passed = False
        
        if supabase_stats.get('agent_memory', 0) != chromadb_stats.get('agent_memory', 0):
            logger.warning(f"Agent memory count mismatch: Supabase={supabase_stats.get('agent_memory', 0)}, ChromaDB={chromadb_stats.get('agent_memory', 0)}")
            verification_passed = False
        
        if verification_passed:
            logger.info("✅ Migration verification passed!")
        else:
            logger.warning("⚠️ Migration verification found discrepancies")
    
    def _print_migration_summary(self):
        """Print migration summary"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Start Time: {self.stats['start_time']}")
        print(f"End Time: {self.stats['end_time']}")
        print(f"Duration: {duration}")
        print(f"Materials Migrated: {self.stats['materials_migrated']}")
        print(f"Analysis Results Migrated: {self.stats['analysis_results_migrated']}")
        print(f"Synthesis Results Migrated: {self.stats['synthesis_results_migrated']}")
        print(f"Agent Memory Migrated: {self.stats['agent_memory_migrated']}")
        print(f"Errors: {self.stats['errors']}")
        print("="*60)
        
        if self.stats['errors'] == 0:
            print("🎉 Migration completed successfully!")
        else:
            print(f"⚠️ Migration completed with {self.stats['errors']} errors")

async def main():
    """Main migration function"""
    print("Starting Supabase to ChromaDB Migration...")
    
    migration_manager = DataMigrationManager()
    
    try:
        await migration_manager.migrate_all_data()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Run the migration
    success = asyncio.run(main())
    
    if success:
        print("✅ Migration process completed!")
    else:
        print("❌ Migration process failed!")
        exit(1)