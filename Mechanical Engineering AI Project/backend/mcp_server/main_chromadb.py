"""
ChromaDB MCP Server - Main Application
FastAPI server with WebSocket support for multi-agent communication using ChromaDB
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Import our modules
from chromadb_manager import ChromaDBManager
from materials_api import MaterialsProjectAPI
from protocol import (
    MCPMessage, MessageType, AgentType, HandshakeMessage,
    MaterialRequestMessage, AnalysisRequestMessage, SimulationRequestMessage,
    SynthesisRequestMessage, MaterialResponseMessage, AnalysisResponseMessage,
    SimulationResponseMessage, SynthesisResponseMessage, ErrorMessage
)
from communication import MCPCommunicationHandler

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDBMCPServer:
    """Main MCP Server using ChromaDB for vector operations"""
    
    def __init__(self):
        """Initialize the MCP server"""
        self.app = FastAPI(
            title="ChromaDB MCP Server",
            description="Multi-Agent Communication Protocol Server with ChromaDB",
            version="2.0.0"
        )
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize components
        self.chromadb_manager = ChromaDBManager()
        self.materials_api = MaterialsProjectAPI()
        # self.communication_handler = MCPCommunicationHandler()  # Temporarily disabled
        self.active_agents = {}  # Simple agent tracking
        
        # Server configuration
        self.host = os.getenv("HOST", "localhost")
        self.port = int(os.getenv("PORT", 8000))
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        
        # Setup routes
        self._setup_routes()
        
        logger.info("ChromaDB MCP Server initialized successfully")
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "message": "ChromaDB MCP Server",
                "version": "2.0.0",
                "status": "running",
                "database": "ChromaDB",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            try:
                # Check ChromaDB connection
                chromadb_stats = self.chromadb_manager.get_collection_stats()
                
                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "chromadb": {
                        "status": "connected",
                        "collections": chromadb_stats
                    },
                    "materials_api": {
                        "status": "connected" if self.materials_api else "disconnected"
                    },
                    "active_agents": len(self.active_agents)
                }
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                )
        
        @self.app.get("/agents")
        async def get_agents():
            """Get list of active agents"""
            return {
                "agents": list(self.active_agents.values()),
                "count": len(self.active_agents)
            }
        
        @self.app.get("/materials/search")
        async def search_materials(query: str, limit: int = 5):
            """Search materials using vector similarity"""
            try:
                results = self.chromadb_manager.search_similar_materials(query, limit)
                return {
                    "query": query,
                    "results": results,
                    "count": len(results)
                }
            except Exception as e:
                logger.error(f"Material search failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/materials/{material_id}")
        async def get_material(material_id: str):
            """Get specific material by ID"""
            try:
                # Search for material in ChromaDB
                results = self.chromadb_manager.search_similar_materials(
                    f"material_id:{material_id}", 1
                )
                
                if results:
                    return results[0]
                else:
                    raise HTTPException(status_code=404, detail="Material not found")
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Get material failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/materials")
        async def add_material(material_data: Dict[str, Any]):
            """Add new material to ChromaDB"""
            try:
                material_id = material_data.get("material_id")
                if not material_id:
                    raise HTTPException(status_code=400, detail="material_id is required")
                
                success = self.chromadb_manager.add_material(material_id, material_data)
                
                if success:
                    return {"message": "Material added successfully", "material_id": material_id}
                else:
                    raise HTTPException(status_code=500, detail="Failed to add material")
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Add material failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/stats")
        async def get_stats():
            """Get server statistics"""
            try:
                chromadb_stats = self.chromadb_manager.get_collection_stats()
                
                return {
                    "server": {
                        "status": "running",
                        "uptime": "N/A",  # Could implement uptime tracking
                        "version": "2.0.0"
                    },
                    "chromadb": chromadb_stats,
                    "agents": {
                        "active": len(self.active_agents),
                        "list": list(self.active_agents.keys())
                    },
                    "materials_api": {
                        "status": "connected" if self.materials_api else "disconnected"
                    }
                }
            except Exception as e:
                logger.error(f"Get stats failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for agent communication"""
            await websocket.accept()
            agent_id = None
            
            try:
                while True:
                    # Receive message
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    # Parse message
                    message = MCPMessage(**message_data)
                    
                    # Handle different message types
                    if message.type == MessageType.HANDSHAKE:
                        handshake = message
                        agent_id = handshake.agent_id
                        
                        # Register agent
                        self.active_agents[agent_id] = {
                            "agent_type": handshake.agent_type,
                            "capabilities": handshake.capabilities,
                            "connected_at": datetime.now().isoformat()
                        }
                        
                        # Send confirmation
                        response = MaterialResponseMessage(
                            type=MessageType.MATERIAL_RESPONSE,
                            material_data={"message": "Agent registered successfully", "agent_id": agent_id},
                            status="success"
                        )
                        await websocket.send_text(response.json())
                        
                        logger.info(f"Agent {agent_id} registered successfully")
                    
                    elif message.type == MessageType.MATERIAL_REQUEST:
                        material_request = message
                        
                        # Process material request using ChromaDB
                        await self._handle_material_request(websocket, material_request)
                    
                    elif message.type == MessageType.ANALYSIS_REQUEST:
                        analysis_request = message
                        
                        # Process analysis request
                        await self._handle_analysis_request(websocket, analysis_request)
                    
                    elif message.type == MessageType.SIMULATION_REQUEST:
                        simulation_request = message
                        
                        # Process simulation request
                        await self._handle_simulation_request(websocket, simulation_request)
                    
                    elif message.type == MessageType.SYNTHESIS_REQUEST:
                        synthesis_request = message
                        
                        # Process synthesis request
                        await self._handle_synthesis_request(websocket, synthesis_request)
                    
                    else:
                        # Unknown message type
                        error = ErrorMessage(
                            type=MessageType.ERROR,
                            error_code="UNKNOWN_MESSAGE_TYPE",
                            error_message=f"Unknown message type: {message.type}"
                        )
                        await websocket.send_text(error.json())
            
            except WebSocketDisconnect:
                if agent_id:
                    if agent_id in self.active_agents:
                        del self.active_agents[agent_id]
                    logger.info(f"Agent {agent_id} disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                if agent_id:
                    if agent_id in self.active_agents:
                        del self.active_agents[agent_id]
    
    async def _handle_material_request(self, websocket: WebSocket, request: MaterialRequestMessage):
        """Handle material request using ChromaDB vector search"""
        try:
            # Search materials using vector similarity
            query = request.formula or f"material_id:{request.material_id}" if request.material_id else "material"
            results = self.chromadb_manager.search_similar_materials(query, 5)
            
            # Format response
            response_data = {
                "query": query,
                "results": results,
                "count": len(results),
                "search_type": "vector_similarity"
            }
            
            response = MaterialResponseMessage(
                type=MessageType.MATERIAL_RESPONSE,
                material_data=response_data,
                status="success"
            )
            
            await websocket.send_text(response.json())
            logger.info(f"Material request processed: {query}")
            
        except Exception as e:
            logger.error(f"Material request failed: {e}")
            error = ErrorMessage(
                type=MessageType.ERROR,
                error_code="MATERIAL_SEARCH_FAILED",
                error_message=str(e)
            )
            await websocket.send_text(error.json())
    
    async def _handle_analysis_request(self, websocket: WebSocket, request: AnalysisRequestMessage):
        """Handle analysis request"""
        try:
            # Get material data
            material_results = self.chromadb_manager.search_similar_materials(
                f"material_id:{request.material_id}", 1
            )
            
            if not material_results:
                raise Exception(f"Material {request.material_id} not found")
            
            material_data = material_results[0]['document']
            
            # Perform analysis (simplified for now)
            analysis_result = {
                "material_id": request.material_id,
                "analysis_type": request.analysis_type,
                "results": {
                    "band_gap": material_data.get('band_gap', 'N/A'),
                    "density": material_data.get('density', 'N/A'),
                    "crystal_system": material_data.get('crystal_system', 'N/A'),
                    "space_group": material_data.get('space_group', 'N/A')
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Store analysis result in ChromaDB
            analysis_id = f"analysis_{request.material_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.chromadb_manager.add_analysis_result(analysis_id, analysis_result)
            
            response = AnalysisResponseMessage(
                type=MessageType.ANALYSIS_RESPONSE,
                material_id=request.material_id,
                analysis_results=analysis_result,
                status="success"
            )
            
            await websocket.send_text(response.json())
            logger.info(f"Analysis request processed: {request.material_id}")
            
        except Exception as e:
            logger.error(f"Analysis request failed: {e}")
            error = ErrorMessage(
                type=MessageType.ERROR,
                error_code="ANALYSIS_FAILED",
                error_message=str(e)
            )
            await websocket.send_text(error.json())
    
    async def _handle_simulation_request(self, websocket: WebSocket, request: SimulationRequestMessage):
        """Handle simulation request"""
        try:
            # Get material data
            material_results = self.chromadb_manager.search_similar_materials(
                f"material_id:{request.material_id}", 1
            )
            
            if not material_results:
                raise Exception(f"Material {request.material_id} not found")
            
            material_data = material_results[0]['document']
            
            # Perform simulation (simplified for now)
            simulation_result = {
                "material_id": request.material_id,
                "simulation_type": request.simulation_type,
                "parameters": request.parameters,
                "results": {
                    "energy": "Simulated energy value",
                    "stability": "Simulated stability",
                    "properties": "Simulated properties"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Store simulation result in ChromaDB
            simulation_id = f"simulation_{request.material_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.chromadb_manager.add_analysis_result(simulation_id, simulation_result)
            
            response = SimulationResponseMessage(
                type=MessageType.SIMULATION_RESPONSE,
                material_id=request.material_id,
                simulation_results=simulation_result,
                status="success"
            )
            
            await websocket.send_text(response.json())
            logger.info(f"Simulation request processed: {request.material_id}")
            
        except Exception as e:
            logger.error(f"Simulation request failed: {e}")
            error = ErrorMessage(
                type=MessageType.ERROR,
                error_code="SIMULATION_FAILED",
                error_message=str(e)
            )
            await websocket.send_text(error.json())
    
    async def _handle_synthesis_request(self, websocket: WebSocket, request: SynthesisRequestMessage):
        """Handle synthesis request"""
        try:
            # Get material data
            material_results = self.chromadb_manager.search_similar_materials(
                f"material_id:{request.material_id}", 1
            )
            
            if not material_results:
                raise Exception(f"Material {request.material_id} not found")
            
            material_data = material_results[0]['document']
            
            # Generate synthesis recommendations (simplified for now)
            synthesis_result = {
                "material_id": request.material_id,
                "method": request.method or "CVD",
                "recommendations": {
                    "temperature": "800-1200°C",
                    "pressure": "1-10 atm",
                    "precursors": "Material-specific precursors",
                    "conditions": "Optimized synthesis conditions"
                },
                "success_rate": 0.85,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store synthesis result in ChromaDB
            synthesis_id = f"synthesis_{request.material_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.chromadb_manager.add_synthesis_result(synthesis_id, synthesis_result)
            
            response = SynthesisResponseMessage(
                type=MessageType.SYNTHESIS_RESPONSE,
                material_id=request.material_id,
                synthesized_output=json.dumps(synthesis_result),
                output_format=request.output_format,
                status="success"
            )
            
            await websocket.send_text(response.json())
            logger.info(f"Synthesis request processed: {request.material_id}")
            
        except Exception as e:
            logger.error(f"Synthesis request failed: {e}")
            error = ErrorMessage(
                type=MessageType.ERROR,
                error_code="SYNTHESIS_FAILED",
                error_message=str(e)
            )
            await websocket.send_text(error.json())
    
    def run(self):
        """Run the server"""
        logger.info(f"Starting ChromaDB MCP Server on {self.host}:{self.port}")
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info" if not self.debug else "debug"
        )

def main():
    """Main function"""
    server = ChromaDBMCPServer()
    server.run()

if __name__ == "__main__":
    main()