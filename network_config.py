"""
Network Configuration for Multi-System Agent Communication
Update these IPs based on your actual system IPs
"""

import os
from datetime import datetime

class NetworkConfig:
    def __init__(self):
        # Default to localhost for local testing
        self.calculator_host = os.getenv('CALCULATOR_HOST', 'localhost')
        self.calculator_port = os.getenv('CALCULATOR_PORT', '5001')
        
        self.unit_converter_host = os.getenv('UNIT_CONVERTER_HOST', 'localhost')
        self.unit_converter_port = os.getenv('UNIT_CONVERTER_PORT', '5002')
        
        self.statistics_host = os.getenv('STATISTICS_HOST', 'localhost')
        self.statistics_port = os.getenv('STATISTICS_PORT', '5003')
        
        # Build URLs
        self.calculator_url = f"http://{self.calculator_host}:{self.calculator_port}"
        self.unit_converter_url = f"http://{self.unit_converter_host}:{self.unit_converter_port}"
        self.statistics_url = f"http://{self.statistics_host}:{self.statistics_port}"
        
        # Registry for all agents
        self.agents = {
            'calculator': {
                'url': self.calculator_url,
                'host': self.calculator_host,
                'port': self.calculator_port,
                'capabilities': ['add', 'subtract', 'multiply', 'divide', 'power', 'square_root', 'percentage']
            },
            'unit_converter': {
                'url': self.unit_converter_url,
                'host': self.unit_converter_host,
                'port': self.unit_converter_port,
                'capabilities': ['length', 'weight', 'temperature', 'volume']
            },
            'statistics': {
                'url': self.statistics_url,
                'host': self.statistics_host,
                'port': self.statistics_port,
                'capabilities': ['mean', 'median', 'mode', 'standard_deviation', 'range']
            }
        }
    
    def get_agent_url(self, agent_name):
        """Get URL for specific agent"""
        return self.agents.get(agent_name, {}).get('url', '')
    
    def update_agent_host(self, agent_name, host, port=None):
        """Update host/port for specific agent"""
        if agent_name in self.agents:
            self.agents[agent_name]['host'] = host
            if port:
                self.agents[agent_name]['port'] = str(port)
            self.agents[agent_name]['url'] = f"http://{host}:{self.agents[agent_name]['port']}"
    
    def print_config(self):
        """Print current configuration"""
        print("🌐 Network Configuration:")
        print("=" * 40)
        for name, config in self.agents.items():
            print(f"{name.title()}: {config['url']}")
        print(f"\nGenerated at: {datetime.now().isoformat()}")

# Global config instance
network_config = NetworkConfig()

# Helper function for easy importing
def get_config():
    return network_config

# Example environment variables setup
def create_env_file():
    """Create .env file template"""
    env_content = """# Network Configuration for Math Agents
# Update these IPs with your actual system IPs

# Calculator Agent (Your system)
CALCULATOR_HOST=192.168.1.100
CALCULATOR_PORT=5001

# Unit Converter Agent (Teammate 1's system)
UNIT_CONVERTER_HOST=192.168.1.101
UNIT_CONVERTER_PORT=5002

# Statistics Agent (Teammate 2's system)
STATISTICS_HOST=192.168.1.102
STATISTICS_PORT=5003

# Alternative: Use public IPs if on different networks
# CALCULATOR_HOST=203.0.113.1
# UNIT_CONVERTER_HOST=203.0.113.2
# STATISTICS_HOST=203.0.113.3
"""
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Created .env file template")
    print("📝 Update the IPs with your actual system addresses")

if __name__ == "__main__":
    network_config.print_config()
    create_env_file()
