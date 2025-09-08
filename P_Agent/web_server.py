#!/usr/bin/env python3
"""
Statistics Agent Web Server - Network Ready Version
Supports A2A communication across different systems
Port: 5003
"""

import os
import sys
import socket
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from statistics_agent import StandaloneStatisticsAgent
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, template_folder='templates')
CORS(app)

# Initialize the statistics agent with network configuration
class NetworkStatisticsAgent(StandaloneStatisticsAgent):
    def __init__(self):
        super().__init__()
        self.agent_id = "statistics_agent"
        self.port = int(os.getenv('STATISTICS_PORT', 5003))
        self.host = '0.0.0.0'
        self.my_ip = self.get_local_ip()
        
        # Other agents' addresses (from environment variables)
        self.calculator_url = f"http://{os.getenv('CALCULATOR_HOST', 'localhost')}:{os.getenv('CALCULATOR_PORT', 5001)}"
        self.unit_converter_url = f"http://{os.getenv('UNIT_CONVERTER_HOST', 'localhost')}:{os.getenv('UNIT_CONVERTER_PORT', 5002)}"
        
        print(f"📊 Statistics Agent initialized")
        print(f"📍 My IP: {self.my_ip}:{self.port}")
        print(f"🧮 Calculator: {self.calculator_url}")
        print(f"🔄 Unit Converter: {self.unit_converter_url}")
    
    def get_local_ip(self):
        """Get the local IP address of this machine"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            return ip
        except Exception:
            return "127.0.0.1"

# Initialize the network-ready statistics agent
stats_agent = NetworkStatisticsAgent()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "agent": "statistics_agent",
        "ip": stats_agent.my_ip,
        "port": stats_agent.port,
        "timestamp": datetime.now().isoformat(),
        "connected_agents": {
            "calculator": stats_agent.calculator_url,
            "unit_converter": stats_agent.unit_converter_url
        }
    })

@app.route('/stats', methods=['POST'])
def calculate_stats():
    """Calculate statistics via API"""
    try:
        data = request.get_json()
        operation = data.get('operation')
        request_data = data.get('data', {})
        
        print(f"📊 Web request: {operation} with {request_data}")
        
        result = stats_agent.process_request(operation, request_data)
        
        return jsonify({
            "agent": "statistics_agent",
            "request": data,
            "response": result
        })
    
    except Exception as e:
        return jsonify({
            "agent": "statistics_agent",
            "error": f"Request processing failed: {str(e)}"
        }), 400

@app.route('/message', methods=['POST'])
def receive_message():
    """Inter-agent communication endpoint (A2A protocol)"""
    try:
        incoming = request.get_json()
        sender = incoming.get('sender', 'unknown')
        message = incoming.get('message', {})
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        print(f"🤖 Message from {sender} ({client_ip})")
        
        operation = message.get('operation')
        request_data = message.get('data', {})
        
        result = stats_agent.process_request(operation, request_data)
        
        return jsonify({
            "agent": "statistics_agent",
            "server_ip": stats_agent.my_ip,
            "sender": sender,
            "response": result,
            "correlation_id": incoming.get('correlation_id'),
            "trace": incoming.get('trace', []) + [f"{stats_agent.agent_id}@{stats_agent.my_ip}:{stats_agent.port}"],
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "agent": "statistics_agent",
            "error": f"Message processing failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 400

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    """Alternative API endpoint for calculations"""
    try:
        data = request.get_json()
        operation = data.get('operation')
        numbers = data.get('numbers', [])
        
        if not numbers:
            return jsonify({"error": "No numbers provided"}), 400
        
        result = stats_agent.process_request(operation, {"numbers": numbers})
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/sample-data')
def get_sample_data():
    """Get sample data for testing"""
    sample_data = {
        "sample1": [10, 15, 20, 25, 30, 25, 15],
        "sample2": [1, 2, 3, 4, 5],
        "sample3": [100, 200, 300, 400, 500],
        "sample4": [5, 5, 5, 5, 5],
        "sample5": [1, 2, 2, 3, 3, 3, 4, 4, 5]
    }
    return jsonify(sample_data)

def test_network_connectivity():
    """Test connectivity to other agents"""
    print("\n🌐 Testing Network Connectivity...")
    
    agents_to_test = {
        "Calculator": stats_agent.calculator_url,
        "Unit Converter": stats_agent.unit_converter_url
    }
    
    for agent_name, url in agents_to_test.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {agent_name}: Connected ({url})")
            else:
                print(f"❌ {agent_name}: Not responding ({url})")
        except Exception as e:
            print(f"❌ {agent_name}: Connection failed ({url}) - {str(e)}")

def test_agent():
    """Test the statistics agent"""
    print("📊 Testing Statistics Agent...")
    
    tests = [
        {"operation": "mean", "data": {"numbers": [10, 20, 30]}},
        {"operation": "median", "data": {"numbers": [1, 2, 3, 4, 5]}},
        {"operation": "mode", "data": {"numbers": [1, 2, 2, 3, 3, 3]}},
        {"operation": "standard_deviation", "data": {"numbers": [10, 20, 30, 40]}}
    ]
    
    for test in tests:
        result = stats_agent.process_request(test["operation"], test["data"])
        if result.get("success"):
            print(f"✅ {test['operation']}: {result.get('result', 'Error')}")
        else:
            print(f"❌ {test['operation']}: {result.get('error', 'Unknown error')}")

if __name__ == '__main__':
    print("📊 Network Statistics Agent Starting...")
    
    # Test local functionality
    test_agent()
    
    # Test network connectivity
    test_network_connectivity()
    
    print(f"\n🚀 Server starting on {stats_agent.host}:{stats_agent.port}")
    print(f"📍 Access from other systems: http://{stats_agent.my_ip}:{stats_agent.port}")
    print("🔗 Web Interface: http://localhost:5003")
    print("📊 Health Check: http://localhost:5003/health")
    print("🤖 Inter-Agent: http://localhost:5003/message")
    
    # Run Flask app
    app.run(host=stats_agent.host, port=stats_agent.port, debug=True)