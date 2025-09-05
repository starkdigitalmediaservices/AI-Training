"""
Calculator Agent - Network Ready Version
Supports communication across different systems
Port: 5001
"""

import math
import json
import socket
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NetworkCalculatorAgent:
    def __init__(self, agent_id="calculator_agent"):
        self.agent_id = agent_id
        self.port = int(os.getenv('CALCULATOR_PORT', 5001))
        self.host = '0.0.0.0'
        self.my_ip = self.get_local_ip()
        unit_host = os.getenv('UNIT_CONVERTER_HOST', 'localhost')
        unit_port = os.getenv('UNIT_CONVERTER_PORT', 5002)
        stats_host = os.getenv('STATISTICS_HOST', 'localhost')
        stats_port = os.getenv('STATISTICS_PORT', 5003)
        self.unit_converter_url = os.getenv('UNIT_CONVERTER_URL') or f"http://{unit_host}:{unit_port}"
        self.statistics_url = os.getenv('STATISTICS_URL') or f"http://{stats_host}:{stats_port}"
        print(f"🧮 Calculator Agent initialized")
        print(f"📍 My IP: {self.my_ip}:{self.port}")
        print(f"🔗 Unit Converter: {self.unit_converter_url}")
        print(f"📊 Statistics Agent: {self.statistics_url}")
        
    def get_local_ip(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            return ip
        except Exception:
            return "127.0.0.1"
    
    def add(self, numbers):
        try:
            result = sum(numbers)
            return {"success": True, "result": result, "operation": "addition"}
        except Exception as e:
            return {"success": False, "error": f"Addition failed: {str(e)}"}
    
    def subtract(self, numbers):
        try:
            result = numbers[0]
            for num in numbers[1:]:
                result -= num
            return {"success": True, "result": result, "operation": "subtraction"}
        except Exception as e:
            return {"success": False, "error": f"Subtraction failed: {str(e)}"}
    
    def multiply(self, numbers):
        try:
            result = 1
            for num in numbers:
                result *= num
            return {"success": True, "result": result, "operation": "multiplication"}
        except Exception as e:
            return {"success": False, "error": f"Multiplication failed: {str(e)}"}
    
    def divide(self, numbers):
        try:
            if 0 in numbers[1:]:
                return {"success": False, "error": "Division by zero not allowed"}
            result = numbers[0]
            for num in numbers[1:]:
                result /= num
            return {"success": True, "result": result, "operation": "division"}
        except Exception as e:
            return {"success": False, "error": f"Division failed: {str(e)}"}
    
    def power(self, base, exponent):
        try:
            result = base ** exponent
            return {"success": True, "result": result, "operation": f"power ({base}^{exponent})"}
        except Exception as e:
            return {"success": False, "error": f"Power calculation failed: {str(e)}"}
    
    def square_root(self, number):
        try:
            if number < 0:
                return {"success": False, "error": "Cannot calculate square root of negative number"}
            result = math.sqrt(number)
            return {"success": True, "result": result, "operation": f"square_root of {number}"}
        except Exception as e:
            return {"success": False, "error": f"Square root calculation failed: {str(e)}"}
    
    def percentage(self, value, percentage):
        try:
            result = (value * percentage) / 100
            return {"success": True, "result": result, "operation": f"{percentage}% of {value}"}
        except Exception as e:
            return {"success": False, "error": f"Percentage calculation failed: {str(e)}"}
    
    def process_request(self, operation, data):
        if operation == "add":
            return self.add(data.get("numbers", []))
        elif operation == "subtract":
            return self.subtract(data.get("numbers", []))
        elif operation == "multiply":
            return self.multiply(data.get("numbers", []))
        elif operation == "divide":
            return self.divide(data.get("numbers", []))
        elif operation == "power":
            return self.power(data.get("base", 0), data.get("exponent", 0))
        elif operation == "square_root":
            return self.square_root(data.get("number", 0))
        elif operation == "percentage":
            return self.percentage(data.get("value", 0), data.get("percentage", 0))
        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}

app = Flask(__name__)
CORS(app)
calculator = NetworkCalculatorAgent()

