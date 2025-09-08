"""
Unit Converter Agent - Network Ready Version
Supports communication across different systems
Port: 5002
"""

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

class NetworkUnitConverterAgent:
    def __init__(self, agent_id="unit_converter_agent"):
        self.agent_id = agent_id
        self.port = int(os.getenv('UNIT_CONVERTER_PORT', 5002))
        self.host = '0.0.0.0'  # Listen on all interfaces
        
        # Get my actual IP address
        self.my_ip = self.get_local_ip()
        
        # Other agents' addresses (from environment variables)
        self.calculator_url = f"http://{os.getenv('CALCULATOR_HOST', 'localhost')}:{os.getenv('CALCULATOR_PORT', 5001)}"
        self.statistics_url = f"http://{os.getenv('STATISTICS_HOST', 'localhost')}:{os.getenv('STATISTICS_PORT', 5003)}"
        
        print(f"🔄 Unit Converter Agent initialized")
        print(f"📍 My IP: {self.my_ip}:{self.port}")
        print(f"🧮 Calculator: {self.calculator_url}")
        print(f"📊 Statistics Agent: {self.statistics_url}")
        
        # Conversion factors (to base units)
        self.conversions = {
            'length': {
                'meter': 1.0,
                'feet': 0.3048,
                'inch': 0.0254,
                'centimeter': 0.01,
                'kilometer': 1000.0,
                'yard': 0.9144,
                'mile': 1609.34
            },
            'weight': {
                'kilogram': 1.0,
                'pound': 0.453592,
                'gram': 0.001,
                'ounce': 0.0283495,
                'ton': 1000.0
            },
            'temperature': {
                'celsius': {'type': 'special'},
                'fahrenheit': {'type': 'special'},
                'kelvin': {'type': 'special'}
            },
            'volume': {
                'liter': 1.0,
                'gallon': 3.78541,
                'milliliter': 0.001,
                'cup': 0.236588,
                'pint': 0.473176
            }
        }
    
    def get_local_ip(self):
        """Get the local IP address of this machine"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            return ip
        except Exception:
            return "127.0.0.1"
    
    def find_unit_category(self, unit):
        """Find which category a unit belongs to"""
        for category, units in self.conversions.items():
            if unit.lower() in units:
                return category
        return None
    
    def convert_temperature(self, value, from_unit, to_unit):
        """Special handling for temperature conversions"""
        try:
            # First convert to Celsius
            if from_unit.lower() == 'fahrenheit':
                celsius = (value - 32) * 5/9
            elif from_unit.lower() == 'kelvin':
                celsius = value - 273.15
            else:  # already celsius
                celsius = value
            
            # Then convert from Celsius to target
            if to_unit.lower() == 'fahrenheit':
                result = (celsius * 9/5) + 32
            elif to_unit.lower() == 'kelvin':
                result = celsius + 273.15
            else:  # stay in celsius
                result = celsius
            
            return {
                "success": True,
                "result": result,
                "from_value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "operation": f"temperature_conversion"
            }
        except Exception as e:
            return {"success": False, "error": f"Temperature conversion failed: {str(e)}"}
    
    def convert_units(self, value, from_unit, to_unit):
        """Convert between units"""
        try:
            from_category = self.find_unit_category(from_unit)
            to_category = self.find_unit_category(to_unit)
            
            if not from_category or not to_category:
                return {"success": False, "error": f"Unknown unit: {from_unit} or {to_unit}"}
            
            if from_category != to_category:
                return {"success": False, "error": f"Cannot convert between {from_category} and {to_category}"}
            
            # Handle temperature separately
            if from_category == 'temperature':
                return self.convert_temperature(value, from_unit, to_unit)
            
            # Standard conversion using calculator agent
            from_factor = self.conversions[from_category][from_unit.lower()]
            to_factor = self.conversions[to_category][to_unit.lower()]
            
            # Use calculator agent for the math
            calc_result = self.call_calculator("multiply", {"numbers": [value, from_factor]})
            if not calc_result.get("success"):
                return calc_result
            
            base_value = calc_result["result"]
            
            # Convert from base to target unit
            division_result = self.call_calculator("divide", {"numbers": [base_value, to_factor]})
            if not division_result.get("success"):
                return division_result
            
            result = division_result["result"]
            
            return {
                "success": True,
                "result": result,
                "from_value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "operation": f"{from_unit}_to_{to_unit}"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Unit conversion failed: {str(e)}"}
    
    def call_calculator(self, operation, data):
        """Call the calculator agent for math operations"""
        try:
            print(f"📞 Calling Calculator: {operation} with {data}")
            
            response = requests.post(
                f"{self.calculator_url}/message",
                json={
                    "sender": self.agent_id,
                    "message": {
                        "operation": operation,
                        "data": data
                    }
                },
                timeout=10  # Longer timeout for network calls
            )
            
            if response.status_code == 200:
                result = response.json()
                calc_response = result.get("response", {})
                print(f"✅ Calculator responded: {calc_response.get('result')}")
                return calc_response
            else:
                print(f"❌ Calculator error: {response.status_code}")
                return {"success": False, "error": "Calculator agent not responding"}
                
        except Exception as e:
            print(f"❌ Calculator communication failed: {str(e)}")
            # Fallback to local calculation if calculator is down
            if operation == "multiply" and len(data.get("numbers", [])) == 2:
                nums = data["numbers"]
                result = nums[0] * nums[1]
                print(f"🔄 Using local fallback: {nums[0]} × {nums[1]} = {result}")
                return {"success": True, "result": result, "operation": "local_multiply"}
            elif operation == "divide" and len(data.get("numbers", [])) == 2:
                nums = data["numbers"]
                if nums[1] != 0:
                    result = nums[0] / nums[1]
                    print(f"🔄 Using local fallback: {nums[0]} ÷ {nums[1]} = {result}")
                    return {"success": True, "result": result, "operation": "local_divide"}
            
            return {"success": False, "error": f"Calculator communication failed: {str(e)}"}
    
    def get_available_units(self):
        """Return list of all supported units"""
        all_units = {}
        for category, units in self.conversions.items():
            all_units[category] = list(units.keys())
        return all_units

# Flask server setup with CORS for cross-system communication
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing
converter = NetworkUnitConverterAgent()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "agent": "unit_converter_agent",
        "ip": converter.my_ip,
        "port": converter.port,
        "timestamp": datetime.now().isoformat(),
        "connected_agents": {
            "calculator": converter.calculator_url,
            "statistics": converter.statistics_url
        }
    })

@app.route('/network-info', methods=['GET'])
def network_info():
    """Return network information for debugging"""
    return jsonify({
        "my_ip": converter.my_ip,
        "my_port": converter.port,
        "my_url": f"http://{converter.my_ip}:{converter.port}",
        "other_agents": {
            "calculator": converter.calculator_url,
            "statistics": converter.statistics_url
        },
        "environment_variables": {
            "UNIT_CONVERTER_HOST": os.getenv('UNIT_CONVERTER_HOST', 'Not set'),
            "UNIT_CONVERTER_PORT": os.getenv('UNIT_CONVERTER_PORT', 'Not set'),
            "CALCULATOR_HOST": os.getenv('CALCULATOR_HOST', 'Not set'),
            "STATISTICS_HOST": os.getenv('STATISTICS_HOST', 'Not set')
        }
    })

@app.route('/convert', methods=['POST'])
def convert_units():
    """Direct conversion endpoint"""
    try:
        data = request.get_json()
        value = data.get('value')
        from_unit = data.get('from_unit')
        to_unit = data.get('to_unit')
        
        # Log the request with source IP
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        print(f"📨 Conversion request from {client_ip}: {value} {from_unit} → {to_unit}")
        
        result = converter.convert_units(value, from_unit, to_unit)
        
        return jsonify({
            "agent": "unit_converter_agent",
            "server_ip": converter.my_ip,
            "request": data,
            "response": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "agent": "unit_converter_agent",
            "error": f"Request processing failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 400

@app.route('/units', methods=['GET'])
def get_units():
    """Get available units"""
    return jsonify({
        "agent": "unit_converter_agent",
        "available_units": converter.get_available_units(),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def index():
    """Serve the Unit Converter UI template"""
    return render_template('index.html')

@app.route('/calculator', methods=['POST'])
def calculator_api():
    """Basic calculator API used by the UI (add, subtract, multiply, divide)"""
    try:
        data = request.get_json(force=True)
        a = float(data.get('a', 0))
        b = float(data.get('b', 0))
        operation = (data.get('operation') or '').lower()

        if operation == 'add':
            result = a + b
        elif operation == 'subtract':
            result = a - b
        elif operation == 'multiply':
            result = a * b
        elif operation == 'divide':
            if b == 0:
                return jsonify({"success": False, "error": "Division by zero"}), 400
            result = a / b
        else:
            return jsonify({"success": False, "error": "Unsupported operation"}), 400

        return jsonify({
            "success": True,
            "result": result,
            "operation": operation
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Calculation failed: {str(e)}"}), 400

@app.route('/message', methods=['POST'])
def receive_message():
    """Inter-agent communication endpoint (A2A protocol)"""
    try:
        incoming = request.get_json()
        sender = incoming.get('sender', 'unknown')
        message = incoming.get('message', {})
        
        # Log the inter-agent communication
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        print(f"🤖 Message from {sender} ({client_ip})")
        
        # Handle different message formats for unit conversion
        value = message.get('value')
        from_unit = message.get('from_unit') or message.get('from') or message.get('fromUnit')
        to_unit = message.get('to_unit') or message.get('to') or message.get('toUnit')
        
        result = converter.convert_units(value, from_unit, to_unit)
        
        return jsonify({
            "agent": "unit_converter_agent",
            "server_ip": converter.my_ip,
            "sender": sender,
            "response": result,
            "correlation_id": incoming.get('correlation_id'),
            "trace": incoming.get('trace', []) + [f"{converter.agent_id}@{converter.my_ip}:{converter.port}"],
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "agent": "unit_converter_agent",
            "error": f"Message processing failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 400

def test_network_connectivity():
    """Test connectivity to other agents"""
    print("\n🌐 Testing Network Connectivity...")
    
    agents_to_test = {
        "Calculator": converter.calculator_url,
        "Statistics": converter.statistics_url
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
    """Test the unit converter agent"""
    print("🔄 Testing Unit Converter Agent...")
    
    tests = [
        {"value": 10, "from_unit": "meter", "to_unit": "feet"},
        {"value": 100, "from_unit": "celsius", "to_unit": "fahrenheit"},
        {"value": 5, "from_unit": "kilogram", "to_unit": "pound"}
    ]
    
    for test in tests:
        result = converter.convert_units(test["value"], test["from_unit"], test["to_unit"])
        if result.get("success"):
            print(f"✅ {test['value']} {test['from_unit']} = {result.get('result', 'Error'):.2f} {test['to_unit']}")
        else:
            print(f"❌ {test}: {result.get('error', 'Unknown error')}")

if __name__ == '__main__':
    print("🔄 Network Unit Converter Agent Starting...")
    
    # Test local functionality
    test_agent()
    
    # Test network connectivity
    test_network_connectivity()
    
    print(f"\n🚀 Server starting on {converter.host}:{converter.port}")
    print(f"📍 Access from other systems: http://{converter.my_ip}:{converter.port}")
    
    # Run Flask app
    app.run(host=converter.host, port=converter.port, debug=True)
