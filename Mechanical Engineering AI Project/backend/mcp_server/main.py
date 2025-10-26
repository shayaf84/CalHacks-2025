"""
MCP Server - Main FastAPI Application
Handles agent communication and Materials Project API integration
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import asyncio
from typing import Dict, List
import logging
from communication import MCPCommunicationHandler
from protocol import parse_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Materials Project MCP Server",
    description="Multi-Agent Communication Protocol Server for Material Analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP Communication Handler
communication_handler = MCPCommunicationHandler()

@app.get("/")
async def root():
    """Health check endpoint"""
    agent_status = communication_handler.get_agent_status()
    return {
        "message": "Materials Project MCP Server is running",
        "active_agents": agent_status["total_agents"],
        "agent_types": [agent["type"] for agent in agent_status["agents"].values()]
    }

@app.get("/status")
async def status():
    """Get server status and active agents"""
    agent_status = communication_handler.get_agent_status()
    return {
        "status": "running",
        "agent_status": agent_status
    }

@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for agent communication"""
    try:
        await websocket.accept()
        logger.info(f"Agent {agent_id} connected")
        
        while True:
            # Receive message from agent
            data = await websocket.receive_text()
            
            # Handle message using communication handler
            response = await communication_handler.handle_message(websocket, agent_id, data)
            
            if response:
                await websocket.send_text(response)
                
    except WebSocketDisconnect:
        communication_handler.disconnect_agent(agent_id)
        logger.info(f"Agent {agent_id} disconnected")

if __name__ == "__main__":
    logger.info("Starting Materials Project MCP Server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )