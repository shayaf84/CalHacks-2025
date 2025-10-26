"""
Final MCP Server with Supabase Integration
Complete Multi-Agent Communication Protocol Server with PostgreSQL database
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
from supabase_db import get_supabase_manager, SupabaseManager
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Materials Project MCP Server",
    description="Multi-Agent Communication Protocol Server with Supabase PostgreSQL",
    version="3.0.0"
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
supabase_manager = get_supabase_manager()

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    try:
        # Get Supabase health
        db_health = supabase_manager.health_check()
        
        # Get agent status
        agent_status = communication_handler.get_agent_status()
        
        return {
            "message": "Materials Project MCP Server v3.0 with Supabase is running",
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
        # Get Supabase health
        db_health = supabase_manager.health_check()
        
        # Get agent status
        agent_status = communication_handler.get_agent_status()
        
        # Get database statistics
        agents = supabase_manager.get_all_agents()
        
        return {
            "status": "running",
            "database": db_health,
            "agent_status": agent_status,
            "database_stats": {
                "total_agents_registered": len(agents),
                "active_agents": len([a for a in agents if a["status"] == "active"]),
                "inactive_agents": len([a for a in agents if a["status"] == "inactive"])
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
        agents = supabase_manager.get_all_agents()
        return {
            "agents": [
                {
                    "agent_id": agent["agent_id"],
                    "agent_type": agent["agent_type"],
                    "capabilities": agent["capabilities"],
                    "status": agent["status"],
                    "connected_at": agent["connected_at"],
                    "last_seen": agent["last_seen"]
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
        agent = supabase_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "agent_id": agent["agent_id"],
            "agent_type": agent["agent_type"],
            "capabilities": agent["capabilities"],
            "version": agent["version"],
            "status": agent["status"],
            "connected_at": agent["connected_at"],
            "last_seen": agent["last_seen"]
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
        material = supabase_manager.get_material(material_id)
        if not material:
            raise HTTPException(status_code=404, detail="Material not found in cache")
        
        return {
            "material_id": material["material_id"],
            "formula": material["formula"],
            "formula_pretty": material["formula_pretty"],
            "space_group": material["space_group"],
            "lattice_params": material["lattice_params"],
            "density": material["density"],
            "band_gap": material["band_gap"],
            "formation_energy": material["formation_energy"],
            "created_at": material["created_at"],
            "updated_at": material["updated_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get material {material_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get material")

@app.post("/materials/search")
async def search_materials(formula: str):
    """Search materials by formula"""
    try:
        materials = supabase_manager.search_materials_by_formula(formula)
        return {
            "materials": [
                {
                    "material_id": material["material_id"],
                    "formula": material["formula"],
                    "formula_pretty": material["formula_pretty"],
                    "space_group": material["space_group"]
                }
                for material in materials
            ],
            "total": len(materials)
        }
    except Exception as e:
        logger.error(f"Failed to search materials: {e}")
        raise HTTPException(status_code=500, detail="Failed to search materials")

@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow state"""
    try:
        workflow = supabase_manager.get_workflow_state(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "workflow_id": workflow["workflow_id"],
            "material_id": workflow["material_id"],
            "current_step": workflow["current_step"],
            "status": workflow["status"],
            "steps_completed": workflow["steps_completed"],
            "steps_pending": workflow["steps_pending"],
            "results": workflow["results"],
            "created_at": workflow["created_at"],
            "updated_at": workflow["updated_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get workflow")

@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """Enhanced WebSocket endpoint with Supabase integration"""
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
                
                # Store message in Supabase
                supabase_manager.create_message(
                    agent_id=agent_id,
                    message_type=message_type,
                    content=message.dict(),
                    message_id=str(uuid.uuid4()),
                    correlation_id=getattr(message, 'correlation_id', None)
                )
                
                # Handle handshake messages
                if message_type == MessageType.HANDSHAKE:
                    try:
                        # Create agent record in Supabase
                        supabase_manager.create_agent(
                            agent_id=agent_id,
                            agent_type=message.agent_type,
                            capabilities=message.capabilities,
                            version=message.version
                        )
                        logger.info(f"Registered agent {agent_id} ({message.agent_type}) in Supabase")
                    except Exception as e:
                        logger.warning(f"Agent {agent_id} already exists in Supabase: {e}")
                
                # Handle message using communication handler
                response = await communication_handler.handle_message(websocket, agent_id, data)
                
                if response:
                    # Store response message
                    response_data = json.loads(response)
                    supabase_manager.create_message(
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
        # Update agent status in Supabase
        try:
            supabase_manager.update_agent_status(agent_id, "inactive")
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
        # Supabase health
        db_health = supabase_manager.health_check()
        
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

@app.get("/stats")
async def get_statistics():
    """Get server statistics"""
    try:
        # Get all data for statistics
        agents = supabase_manager.get_all_agents()
        materials = supabase_manager.search_materials_by_formula("")  # Get all materials
        
        # Calculate statistics
        agent_stats = {}
        for agent in agents:
            agent_type = agent["agent_type"]
            if agent_type not in agent_stats:
                agent_stats[agent_type] = {"total": 0, "active": 0, "inactive": 0}
            agent_stats[agent_type]["total"] += 1
            if agent["status"] == "active":
                agent_stats[agent_type]["active"] += 1
            else:
                agent_stats[agent_type]["inactive"] += 1
        
        return {
            "agents": agent_stats,
            "materials": {
                "total_cached": len(materials),
                "unique_formulas": len(set(m["formula"] for m in materials))
            },
            "websocket_connections": len(active_connections),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

if __name__ == "__main__":
    logger.info("Starting Materials Project MCP Server v3.0 with Supabase...")
    logger.info(f"Supabase URL: {config.supabase_url}")
    logger.info(f"Server will run on {config.host}:{config.port}")
    
    uvicorn.run(
        "main_supabase:app",
        host=config.host,
        port=config.port,
        reload=config.reload,
        log_level=config.log_level.lower()
    )