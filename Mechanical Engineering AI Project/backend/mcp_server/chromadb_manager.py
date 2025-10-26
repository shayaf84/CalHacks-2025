"""
ChromaDB Manager for Materials Project
Handles vector database operations for material properties and analysis results
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json
import numpy as np
from typing import List, Dict, Any, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDBManager:
    """Manages ChromaDB operations for materials data"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB client and collections"""
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize collections
        self._initialize_collections()
        
        logger.info("ChromaDB Manager initialized successfully")
    
    def _initialize_collections(self):
        """Create and initialize all required collections"""
        
        # Materials collection - stores material properties and structures
        self.materials_collection = self.client.get_or_create_collection(
            name="materials",
            metadata={"description": "Material properties and crystal structures"}
        )
        
        # Analysis results collection - stores analysis outputs
        self.analysis_collection = self.client.get_or_create_collection(
            name="analysis_results",
            metadata={"description": "Material analysis and simulation results"}
        )
        
        # Synthesis results collection - stores synthesis recommendations
        self.synthesis_collection = self.client.get_or_create_collection(
            name="synthesis_results",
            metadata={"description": "Material synthesis recommendations and methods"}
        )
        
        # Agent memory collection - stores agent interactions and learnings
        self.agent_memory_collection = self.client.get_or_create_collection(
            name="agent_memory",
            metadata={"description": "Agent interactions, learnings, and workflow states"}
        )
        
        logger.info("All collections initialized")
    
    def create_material_embedding(self, material_data: Dict[str, Any]) -> List[float]:
        """Create embedding for material data"""
        
        # Create text description from material properties
        description_parts = []
        
        if 'formula' in material_data:
            description_parts.append(f"Chemical formula: {material_data['formula']}")
        
        if 'space_group' in material_data:
            description_parts.append(f"Space group: {material_data['space_group']}")
        
        if 'crystal_system' in material_data:
            description_parts.append(f"Crystal system: {material_data['crystal_system']}")
        
        if 'band_gap' in material_data:
            description_parts.append(f"Band gap: {material_data['band_gap']} eV")
        
        if 'density' in material_data:
            description_parts.append(f"Density: {material_data['density']} g/cm³")
        
        if 'applications' in material_data:
            description_parts.append(f"Applications: {', '.join(material_data['applications'])}")
        
        # Combine into single text
        description = ". ".join(description_parts)
        
        # Generate embedding
        embedding = self.embedding_model.encode(description).tolist()
        
        return embedding
    
    def add_material(self, material_id: str, material_data: Dict[str, Any]) -> bool:
        """Add material to ChromaDB"""
        try:
            # Create embedding
            embedding = self.create_material_embedding(material_data)
            
            # Prepare metadata
            metadata = {
                "material_id": material_id,
                "formula": material_data.get('formula', ''),
                "space_group": material_data.get('space_group', ''),
                "crystal_system": material_data.get('crystal_system', ''),
                "band_gap": material_data.get('band_gap', 0),
                "density": material_data.get('density', 0),
                "created_at": material_data.get('created_at', ''),
                "source": material_data.get('source', 'materials_project')
            }
            
            # Add to collection
            self.materials_collection.add(
                ids=[material_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[json.dumps(material_data)]
            )
            
            logger.info(f"Material {material_id} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding material {material_id}: {e}")
            return False
    
    def search_similar_materials(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar materials using text query"""
        try:
            # Create embedding for query
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in materials collection
            results = self.materials_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['metadatas', 'documents', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    'material_id': results['ids'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'document': json.loads(results['documents'][0][i]),
                    'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching materials: {e}")
            return []
    
    def add_analysis_result(self, analysis_id: str, analysis_data: Dict[str, Any]) -> bool:
        """Add analysis result to ChromaDB"""
        try:
            # Create embedding from analysis description
            description = analysis_data.get('description', '')
            embedding = self.embedding_model.encode(description).tolist()
            
            # Prepare metadata
            metadata = {
                "analysis_id": analysis_id,
                "material_id": analysis_data.get('material_id', ''),
                "analysis_type": analysis_data.get('analysis_type', ''),
                "agent_id": analysis_data.get('agent_id', ''),
                "created_at": analysis_data.get('created_at', ''),
                "status": analysis_data.get('status', 'completed')
            }
            
            # Add to collection
            self.analysis_collection.add(
                ids=[analysis_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[json.dumps(analysis_data)]
            )
            
            logger.info(f"Analysis result {analysis_id} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding analysis result {analysis_id}: {e}")
            return False
    
    def add_synthesis_result(self, synthesis_id: str, synthesis_data: Dict[str, Any]) -> bool:
        """Add synthesis result to ChromaDB"""
        try:
            # Create embedding from synthesis description
            description = synthesis_data.get('description', '')
            embedding = self.embedding_model.encode(description).tolist()
            
            # Prepare metadata
            metadata = {
                "synthesis_id": synthesis_id,
                "material_id": synthesis_data.get('material_id', ''),
                "method": synthesis_data.get('method', ''),
                "agent_id": synthesis_data.get('agent_id', ''),
                "created_at": synthesis_data.get('created_at', ''),
                "success_rate": synthesis_data.get('success_rate', 0)
            }
            
            # Add to collection
            self.synthesis_collection.add(
                ids=[synthesis_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[json.dumps(synthesis_data)]
            )
            
            logger.info(f"Synthesis result {synthesis_id} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding synthesis result {synthesis_id}: {e}")
            return False
    
    def add_agent_memory(self, memory_id: str, memory_data: Dict[str, Any]) -> bool:
        """Add agent memory to ChromaDB"""
        try:
            # Create embedding from memory content
            content = memory_data.get('content', '')
            embedding = self.embedding_model.encode(content).tolist()
            
            # Prepare metadata
            metadata = {
                "memory_id": memory_id,
                "agent_id": memory_data.get('agent_id', ''),
                "memory_type": memory_data.get('memory_type', ''),
                "created_at": memory_data.get('created_at', ''),
                "importance": memory_data.get('importance', 0)
            }
            
            # Add to collection
            self.agent_memory_collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[json.dumps(memory_data)]
            )
            
            logger.info(f"Agent memory {memory_id} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding agent memory {memory_id}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics for all collections"""
        stats = {}
        
        try:
            stats['materials'] = self.materials_collection.count()
            stats['analysis_results'] = self.analysis_collection.count()
            stats['synthesis_results'] = self.synthesis_collection.count()
            stats['agent_memory'] = self.agent_memory_collection.count()
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            stats = {'error': str(e)}
        
        return stats
    
    def reset_database(self):
        """Reset all collections (for testing)"""
        try:
            self.client.reset()
            self._initialize_collections()
            logger.info("Database reset successfully")
        except Exception as e:
            logger.error(f"Error resetting database: {e}")

# Test function
def test_chromadb_manager():
    """Test ChromaDB manager functionality"""
    print("Testing ChromaDB Manager...")
    
    # Initialize manager
    db_manager = ChromaDBManager()
    
    # Test material data
    test_material = {
        'formula': 'Si',
        'space_group': 'Fd-3m',
        'crystal_system': 'cubic',
        'band_gap': 1.1,
        'density': 2.33,
        'applications': ['semiconductors', 'solar cells'],
        'created_at': '2024-01-01',
        'source': 'materials_project'
    }
    
    # Add test material
    success = db_manager.add_material("test-si-001", test_material)
    print(f"Material added: {success}")
    
    # Search for similar materials
    results = db_manager.search_similar_materials("silicon semiconductor", n_results=3)
    print(f"Search results: {len(results)} found")
    
    # Get stats
    stats = db_manager.get_collection_stats()
    print(f"Collection stats: {stats}")
    
    print("ChromaDB Manager test completed!")

if __name__ == "__main__":
    test_chromadb_manager()
