"""
Enhanced MCP Server with Database Integration
Main FastAPI Application with persistent storage and agent management
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import asyncio
from typing import Dict, List, Optional
import logging
from datetime import datetime
import uuid

from communication import MCPCommunicationHandler
from protocol import parse_message, MessageType, AgentType
from database import get_db_manager, DatabaseManager
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Materials Project MCP Server",
    description="Multi-Agent Communication Protocol Server with Database Integration",
    version="2.0.0"
)

# Get configuration
config = get_config()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=config.cors_methods,
    allow_headers=config.cors_headers,
)

# Initialize components
communication_handler = MCPCommunicationHandler()
db_manager = get_db_manager()

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    try:
        # Get database health
        db_health = db_manager.health_check()
        
        # Get agent status
        agent_status = communication_handler.get_agent_status()
        
        return {
            "message": "Materials Project MCP Server v2.0 is running",
            "database": db_health,
            "active_agents": agent_status["total_agents"],
            "agent_types": [agent["type"] for agent in agent_status["agents"].values()],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Server health check failed")

@app.get("/status")
async def status():
    """Get detailed server status"""
    try:
        # Get database health
        db_health = db_manager.health_check()
        
        # Get agent status
        agent_status = communication_handler.get_agent_status()
        
        # Get database statistics
        agents = db_manager.get_all_agents()
        
        return {
            "status": "running",
            "database": db_health,
            "agent_status": agent_status,
            "database_stats": {
                "total_agents_registered": len(agents),
                "active_agents": len([a for a in agents if a.status == "active"]),
                "inactive_agents": len([a for a in agents if a.status == "inactive"])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

@app.get("/agents")
async def get_agents():
    """Get all registered agents"""
    try:
        agents = db_manager.get_all_agents()
        return {
            "agents": [
                {
                    "agent_id": agent.agent_id,
                    "agent_type": agent.agent_type,
                    "capabilities": agent.capabilities,
                    "status": agent.status,
                    "connected_at": agent.connected_at.isoformat(),
                    "last_seen": agent.last_seen.isoformat()
                }
                for agent in agents
            ],
            "total": len(agents)
        }
    except Exception as e:
        logger.error(f"Failed to get agents: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agents")

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent details"""
    try:
        agent = db_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type,
            "capabilities": agent.capabilities,
            "version": agent.version,
            "status": agent.status,
            "connected_at": agent.connected_at.isoformat(),
            "last_seen": agent.last_seen.isoformat(),
            "created_at": agent.created_at.isoformat(),
            "updated_at": agent.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent")

@app.get("/materials/{material_id}")
async def get_material(material_id: str):
    """Get cached material data"""
    try:
        material = db_manager.get_material(material_id)
        if not material:
            raise HTTPException(status_code=404, detail="Material not found in cache")
        
        return {
            "material_id": material.material_id,
            "formula": material.formula,
            "formula_pretty": material.formula_pretty,
            "space_group": material.space_group,
            "lattice_params": material.lattice_params,
            "density": material.density,
            "band_gap": material.band_gap,
            "formation_energy": material.formation_energy,
            "created_at": material.created_at.isoformat(),
            "updated_at": material.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get material {material_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get material")

@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """Enhanced WebSocket endpoint with database integration"""
    try:
        await websocket.accept()
        active_connections[agent_id] = websocket
        logger.info(f"Agent {agent_id} connected")
        
        while True:
            # Receive message from agent
            data = await websocket.receive_text()
            
            try:
                # Parse message to get type
                message = parse_message(data)
                message_type = message.type
                
                # Store message in database
                db_manager.create_message(
                    agent_id=agent_id,
                    message_type=message_type,
                    content=message.dict(),
                    message_id=str(uuid.uuid4()),
                    correlation_id=getattr(message, 'correlation_id', None)
                )
                
                # Handle handshake messages
                if message_type == MessageType.HANDSHAKE:
                    try:
                        # Create agent record in database
                        db_manager.create_agent(
                            agent_id=agent_id,
                            agent_type=message.agent_type,
                            capabilities=message.capabilities,
                            version=message.version
                        )
                        logger.info(f"Registered agent {agent_id} ({message.agent_type}) in database")
                    except Exception as e:
                        logger.warning(f"Agent {agent_id} already exists in database: {e}")
                
                # Handle message using communication handler
                response = await communication_handler.handle_message(websocket, agent_id, data)
                
                if response:
                    # Store response message
                    response_data = json.loads(response)
                    db_manager.create_message(
                        agent_id="server",
                        message_type=response_data.get("type", "response"),
                        content=response_data,
                        message_id=str(uuid.uuid4()),
                        correlation_id=getattr(message, 'correlation_id', None)
                    )
                    
                    await websocket.send_text(response)
                
            except Exception as e:
                logger.error(f"Error processing message from {agent_id}: {e}")
                error_response = json.dumps({
                    "type": "error",
                    "error_code": "PROCESSING_ERROR",
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
                await websocket.send_text(error_response)
                
    except WebSocketDisconnect:
        # Update agent status in database
        try:
            db_manager.update_agent_status(agent_id, "inactive")
            logger.info(f"Updated agent {agent_id} status to inactive")
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id} status: {e}")
        
        # Remove from active connections
        if agent_id in active_connections:
            del active_connections[agent_id]
        
        communication_handler.disconnect_agent(agent_id)
        logger.info(f"Agent {agent_id} disconnected")

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Database health
        db_health = db_manager.health_check()
        
        # Agent status
        agent_status = communication_handler.get_agent_status()
        
        # WebSocket connections
        ws_connections = len(active_connections)
        
        # Overall health
        overall_health = "healthy" if db_health["status"] == "healthy" else "unhealthy"
        
        return {
            "status": overall_health,
            "database": db_health,
            "agents": agent_status,
            "websocket_connections": ws_connections,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    logger.info("Starting Enhanced Materials Project MCP Server v2.0...")
    logger.info(f"Database URL: {config.database_url}")
    logger.info(f"Server will run on {config.host}:{config.port}")
    
    uvicorn.run(
        "main_with_db:app",
        host=config.host,
        port=config.port,
        reload=config.reload,
        log_level=config.log_level.lower()
    )