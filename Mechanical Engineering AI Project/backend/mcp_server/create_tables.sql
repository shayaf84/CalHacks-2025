-- Materials Project MCP Server Database Schema
-- Create tables for agent management, message persistence, and material caching

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Agents table - stores agent registration and status
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    capabilities JSONB DEFAULT '[]',
    version VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on agent_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_agents_agent_id ON agents(agent_id);
CREATE INDEX IF NOT EXISTS idx_agents_agent_type ON agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);

-- Messages table - stores MCP message history
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(100) UNIQUE,
    agent_id VARCHAR(100) NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    message_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    correlation_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'sent',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for message queries
CREATE INDEX IF NOT EXISTS idx_messages_agent_id ON messages(agent_id);
CREATE INDEX IF NOT EXISTS idx_messages_message_type ON messages(message_type);
CREATE INDEX IF NOT EXISTS idx_messages_correlation_id ON messages(correlation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);

-- Materials table - stores cached material data from Materials Project API
CREATE TABLE IF NOT EXISTS materials (
    id SERIAL PRIMARY KEY,
    material_id VARCHAR(100) UNIQUE NOT NULL,
    formula VARCHAR(200) NOT NULL,
    formula_pretty VARCHAR(200),
    structure_data JSONB,
    properties JSONB,
    space_group VARCHAR(50),
    lattice_params JSONB,
    density VARCHAR(50),
    band_gap VARCHAR(50),
    formation_energy VARCHAR(50),
    api_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for material queries
CREATE INDEX IF NOT EXISTS idx_materials_material_id ON materials(material_id);
CREATE INDEX IF NOT EXISTS idx_materials_formula ON materials(formula);
CREATE INDEX IF NOT EXISTS idx_materials_space_group ON materials(space_group);

-- Analysis Results table - stores analysis results from analysis agent
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    material_id VARCHAR(100) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    analysis_data JSONB NOT NULL,
    parameters JSONB,
    agent_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for analysis results
CREATE INDEX IF NOT EXISTS idx_analysis_results_material_id ON analysis_results(material_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis_type ON analysis_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_results_agent_id ON analysis_results(agent_id);

-- Simulation Results table - stores simulation results from simulation agent
CREATE TABLE IF NOT EXISTS simulation_results (
    id SERIAL PRIMARY KEY,
    material_id VARCHAR(100) NOT NULL,
    simulation_type VARCHAR(50) NOT NULL,
    simulation_data JSONB NOT NULL,
    parameters JSONB,
    agent_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for simulation results
CREATE INDEX IF NOT EXISTS idx_simulation_results_material_id ON simulation_results(material_id);
CREATE INDEX IF NOT EXISTS idx_simulation_results_simulation_type ON simulation_results(simulation_type);
CREATE INDEX IF NOT EXISTS idx_simulation_results_agent_id ON simulation_results(agent_id);

-- Synthesis Results table - stores synthesis results from synthesis agent
CREATE TABLE IF NOT EXISTS synthesis_results (
    id SERIAL PRIMARY KEY,
    material_id VARCHAR(100) NOT NULL,
    synthesis_type VARCHAR(50) NOT NULL,
    synthesized_output TEXT NOT NULL,
    analysis_data JSONB,
    simulation_data JSONB,
    agent_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for synthesis results
CREATE INDEX IF NOT EXISTS idx_synthesis_results_material_id ON synthesis_results(material_id);
CREATE INDEX IF NOT EXISTS idx_synthesis_results_synthesis_type ON synthesis_results(synthesis_type);
CREATE INDEX IF NOT EXISTS idx_synthesis_results_agent_id ON synthesis_results(agent_id);

-- Workflow States table - tracks multi-agent workflow states
CREATE TABLE IF NOT EXISTS workflow_states (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(100) UNIQUE NOT NULL,
    material_id VARCHAR(100) NOT NULL,
    current_step VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    steps_completed JSONB DEFAULT '[]',
    steps_pending JSONB DEFAULT '[]',
    results JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for workflow states
CREATE INDEX IF NOT EXISTS idx_workflow_states_workflow_id ON workflow_states(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_states_material_id ON workflow_states(material_id);
CREATE INDEX IF NOT EXISTS idx_workflow_states_status ON workflow_states(status);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_materials_updated_at BEFORE UPDATE ON materials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_states_updated_at BEFORE UPDATE ON workflow_states
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) for better security
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE synthesis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_states ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (since we're using anon key)
CREATE POLICY "Allow all operations for anon users" ON agents FOR ALL USING (true);
CREATE POLICY "Allow all operations for anon users" ON messages FOR ALL USING (true);
CREATE POLICY "Allow all operations for anon users" ON materials FOR ALL USING (true);
CREATE POLICY "Allow all operations for anon users" ON analysis_results FOR ALL USING (true);
CREATE POLICY "Allow all operations for anon users" ON simulation_results FOR ALL USING (true);
CREATE POLICY "Allow all operations for anon users" ON synthesis_results FOR ALL USING (true);
CREATE POLICY "Allow all operations for anon users" ON workflow_states FOR ALL USING (true);

-- Insert some sample data for testing
INSERT INTO agents (agent_id, agent_type, capabilities, version) VALUES
('test-retrieval-001', 'retrieval', '["material_search", "structure_fetch", "property_retrieval"]', '1.0.0'),
('test-analysis-001', 'analysis', '["property_analysis", "stability_prediction", "application_suggestion"]', '1.0.0'),
('test-simulation-001', 'simulation', '["degradation_simulation", "stress_testing", "thermal_analysis"]', '1.0.0'),
('test-synthesis-001', 'synthesis', '["natural_language", "table_generation", "visual_creation"]', '1.0.0')
ON CONFLICT (agent_id) DO NOTHING;

-- Create a view for agent status summary
CREATE OR REPLACE VIEW agent_status_summary AS
SELECT 
    agent_type,
    COUNT(*) as total_agents,
    COUNT(*) FILTER (WHERE status = 'active') as active_agents,
    COUNT(*) FILTER (WHERE status = 'inactive') as inactive_agents,
    MAX(last_seen) as last_activity
FROM agents
GROUP BY agent_type;

-- Create a view for message statistics
CREATE OR REPLACE VIEW message_statistics AS
SELECT 
    message_type,
    COUNT(*) as total_messages,
    COUNT(*) FILTER (WHERE status = 'sent') as sent_messages,
    COUNT(*) FILTER (WHERE status = 'received') as received_messages,
    COUNT(*) FILTER (WHERE status = 'error') as error_messages,
    MAX(timestamp) as last_message_time
FROM messages
GROUP BY message_type;