AGENT_CONFIG = {
    "calculator_url": f"http://{calculator.my_ip}:{calculator.port}",
    "unit_url": calculator.unit_converter_url,
    "statistics_url": calculator.statistics_url,
}

def _inject_result_for_next(operation: str, data: dict, local_result):
    data = dict(data or {})
    if 'value' not in data:
        data['value'] = local_result
    if operation in {"mean", "median", "mode", "standard_deviation", "range"}:
        nums = data.get('numbers')
        if isinstance(nums, list):
            data['numbers'] = [local_result] + nums
    return data

# Orchestrated forwarding to collect per-step outputs
def _forward_chain(next_hop: dict, incoming: dict, local_result, trace: list, steps: list):
    if not next_hop or not isinstance(next_hop, dict):
        return {
            "agent": calculator.agent_id,
            "server_ip": calculator.my_ip,
            "response": {"result": local_result, "success": True},
            "correlation_id": incoming.get('correlation_id'),
            "trace": trace,
            "timestamp": datetime.now().isoformat(),
            "steps": steps,
            "final": local_result,
        }

    url = next_hop.get('url')
    handoff = next_hop.get('handoff', {})
    next_next = next_hop.get('next')

    if url and url.rstrip('/').endswith('/convert'):
        payload = {
            "value": local_result,
            "from_unit": handoff.get('from_unit') or handoff.get('from') or handoff.get('fromUnit'),
            "to_unit": handoff.get('to_unit') or handoff.get('to') or handoff.get('toUnit')
        }
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        body = resp.json()
        next_result = body.get('response', {}).get('result')
        steps.append({
            "agent": body.get('agent', 'unit_converter_agent'),
            "operation": body.get('response', {}).get('operation'),
            "result": next_result
        })
        return _forward_chain(next_next, incoming, next_result, trace + [f"{calculator.agent_id}@{calculator.my_ip}:{calculator.port}"], steps)

    # Default: call /message without passing nested next; orchestrate locally for step collection
    message = handoff if isinstance(handoff, dict) else {}
    op = message.get('operation')
    data = message.get('data', {})
    data = _inject_result_for_next(op or '', data, local_result)
    envelope = {
        "sender": calculator.agent_id,
        "correlation_id": incoming.get('correlation_id'),
        "trace": trace + [f"{calculator.agent_id}@{calculator.my_ip}:{calculator.port}"],
        "message": {"operation": op, "data": data}
    }
    resp = requests.post(url, json=envelope, timeout=10)
    resp.raise_for_status()
    body = resp.json()
    next_result = body.get('response', {}).get('result')
    steps.append({
        "agent": body.get('agent', 'unknown_agent'),
        "operation": body.get('response', {}).get('operation'),
        "result": next_result
    })
    return _forward_chain(next_next, incoming, next_result, trace + [f"{calculator.agent_id}@{calculator.my_ip}:{calculator.port}"], steps)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/config/agents', methods=['GET', 'PUT'])
def config_agents():
    if request.method == 'GET':
        return jsonify(AGENT_CONFIG)
    try:
        data = request.get_json() or {}
        for k in ["calculator_url", "unit_url", "statistics_url"]:
            if k in data and isinstance(data[k], str) and data[k]:
                AGENT_CONFIG[k] = data[k].rstrip('/')
        return jsonify({"ok": True, "config": AGENT_CONFIG})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@app.route('/config/test', methods=['POST'])
def config_test():
    results = {}
    for key, base in AGENT_CONFIG.items():
        try:
            r = requests.get(f"{base}/health", timeout=5)
            results[key] = {"ok": r.status_code == 200}
        except Exception as e:
            results[key] = {"ok": False, "error": str(e)}
    return jsonify(results)

