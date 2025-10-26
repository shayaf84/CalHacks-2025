"""
MCP Communication Handler
Handles message processing and routing between agents
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from protocol import (
    MCPMessage, MessageType, AgentType,
    parse_message, create_error_message,
    HandshakeMessage, HandshakeAckMessage,
    BroadcastMessage, DirectMessage,
    MaterialRequestMessage, MaterialResponseMessage,
    AnalysisRequestMessage, AnalysisResponseMessage,
    SimulationRequestMessage, SimulationResponseMessage,
    SynthesisRequestMessage, SynthesisResponseMessage,
    ErrorMessage
)

logger = logging.getLogger(__name__)

class MCPCommunicationHandler:
    """Handles MCP protocol communication between agents"""
    
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}  # agent_id -> agent_info
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[Dict[str, Any]] = []
        
    async def handle_message(self, websocket, agent_id: str, message_str: str) -> Optional[str]:
        """Handle incoming message from agent"""
        try:
            # Parse message
            message = parse_message(message_str)
            logger.info(f"Handling message from {agent_id}: {message.type}")
            
            # Add to history
            self.message_history.append({
                "timestamp": datetime.now(),
                "agent_id": agent_id,
                "message_type": message.type,
                "message": message.dict()
            })
            
            # Route message based on type
            response = await self._route_message(websocket, agent_id, message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling message from {agent_id}: {e}")
            error_msg = create_error_message(
                "PARSE_ERROR",
                f"Failed to process message: {str(e)}"
            )
            return error_msg.json()
    
    async def _route_message(self, websocket, agent_id: str, message: MCPMessage) -> Optional[str]:
        """Route message to appropriate handler"""
        
        if message.type == MessageType.HANDSHAKE:
            return await self._handle_handshake(websocket, agent_id, message)
        
        elif message.type == MessageType.BROADCAST:
            return await self._handle_broadcast(websocket, agent_id, message)
        
        elif message.type == MessageType.DIRECT:
            return await self._handle_direct(websocket, agent_id, message)
        
        elif message.type == MessageType.MATERIAL_REQUEST:
            return await self._handle_material_request(websocket, agent_id, message)
        
        elif message.type == MessageType.ANALYSIS_REQUEST:
            return await self._handle_analysis_request(websocket, agent_id, message)
        
        elif message.type == MessageType.SIMULATION_REQUEST:
            return await self._handle_simulation_request(websocket, agent_id, message)
        
        elif message.type == MessageType.SYNTHESIS_REQUEST:
            return await self._handle_synthesis_request(websocket, agent_id, message)
        
        else:
            # Echo back for unknown message types
            return json.dumps({
                "type": "echo",
                "original_message": message.dict()
            })
    
    async def _handle_handshake(self, websocket, agent_id: str, message: HandshakeMessage) -> str:
        """Handle agent handshake"""
        # Register agent
        self.agents[agent_id] = {
            "agent_type": message.agent_type,
            "capabilities": message.capabilities,
            "version": message.version,
            "connected_at": datetime.now(),
            "websocket": websocket
        }
        
        logger.info(f"Agent {agent_id} ({message.agent_type}) registered with capabilities: {message.capabilities}")
        
        # Send handshake acknowledgement
        ack_message = HandshakeAckMessage(
            status="success",
            agent_id=agent_id,
            server_capabilities=["material_retrieval", "analysis", "simulation", "synthesis"]
        )
        
        return ack_message.json()
    
    async def _handle_broadcast(self, websocket, agent_id: str, message: BroadcastMessage) -> str:
        """Handle broadcast message"""
        # Forward to all other agents
        for other_agent_id, agent_info in self.agents.items():
            if other_agent_id != agent_id and "websocket" in agent_info:
                try:
                    await agent_info["websocket"].send_text(message.json())
                except Exception as e:
                    logger.error(f"Failed to send broadcast to {other_agent_id}: {e}")
        
        return json.dumps({"type": "broadcast_sent", "status": "success"})
    
    async def _handle_direct(self, websocket, agent_id: str, message: DirectMessage) -> str:
        """Handle direct message to specific agent"""
        target_agent = self.agents.get(message.target_agent)
        
        if not target_agent:
            error_msg = create_error_message(
                "AGENT_NOT_FOUND",
                f"Target agent {message.target_agent} not found"
            )
            return error_msg.json()
        
        try:
            await target_agent["websocket"].send_text(message.json())
            return json.dumps({"type": "direct_sent", "status": "success"})
        except Exception as e:
            error_msg = create_error_message(
                "SEND_FAILED",
                f"Failed to send message to {message.target_agent}: {str(e)}"
            )
            return error_msg.json()
    
    async def _handle_material_request(self, websocket, agent_id: str, message: MaterialRequestMessage) -> str:
        """Handle material data request"""
        # Find retrieval agent
        retrieval_agent = None
        for agent_id_check, agent_info in self.agents.items():
            if agent_info.get("agent_type") == AgentType.RETRIEVAL:
                retrieval_agent = agent_info
                break
        
        if not retrieval_agent:
            error_msg = create_error_message(
                "NO_RETRIEVAL_AGENT",
                "No retrieval agent available to handle material request"
            )
            return error_msg.json()
        
        try:
            # Forward request to retrieval agent
            await retrieval_agent["websocket"].send_text(message.json())
            return json.dumps({"type": "request_forwarded", "status": "success"})
        except Exception as e:
            error_msg = create_error_message(
                "FORWARD_FAILED",
                f"Failed to forward material request: {str(e)}"
            )
            return error_msg.json()
    
    async def _handle_analysis_request(self, websocket, agent_id: str, message: AnalysisRequestMessage) -> str:
        """Handle analysis request"""
        # Find analysis agent
        analysis_agent = None
        for agent_id_check, agent_info in self.agents.items():
            if agent_info.get("agent_type") == AgentType.ANALYSIS:
                analysis_agent = agent_info
                break
        
        if not analysis_agent:
            error_msg = create_error_message(
                "NO_ANALYSIS_AGENT",
                "No analysis agent available to handle analysis request"
            )
            return error_msg.json()
        
        try:
            await analysis_agent["websocket"].send_text(message.json())
            return json.dumps({"type": "request_forwarded", "status": "success"})
        except Exception as e:
            error_msg = create_error_message(
                "FORWARD_FAILED",
                f"Failed to forward analysis request: {str(e)}"
            )
            return error_msg.json()
    
    async def _handle_simulation_request(self, websocket, agent_id: str, message: SimulationRequestMessage) -> str:
        """Handle simulation request"""
        # Find simulation agent
        simulation_agent = None
        for agent_id_check, agent_info in self.agents.items():
            if agent_info.get("agent_type") == AgentType.SIMULATION:
                simulation_agent = agent_info
                break
        
        if not simulation_agent:
            error_msg = create_error_message(
                "NO_SIMULATION_AGENT",
                "No simulation agent available to handle simulation request"
            )
            return error_msg.json()
        
        try:
            await simulation_agent["websocket"].send_text(message.json())
            return json.dumps({"type": "request_forwarded", "status": "success"})
        except Exception as e:
            error_msg = create_error_message(
                "FORWARD_FAILED",
                f"Failed to forward simulation request: {str(e)}"
            )
            return error_msg.json()
    
    async def _handle_synthesis_request(self, websocket, agent_id: str, message: SynthesisRequestMessage) -> str:
        """Handle synthesis request"""
        # Find synthesis agent
        synthesis_agent = None
        for agent_id_check, agent_info in self.agents.items():
            if agent_info.get("agent_type") == AgentType.SYNTHESIS:
                synthesis_agent = agent_info
                break
        
        if not synthesis_agent:
            error_msg = create_error_message(
                "NO_SYNTHESIS_AGENT",
                "No synthesis agent available to handle synthesis request"
            )
            return error_msg.json()
        
        try:
            await synthesis_agent["websocket"].send_text(message.json())
            return json.dumps({"type": "request_forwarded", "status": "success"})
        except Exception as e:
            error_msg = create_error_message(
                "FORWARD_FAILED",
                f"Failed to forward synthesis request: {str(e)}"
            )
            return error_msg.json()
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all connected agents"""
        return {
            "total_agents": len(self.agents),
            "agents": {
                agent_id: {
                    "type": agent_info["agent_type"],
                    "capabilities": agent_info["capabilities"],
                    "connected_at": agent_info["connected_at"].isoformat()
                }
                for agent_id, agent_info in self.agents.items()
            }
        }
    
    def disconnect_agent(self, agent_id: str):
        """Remove agent from registry"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Agent {agent_id} disconnected and removed from registry")