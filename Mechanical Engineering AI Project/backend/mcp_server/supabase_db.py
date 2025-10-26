"""
Supabase Database Manager
Handles database operations using Supabase PostgreSQL
"""

from supabase import create_client, Client
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from config import get_config

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Manages Supabase database operations"""
    
    def __init__(self):
        self.config = get_config()
        self.supabase: Client = None
        self._initialize_supabase()
    
    def _initialize_supabase(self):
        """Initialize Supabase client"""
        try:
            if self.config.supabase_url and self.config.supabase_key:
                self.supabase = create_client(
                    self.config.supabase_url,
                    self.config.supabase_key
                )
                logger.info("Supabase client initialized successfully")
            else:
                logger.warning("Supabase credentials not found, using fallback")
                self.supabase = None
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            self.supabase = None
    
    def is_connected(self) -> bool:
        """Check if Supabase is connected"""
        return self.supabase is not None
    
    # Agent CRUD Operations
    def create_agent(self, agent_id: str, agent_type: str, capabilities: List[str] = None, version: str = None) -> Dict[str, Any]:
        """Create a new agent record"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            agent_data = {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "capabilities": capabilities or [],
                "version": version,
                "status": "active",
                "connected_at": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("agents").insert(agent_data).execute()
            logger.info(f"Created agent: {agent_id} ({agent_type})")
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Failed to create agent {agent_id}: {e}")
            raise
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            result = self.supabase.table("agents").select("*").eq("agent_id", agent_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
            raise
    
    def update_agent_status(self, agent_id: str, status: str):
        """Update agent status"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            result = self.supabase.table("agents").update({
                "status": status,
                "last_seen": datetime.utcnow().isoformat()
            }).eq("agent_id", agent_id).execute()
            
            logger.info(f"Updated agent {agent_id} status to {status}")
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id} status: {e}")
            raise
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all agents"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            result = self.supabase.table("agents").select("*").execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get all agents: {e}")
            raise
    
    def delete_agent(self, agent_id: str):
        """Delete agent"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            result = self.supabase.table("agents").delete().eq("agent_id", agent_id).execute()
            logger.info(f"Deleted agent: {agent_id}")
        except Exception as e:
            logger.error(f"Failed to delete agent {agent_id}: {e}")
            raise
    
    # Message CRUD Operations
    def create_message(self, agent_id: str, message_type: str, content: Dict[str, Any], 
                      message_id: str = None, correlation_id: str = None) -> Dict[str, Any]:
        """Create a new message record"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            message_data = {
                "message_id": message_id,
                "agent_id": agent_id,
                "message_type": message_type,
                "content": content,
                "correlation_id": correlation_id,
                "status": "sent",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("messages").insert(message_data).execute()
            logger.info(f"Created message: {message_type} from {agent_id}")
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Failed to create message: {e}")
            raise
    
    def get_messages_by_agent(self, agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages by agent ID"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            result = self.supabase.table("messages").select("*").eq(
                "agent_id", agent_id
            ).order("timestamp", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get messages for agent {agent_id}: {e}")
            raise
    
    def get_messages_by_correlation(self, correlation_id: str) -> List[Dict[str, Any]]:
        """Get messages by correlation ID"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            result = self.supabase.table("messages").select("*").eq(
                "correlation_id", correlation_id
            ).order("timestamp", desc=False).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get messages by correlation {correlation_id}: {e}")
            raise
    
    # Material CRUD Operations
    def create_material(self, material_id: str, formula: str, **kwargs) -> Dict[str, Any]:
        """Create a new material record"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            material_data = {
                "material_id": material_id,
                "formula": formula,
                **kwargs
            }
            
            result = self.supabase.table("materials").insert(material_data).execute()
            logger.info(f"Created material: {material_id} ({formula})")
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Failed to create material {material_id}: {e}")
            raise
    
    def get_material(self, material_id: str) -> Optional[Dict[str, Any]]:
        """Get material by ID"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            result = self.supabase.table("materials").select("*").eq("material_id", material_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get material {material_id}: {e}")
            raise
    
    def search_materials_by_formula(self, formula: str) -> List[Dict[str, Any]]:
        """Search materials by formula"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            result = self.supabase.table("materials").select("*").ilike("formula", f"%{formula}%").execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to search materials by formula {formula}: {e}")
            raise
    
    # Workflow State Operations
    def create_workflow_state(self, workflow_id: str, material_id: str, current_step: str) -> Dict[str, Any]:
        """Create a new workflow state"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            workflow_data = {
                "workflow_id": workflow_id,
                "material_id": material_id,
                "current_step": current_step,
                "status": "active",
                "steps_completed": [],
                "steps_pending": ["retrieval", "analysis", "simulation", "synthesis"]
            }
            
            result = self.supabase.table("workflow_states").insert(workflow_data).execute()
            logger.info(f"Created workflow: {workflow_id} for material {material_id}")
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Failed to create workflow {workflow_id}: {e}")
            raise
    
    def update_workflow_step(self, workflow_id: str, current_step: str, completed_steps: List[str] = None):
        """Update workflow current step"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            update_data = {
                "current_step": current_step
            }
            if completed_steps:
                update_data["steps_completed"] = completed_steps
            
            result = self.supabase.table("workflow_states").update(update_data).eq(
                "workflow_id", workflow_id
            ).execute()
            
            logger.info(f"Updated workflow {workflow_id} to step {current_step}")
        except Exception as e:
            logger.error(f"Failed to update workflow {workflow_id}: {e}")
            raise
    
    def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow state by ID"""
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            result = self.supabase.table("workflow_states").select("*").eq("workflow_id", workflow_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get workflow {workflow_id}: {e}")
            raise
    
    # Database Health Check
    def health_check(self) -> Dict[str, Any]:
        """Check Supabase connection health"""
        try:
            if not self.is_connected():
                return {
                    "status": "unhealthy",
                    "error": "Supabase not connected",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test basic query
            result = self.supabase.table("agents").select("count").execute()
            
            return {
                "status": "healthy",
                "database_type": "supabase_postgresql",
                "supabase_url": self.config.supabase_url,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Global Supabase manager instance
supabase_manager = SupabaseManager()

def get_supabase_manager() -> SupabaseManager:
    """Get the global Supabase manager instance"""
    return supabase_manager