@app.route('/route', methods=['POST'])
def route_proxy():
    try:
        body = request.get_json() or {}
        target = body.get('target')
        endpoint = body.get('endpoint', '/message')
        payload = body.get('payload', {})
        if target not in ["calculator", "unit", "statistics"]:
            return jsonify({"error": "invalid target"}), 400
        base = AGENT_CONFIG["calculator_url" if target == "calculator" else ("unit_url" if target == "unit" else "statistics_url")]
        url = f"{base}{endpoint if endpoint.startswith('/') else '/' + endpoint}"
        resp = requests.post(url, json=payload, timeout=15)
        return jsonify(resp.json()), resp.status_code
    except requests.RequestException as e:
        return jsonify({"error": f"proxy failed: {str(e)}"}), 502

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "agent": "calculator_agent",
        "ip": calculator.my_ip,
        "port": calculator.port,
        "timestamp": datetime.now().isoformat(),
        "connected_agents": {
            "unit_converter": calculator.unit_converter_url,
            "statistics": calculator.statistics_url
        }
    })

@app.route('/network-info', methods=['GET'])
def network_info():
    """Return network information for debugging"""
    return jsonify({
        "my_ip": calculator.my_ip,
        "my_port": calculator.port,
        "my_url": f"http://{calculator.my_ip}:{calculator.port}",
        "other_agents": {
            "unit_converter": calculator.unit_converter_url,
            "statistics": calculator.statistics_url
        },
        "environment_variables": {
            "CALCULATOR_HOST": os.getenv('CALCULATOR_HOST', 'Not set'),
            "CALCULATOR_PORT": os.getenv('CALCULATOR_PORT', 'Not set'),
            "UNIT_CONVERTER_HOST": os.getenv('UNIT_CONVERTER_HOST', 'Not set'),
            "STATISTICS_HOST": os.getenv('STATISTICS_HOST', 'Not set')
        }
    })

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        operation = data.get('operation')
        request_data = data.get('data', {})
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        print(f"📨 Calculation request from {client_ip}: {operation}")
        result = calculator.process_request(operation, request_data)
        return jsonify({
            "agent": "calculator_agent",
            "server_ip": calculator.my_ip,
            "request": data,
            "response": result,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "agent": "calculator_agent",
            "error": f"Request processing failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 400

@app.route('/message', methods=['POST'])
def receive_message():
    try:
        incoming = request.get_json()
        sender = incoming.get('sender', 'unknown')
        message = incoming.get('message', {})
        next_hop = incoming.get('next')
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        print(f"🤖 Message from {sender} ({client_ip})")
        operation = message.get('operation')
        request_data = message.get('data', {})
        local = calculator.process_request(operation, request_data)
        steps = [
            {"agent": calculator.agent_id, "operation": operation, "result": local.get('result')}
        ] if local.get('success') else []
        if next_hop and local.get('success'):
            aggregated = _forward_chain(next_hop, incoming, local.get('result'), incoming.get('trace', []), steps)
            return jsonify(aggregated)
        return jsonify({
            "agent": "calculator_agent",
            "server_ip": calculator.my_ip,
            "sender": sender,
            "response": local,
            "correlation_id": incoming.get('correlation_id'),
            "trace": incoming.get('trace', []) + [f"{calculator.agent_id}@{calculator.my_ip}:{calculator.port}"],
            "steps": steps,
            "final": local.get('result') if local.get('success') else None,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "agent": "calculator_agent",
            "error": f"Message processing failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 400

def test_network_connectivity():
    print("\n🌐 Testing Network Connectivity...")
    agents_to_test = {
        "Unit Converter": calculator.unit_converter_url,
        "Statistics": calculator.statistics_url
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
    print("🧮 Testing Calculator Agent...")
    tests = [
        {"operation": "add", "data": {"numbers": [10, 20, 30]}},
        {"operation": "multiply", "data": {"numbers": [4, 5, 2]}},
        {"operation": "square_root", "data": {"number": 16}},
        {"operation": "percentage", "data": {"value": 150, "percentage": 20}}
    ]
    for test in tests:
        result = calculator.process_request(test["operation"], test["data"])
        print(f"✅ {test['operation']}: {result.get('result', 'Error')}")

if __name__ == '__main__':
    print("🧮 Network Calculator Agent Starting...")
    test_agent()
    test_network_connectivity()
    print(f"\n🚀 Server starting on {calculator.host}:{calculator.port}")
    print(f"📍 Access from other systems: http://{calculator.my_ip}:{calculator.port}")
    app.run(host=calculator.host, port=calculator.port, debug=True)
