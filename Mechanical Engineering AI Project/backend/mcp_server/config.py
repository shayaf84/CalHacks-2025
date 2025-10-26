"""
MCP Server Configuration
Centralized configuration for the Materials Project MCP Server
"""

import os
from typing import Dict, List, Any
from pydantic_settings import BaseSettings

class MCPServerConfig(BaseSettings):
    """Configuration settings for MCP Server"""
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    reload: bool = True
    
    # Materials Project API Settings
    materials_project_api_key: str = "wNWHdtELVIgc7FbaasH6QVFNaFqUdfeH"
    materials_project_base_url: str = "https://api.materialsproject.org"
    
    # Database Settings
    database_url: str = "sqlite:///./mcp_server.db"  # Fallback to SQLite
    database_echo: bool = False
    
    # Supabase Settings
    supabase_url: str = ""
    supabase_key: str = ""
    
    # Agent Settings
    max_agents: int = 10
    agent_timeout: int = 300  # 5 minutes
    message_queue_size: int = 1000
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS Settings
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Security Settings
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # Letta Integration (for future use)
    letta_api_key: str = ""
    letta_base_url: str = "https://api.letta.ai"
    
    # Conway Integration (for future use)
    conway_api_key: str = ""
    conway_base_url: str = "https://api.conway.ai"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global configuration instance
config = MCPServerConfig()

# Agent type configurations
AGENT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "retrieval": {
        "description": "Retrieves material data from Materials Project API",
        "capabilities": ["material_search", "structure_fetch", "property_retrieval"],
        "max_concurrent_requests": 5,
        "timeout": 30
    },
    "analysis": {
        "description": "Analyzes material properties and characteristics",
        "capabilities": ["property_analysis", "stability_prediction", "application_suggestion"],
        "max_concurrent_requests": 3,
        "timeout": 60
    },
    "simulation": {
        "description": "Runs virtual simulations on materials",
        "capabilities": ["degradation_simulation", "stress_testing", "thermal_analysis"],
        "max_concurrent_requests": 2,
        "timeout": 120
    },
    "synthesis": {
        "description": "Synthesizes results into readable formats",
        "capabilities": ["natural_language", "table_generation", "visual_creation"],
        "max_concurrent_requests": 5,
        "timeout": 45
    }
}

# Message type configurations
MESSAGE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "material_request": {
        "priority": "high",
        "timeout": 30,
        "retry_count": 3
    },
    "analysis_request": {
        "priority": "medium",
        "timeout": 60,
        "retry_count": 2
    },
    "simulation_request": {
        "priority": "medium",
        "timeout": 120,
        "retry_count": 1
    },
    "synthesis_request": {
        "priority": "low",
        "timeout": 45,
        "retry_count": 2
    }
}

# Database table configurations
DATABASE_TABLES = {
    "agents": {
        "columns": [
            "id", "agent_id", "agent_type", "capabilities", 
            "connected_at", "last_seen", "status"
        ]
    },
    "messages": {
        "columns": [
            "id", "message_id", "agent_id", "message_type", 
            "content", "timestamp", "status"
        ]
    },
    "materials": {
        "columns": [
            "id", "material_id", "formula", "structure_data", 
            "properties", "created_at", "updated_at"
        ]
    }
}

def get_config() -> MCPServerConfig:
    """Get the global configuration instance"""
    return config

def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """Get configuration for specific agent type"""
    return AGENT_CONFIGS.get(agent_type, {})

def get_message_config(message_type: str) -> Dict[str, Any]:
    """Get configuration for specific message type"""
    return MESSAGE_CONFIGS.get(message_type, {})

def get_database_config() -> Dict[str, Any]:
    """Get database configuration"""
    return {
        "url": config.database_url,
        "echo": config.database_echo,
        "tables": DATABASE_TABLES
    }