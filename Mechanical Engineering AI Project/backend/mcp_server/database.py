"""
Database Connection and Session Management
Handles database connections, sessions, and CRUD operations for MCP Server
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

from models import Base, Agent, Message, Material, AnalysisResult, SimulationResult, SynthesisResult, WorkflowState
from config import get_config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.config = get_config()
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and session factory"""
        try:
            # Create database engine
            self.engine = create_engine(
                self.config.database_url,
                echo=self.config.database_echo,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close a database session"""
        session.close()
    
    # Agent CRUD Operations
    def create_agent(self, agent_id: str, agent_type: str, capabilities: List[str] = None, version: str = None) -> Agent:
        """Create a new agent record"""
        session = self.get_session()
        try:
            agent = Agent(
                agent_id=agent_id,
                agent_type=agent_type,
                capabilities=capabilities or [],
                version=version,
                status="active",
                connected_at=datetime.utcnow(),
                last_seen=datetime.utcnow()
            )
            session.add(agent)
            session.commit()
            session.refresh(agent)
            logger.info(f"Created agent: {agent_id} ({agent_type})")
            return agent
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to create agent {agent_id}: {e}")
            raise
        finally:
            self.close_session(session)
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        session = self.get_session()
        try:
            return session.query(Agent).filter(Agent.agent_id == agent_id).first()
        finally:
            self.close_session(session)
    
    def update_agent_status(self, agent_id: str, status: str):
        """Update agent status"""
        session = self.get_session()
        try:
            agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
            if agent:
                agent.status = status
                agent.last_seen = datetime.utcnow()
                agent.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Updated agent {agent_id} status to {status}")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to update agent {agent_id} status: {e}")
            raise
        finally:
            self.close_session(session)
    
    def get_all_agents(self) -> List[Agent]:
        """Get all agents"""
        session = self.get_session()
        try:
            return session.query(Agent).all()
        finally:
            self.close_session(session)
    
    def delete_agent(self, agent_id: str):
        """Delete agent"""
        session = self.get_session()
        try:
            agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
            if agent:
                session.delete(agent)
                session.commit()
                logger.info(f"Deleted agent: {agent_id}")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to delete agent {agent_id}: {e}")
            raise
        finally:
            self.close_session(session)
    
    # Message CRUD Operations
    def create_message(self, agent_id: str, message_type: str, content: Dict[str, Any], 
                      message_id: str = None, correlation_id: str = None) -> Message:
        """Create a new message record"""
        session = self.get_session()
        try:
            message = Message(
                message_id=message_id,
                agent_id=agent_id,
                message_type=message_type,
                content=content,
                correlation_id=correlation_id,
                status="sent",
                timestamp=datetime.utcnow()
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            logger.info(f"Created message: {message_type} from {agent_id}")
            return message
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to create message: {e}")
            raise
        finally:
            self.close_session(session)
    
    def get_messages_by_agent(self, agent_id: str, limit: int = 100) -> List[Message]:
        """Get messages by agent ID"""
        session = self.get_session()
        try:
            return session.query(Message).filter(
                Message.agent_id == agent_id
            ).order_by(Message.timestamp.desc()).limit(limit).all()
        finally:
            self.close_session(session)
    
    def get_messages_by_correlation(self, correlation_id: str) -> List[Message]:
        """Get messages by correlation ID"""
        session = self.get_session()
        try:
            return session.query(Message).filter(
                Message.correlation_id == correlation_id
            ).order_by(Message.timestamp.asc()).all()
        finally:
            self.close_session(session)
    
    # Material CRUD Operations
    def create_material(self, material_id: str, formula: str, **kwargs) -> Material:
        """Create a new material record"""
        session = self.get_session()
        try:
            material = Material(
                material_id=material_id,
                formula=formula,
                **kwargs
            )
            session.add(material)
            session.commit()
            session.refresh(material)
            logger.info(f"Created material: {material_id} ({formula})")
            return material
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to create material {material_id}: {e}")
            raise
        finally:
            self.close_session(session)
    
    def get_material(self, material_id: str) -> Optional[Material]:
        """Get material by ID"""
        session = self.get_session()
        try:
            return session.query(Material).filter(Material.material_id == material_id).first()
        finally:
            self.close_session(session)
    
    def search_materials_by_formula(self, formula: str) -> List[Material]:
        """Search materials by formula"""
        session = self.get_session()
        try:
            return session.query(Material).filter(
                Material.formula.ilike(f"%{formula}%")
            ).all()
        finally:
            self.close_session(session)
    
    # Workflow State Operations
    def create_workflow_state(self, workflow_id: str, material_id: str, current_step: str) -> WorkflowState:
        """Create a new workflow state"""
        session = self.get_session()
        try:
            workflow = WorkflowState(
                workflow_id=workflow_id,
                material_id=material_id,
                current_step=current_step,
                status="active",
                steps_completed=[],
                steps_pending=["retrieval", "analysis", "simulation", "synthesis"]
            )
            session.add(workflow)
            session.commit()
            session.refresh(workflow)
            logger.info(f"Created workflow: {workflow_id} for material {material_id}")
            return workflow
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to create workflow {workflow_id}: {e}")
            raise
        finally:
            self.close_session(session)
    
    def update_workflow_step(self, workflow_id: str, current_step: str, completed_steps: List[str] = None):
        """Update workflow current step"""
        session = self.get_session()
        try:
            workflow = session.query(WorkflowState).filter(
                WorkflowState.workflow_id == workflow_id
            ).first()
            if workflow:
                workflow.current_step = current_step
                if completed_steps:
                    workflow.steps_completed = completed_steps
                workflow.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Updated workflow {workflow_id} to step {current_step}")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to update workflow {workflow_id}: {e}")
            raise
        finally:
            self.close_session(session)
    
    def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow state by ID"""
        session = self.get_session()
        try:
            return session.query(WorkflowState).filter(
                WorkflowState.workflow_id == workflow_id
            ).first()
        finally:
            self.close_session(session)
    
    # Database Health Check
    def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            session = self.get_session()
            # Test basic query
            result = session.execute(text("SELECT 1")).fetchone()
            self.close_session(session)
            
            return {
                "status": "healthy",
                "database_url": self.config.database_url,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager