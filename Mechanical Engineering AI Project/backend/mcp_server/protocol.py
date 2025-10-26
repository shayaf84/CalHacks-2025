"""
MCP Protocol Definitions
Defines the communication protocol between agents and the MCP server
"""

from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json
from datetime import datetime

class MessageType(str, Enum):
    """Types of messages in the MCP protocol"""
    HANDSHAKE = "handshake"
    HANDSHAKE_ACK = "handshake_ack"
    BROADCAST = "broadcast"
    DIRECT = "direct"
    ECHO = "echo"
    ERROR = "error"
    MATERIAL_REQUEST = "material_request"
    MATERIAL_RESPONSE = "material_response"
    ANALYSIS_REQUEST = "analysis_request"
    ANALYSIS_RESPONSE = "analysis_response"
    SIMULATION_REQUEST = "simulation_request"
    SIMULATION_RESPONSE = "simulation_response"
    SYNTHESIS_REQUEST = "synthesis_request"
    SYNTHESIS_RESPONSE = "synthesis_response"

class AgentType(str, Enum):
    """Types of agents in the system"""
    RETRIEVAL = "retrieval"
    ANALYSIS = "analysis"
    SIMULATION = "simulation"
    SYNTHESIS = "synthesis"
    COORDINATOR = "coordinator"

class BaseMessage(BaseModel):
    """Base message structure for all MCP communications"""
    type: MessageType
    timestamp: datetime = datetime.now()
    message_id: Optional[str] = None
    correlation_id: Optional[str] = None

class HandshakeMessage(BaseMessage):
    """Handshake message when agent connects"""
    type: MessageType = MessageType.HANDSHAKE
    agent_id: str
    agent_type: AgentType
    capabilities: List[str] = []
    version: str = "1.0.0"

class HandshakeAckMessage(BaseMessage):
    """Acknowledgement of handshake"""
    type: MessageType = MessageType.HANDSHAKE_ACK
    status: str
    agent_id: str
    server_capabilities: List[str] = []

class BroadcastMessage(BaseMessage):
    """Broadcast message to all agents"""
    type: MessageType = MessageType.BROADCAST
    content: Dict[str, Any]
    priority: str = "normal"  # normal, high, urgent

class DirectMessage(BaseMessage):
    """Direct message to specific agent"""
    type: MessageType = MessageType.DIRECT
    target_agent: str
    content: Dict[str, Any]
    priority: str = "normal"

class MaterialRequestMessage(BaseMessage):
    """Request for material data"""
    type: MessageType = MessageType.MATERIAL_REQUEST
    material_id: Optional[str] = None
    formula: Optional[str] = None
    properties: List[str] = []
    requester_agent: str

class MaterialResponseMessage(BaseMessage):
    """Response with material data"""
    type: MessageType = MessageType.MATERIAL_RESPONSE
    material_data: Dict[str, Any]
    status: str  # success, error, partial
    error_message: Optional[str] = None

class AnalysisRequestMessage(BaseMessage):
    """Request for material analysis"""
    type: MessageType = MessageType.ANALYSIS_REQUEST
    material_id: str
    analysis_type: str  # properties, stability, applications, etc.
    parameters: Dict[str, Any] = {}
    requester_agent: str

class AnalysisResponseMessage(BaseMessage):
    """Response with analysis results"""
    type: MessageType = MessageType.ANALYSIS_RESPONSE
    material_id: str
    analysis_results: Dict[str, Any]
    status: str
    error_message: Optional[str] = None

class SimulationRequestMessage(BaseMessage):
    """Request for material simulation"""
    type: MessageType = MessageType.SIMULATION_REQUEST
    material_id: str
    simulation_type: str  # degradation, stress, thermal, etc.
    parameters: Dict[str, Any] = {}
    requester_agent: str

class SimulationResponseMessage(BaseMessage):
    """Response with simulation results"""
    type: MessageType = MessageType.SIMULATION_RESPONSE
    material_id: str
    simulation_results: Dict[str, Any]
    status: str
    error_message: Optional[str] = None

class SynthesisRequestMessage(BaseMessage):
    """Request for result synthesis"""
    type: MessageType = MessageType.SYNTHESIS_REQUEST
    material_id: str
    analysis_data: Dict[str, Any]
    simulation_data: Dict[str, Any]
    output_format: str  # natural_language, table, visual
    requester_agent: str

class SynthesisResponseMessage(BaseMessage):
    """Response with synthesized results"""
    type: MessageType = MessageType.SYNTHESIS_RESPONSE
    material_id: str
    synthesized_output: str
    output_format: str
    status: str
    error_message: Optional[str] = None

class ErrorMessage(BaseMessage):
    """Error message"""
    type: MessageType = MessageType.ERROR
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None

# Union type for all possible messages
MCPMessage = Union[
    HandshakeMessage,
    HandshakeAckMessage,
    BroadcastMessage,
    DirectMessage,
    MaterialRequestMessage,
    MaterialResponseMessage,
    AnalysisRequestMessage,
    AnalysisResponseMessage,
    SimulationRequestMessage,
    SimulationResponseMessage,
    SynthesisRequestMessage,
    SynthesisResponseMessage,
    ErrorMessage
]

def parse_message(message_str: str) -> MCPMessage:
    """Parse JSON string into appropriate MCP message type"""
    try:
        data = json.loads(message_str)
        message_type = data.get("type")
        
        # Map message types to classes
        message_classes = {
            MessageType.HANDSHAKE: HandshakeMessage,
            MessageType.HANDSHAKE_ACK: HandshakeAckMessage,
            MessageType.BROADCAST: BroadcastMessage,
            MessageType.DIRECT: DirectMessage,
            MessageType.MATERIAL_REQUEST: MaterialRequestMessage,
            MessageType.MATERIAL_RESPONSE: MaterialResponseMessage,
            MessageType.ANALYSIS_REQUEST: AnalysisRequestMessage,
            MessageType.ANALYSIS_RESPONSE: AnalysisResponseMessage,
            MessageType.SIMULATION_REQUEST: SimulationRequestMessage,
            MessageType.SIMULATION_RESPONSE: SimulationResponseMessage,
            MessageType.SYNTHESIS_REQUEST: SynthesisRequestMessage,
            MessageType.SYNTHESIS_RESPONSE: SynthesisResponseMessage,
            MessageType.ERROR: ErrorMessage
        }
        
        if message_type in message_classes:
            return message_classes[message_type](**data)
        else:
            raise ValueError(f"Unknown message type: {message_type}")
            
    except Exception as e:
        raise ValueError(f"Failed to parse message: {e}")

def create_error_message(error_code: str, error_message: str, details: Dict[str, Any] = None) -> ErrorMessage:
    """Create an error message"""
    return ErrorMessage(
        error_code=error_code,
        error_message=error_message,
        details=details
    )