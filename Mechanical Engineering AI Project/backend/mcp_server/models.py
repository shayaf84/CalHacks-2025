"""
Database Models for MCP Server
SQLAlchemy models for agent management, message persistence, and material caching
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json

Base = declarative_base()

class Agent(Base):
    """Agent registration and status tracking"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(100), unique=True, index=True, nullable=False)
    agent_type = Column(String(50), nullable=False)  # retrieval, analysis, simulation, synthesis
    capabilities = Column(JSON, nullable=True)  # List of capabilities
    version = Column(String(20), nullable=True)
    status = Column(String(20), default="active")  # active, inactive, error
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("Message", back_populates="agent")
    
    def __repr__(self):
        return f"<Agent(id={self.agent_id}, type={self.agent_type}, status={self.status})>"

class Message(Base):
    """MCP message history and tracking"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(100), unique=True, index=True, nullable=True)
    agent_id = Column(String(100), ForeignKey("agents.agent_id"), nullable=False)
    message_type = Column(String(50), nullable=False)  # handshake, broadcast, material_request, etc.
    content = Column(JSON, nullable=False)  # Full message content
    correlation_id = Column(String(100), nullable=True)  # For linking request/response
    status = Column(String(20), default="sent")  # sent, received, processed, error
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.message_id}, type={self.message_type}, agent={self.agent_id})>"

class Material(Base):
    """Cached material data from Materials Project API"""
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(String(100), unique=True, index=True, nullable=False)  # mp-149, etc.
    formula = Column(String(200), nullable=False)  # Si, SiO2, etc.
    formula_pretty = Column(String(200), nullable=True)  # Pretty formatted formula
    structure_data = Column(JSON, nullable=True)  # Crystal structure data
    properties = Column(JSON, nullable=True)  # Material properties
    space_group = Column(String(50), nullable=True)  # Space group symbol
    lattice_params = Column(JSON, nullable=True)  # Lattice parameters
    density = Column(String(50), nullable=True)  # Density
    band_gap = Column(String(50), nullable=True)  # Band gap
    formation_energy = Column(String(50), nullable=True)  # Formation energy
    api_response = Column(JSON, nullable=True)  # Full API response for debugging
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Material(id={self.material_id}, formula={self.formula})>"

class AnalysisResult(Base):
    """Stored analysis results from analysis agent"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(String(100), nullable=False, index=True)
    analysis_type = Column(String(50), nullable=False)  # properties, stability, applications
    analysis_data = Column(JSON, nullable=False)  # Analysis results
    parameters = Column(JSON, nullable=True)  # Analysis parameters used
    agent_id = Column(String(100), nullable=True)  # Which agent performed analysis
    status = Column(String(20), default="completed")  # completed, error, pending
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AnalysisResult(material={self.material_id}, type={self.analysis_type})>"

class SimulationResult(Base):
    """Stored simulation results from simulation agent"""
    __tablename__ = "simulation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(String(100), nullable=False, index=True)
    simulation_type = Column(String(50), nullable=False)  # degradation, stress, thermal
    simulation_data = Column(JSON, nullable=False)  # Simulation results
    parameters = Column(JSON, nullable=True)  # Simulation parameters used
    agent_id = Column(String(100), nullable=True)  # Which agent performed simulation
    status = Column(String(20), default="completed")  # completed, error, pending
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SimulationResult(material={self.material_id}, type={self.simulation_type})>"

class SynthesisResult(Base):
    """Stored synthesis results from synthesis agent"""
    __tablename__ = "synthesis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(String(100), nullable=False, index=True)
    synthesis_type = Column(String(50), nullable=False)  # natural_language, table, visual
    synthesized_output = Column(Text, nullable=False)  # Final synthesized output
    analysis_data = Column(JSON, nullable=True)  # Analysis data used
    simulation_data = Column(JSON, nullable=True)  # Simulation data used
    agent_id = Column(String(100), nullable=True)  # Which agent performed synthesis
    status = Column(String(20), default="completed")  # completed, error, pending
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SynthesisResult(material={self.material_id}, type={self.synthesis_type})>"

class WorkflowState(Base):
    """Track multi-agent workflow states"""
    __tablename__ = "workflow_states"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(100), unique=True, index=True, nullable=False)
    material_id = Column(String(100), nullable=False, index=True)
    current_step = Column(String(50), nullable=False)  # retrieval, analysis, simulation, synthesis
    status = Column(String(20), default="active")  # active, completed, error, paused
    steps_completed = Column(JSON, nullable=True)  # List of completed steps
    steps_pending = Column(JSON, nullable=True)  # List of pending steps
    results = Column(JSON, nullable=True)  # Accumulated results
    error_message = Column(Text, nullable=True)  # Error details if any
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<WorkflowState(id={self.workflow_id}, material={self.material_id}, step={self.current_step})>"

# Database utility functions
def create_tables(engine):
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def drop_tables(engine):
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)