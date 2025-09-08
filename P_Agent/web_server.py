#!/usr/bin/env python3
"""
Statistics Agent Web Server
Serves the HTML frontend and handles API requests
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from statistics_agent import StandaloneStatisticsAgent
import json

# Create Flask app
app = Flask(__name__, template_folder='templates')
CORS(app)

# Initialize the statistics agent
stats_agent = StandaloneStatisticsAgent()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "agent": "statistics_agent",
        "ip": "192.168.0.99",  # You can get this dynamically
        "port": 5003,
        "mode": "web_server"
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
    """Inter-agent communication endpoint"""
    try:
        data = request.get_json()
        sender = data.get('sender', 'unknown')
        message = data.get('message', {})
        
        print(f"🤖 Message from {sender}")
        
        operation = message.get('operation')
        request_data = message.get('data', {})
        
        result = stats_agent.process_request(operation, request_data)
        
        return jsonify({
            "agent": "statistics_agent",
            "sender": sender,
            "response": result
        })
    
    except Exception as e:
        return jsonify({
            "agent": "statistics_agent",
            "error": f"Message processing failed: {str(e)}"
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

if __name__ == '__main__':
    print("🌐 Statistics Agent Web Server Starting...")
    print("📍 Web Interface: http://localhost:5003")
    print("🔗 API Endpoint: http://localhost:5003/stats")
    print("📊 Health Check: http://localhost:5003/health")
    print("🤖 Inter-Agent: http://localhost:5003/message")
    
    # Test the agent
    print("\n🧪 Testing agent...")
    test_result = stats_agent.process_request("mean", {"numbers": [10, 20, 30]})
    if test_result.get("success"):
        print(f"✅ Agent test passed: mean([10, 20, 30]) = {test_result['result']}")
    else:
        print(f"❌ Agent test failed: {test_result.get('error')}")
    
    print("\n🚀 Starting web server...")
    app.run(host='0.0.0.0', port=5004, debug=True)