#!/usr/bin/env python3
"""
System Test Script
Tests the complete multi-agent system functionality
"""

import requests
import json
import time
import sys

def test_agent_health():
    """Test if all agents are healthy"""
    print("🔍 Testing Agent Health...")
    
    agents = {
        "Calculator": "http://localhost:5001/health",
        "Unit Converter": "http://localhost:5002/health", 
        "Statistics": "http://localhost:5003/health"
    }
    
    all_healthy = True
    for name, url in agents.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: {data['status']} on port {data['port']}")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            all_healthy = False
    
    return all_healthy

def test_calculator_agent():
    """Test calculator agent functionality"""
    print("\n🧮 Testing Calculator Agent...")
    
    tests = [
        {"operation": "add", "data": {"numbers": [10, 20, 30]}},
        {"operation": "multiply", "data": {"numbers": [5, 4]}},
        {"operation": "power", "data": {"base": 2, "exponent": 3}}
    ]
    
    for test in tests:
        try:
            response = requests.post(
                "http://localhost:5001/calculate",
                json=test,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                result = data['response']['result']
                print(f"✅ {test['operation']}: {result}")
            else:
                print(f"❌ {test['operation']}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {test['operation']}: {str(e)}")

def test_unit_converter_agent():
    """Test unit converter agent functionality"""
    print("\n🔄 Testing Unit Converter Agent...")
    
    tests = [
        {"value": 10, "from_unit": "meter", "to_unit": "feet"},
        {"value": 100, "from_unit": "celsius", "to_unit": "fahrenheit"},
        {"value": 5, "from_unit": "kilogram", "to_unit": "pound"}
    ]
    
    for test in tests:
        try:
            response = requests.post(
                "http://localhost:5002/convert",
                json=test,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                result = data['response']['result']
                print(f"✅ {test['value']} {test['from_unit']} → {result:.2f} {test['to_unit']}")
            else:
                print(f"❌ {test['from_unit']} to {test['to_unit']}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {test['from_unit']} to {test['to_unit']}: {str(e)}")

def test_statistics_agent():
    """Test statistics agent functionality"""
    print("\n📊 Testing Statistics Agent...")
    
    tests = [
        {"operation": "mean", "data": {"numbers": [10, 20, 30]}},
        {"operation": "median", "data": {"numbers": [1, 2, 3, 4, 5]}},
        {"operation": "mode", "data": {"numbers": [1, 2, 2, 3, 3, 3]}}
    ]
    
    for test in tests:
        try:
            response = requests.post(
                "http://localhost:5003/message",
                json={
                    "sender": "test_system",
                    "message": test
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                result = data['response']['result']
                print(f"✅ {test['operation']}: {result}")
            else:
                print(f"❌ {test['operation']}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {test['operation']}: {str(e)}")

def test_a2a_communication():
    """Test A2A communication between agents"""
    print("\n🤖 Testing A2A Communication...")
    
    # Test calculator → unit converter communication
    try:
        # First get a result from calculator
        calc_response = requests.post(
            "http://localhost:5001/message",
            json={
                "sender": "test_system",
                "correlation_id": "test-123",
                "trace": ["test_system"],
                "message": {
                    "operation": "add",
                    "data": {"numbers": [10, 20]}
                }
            },
            timeout=5
        )
        
        if calc_response.status_code == 200:
            calc_data = calc_response.json()
            calc_result = calc_data['response']['result']
            print(f"✅ Calculator A2A: {calc_result}")
            
            # Now test unit converter with the result
            unit_response = requests.post(
                "http://localhost:5002/message",
                json={
                    "sender": "test_system",
                    "correlation_id": "test-123",
                    "trace": calc_data['trace'],
                    "message": {
                        "operation": "convert",
                        "data": {
                            "value": calc_result,
                            "from_unit": "meter",
                            "to_unit": "feet"
                        }
                    }
                },
                timeout=5
            )
            
            if unit_response.status_code == 200:
                unit_data = unit_response.json()
                unit_result = unit_data['response']['result']
                print(f"✅ Unit Converter A2A: {unit_result:.2f} feet")
            else:
                print(f"❌ Unit Converter A2A: HTTP {unit_response.status_code}")
        else:
            print(f"❌ Calculator A2A: HTTP {calc_response.status_code}")
            
    except Exception as e:
        print(f"❌ A2A Communication: {str(e)}")

def test_pipeline_orchestrator():
    """Test the pipeline orchestrator"""
    print("\n🔄 Testing Pipeline Orchestrator...")
    
    import subprocess
    
    try:
        result = subprocess.run([
            "python3", "pipeline_orchestrator.py",
            "--numbers", "10,20,30",
            "--from-unit", "meter", 
            "--to-unit", "feet",
            "--stats-op", "mean"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Pipeline Orchestrator: Success")
            # Extract final result from output
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith("✔ Final output:"):
                    print(f"   {line}")
                    break
        else:
            print(f"❌ Pipeline Orchestrator: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Pipeline Orchestrator: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Multi-Agent System Test Suite")
    print("=" * 40)
    
    # Test 1: Health checks
    if not test_agent_health():
        print("\n❌ Health checks failed. Please ensure all agents are running.")
        print("Run: ./start_agents.sh start")
        sys.exit(1)
    
    # Test 2: Individual agent functionality
    test_calculator_agent()
    test_unit_converter_agent()
    test_statistics_agent()
    
    # Test 3: A2A communication
    test_a2a_communication()
    
    # Test 4: Pipeline orchestrator
    test_pipeline_orchestrator()
    
    print("\n🎉 All tests completed!")
    print("\n📋 System Status:")
    print("  🧮 Calculator Agent: http://localhost:5001")
    print("  🔄 Unit Converter Agent: http://localhost:5002")
    print("  📊 Statistics Agent: http://localhost:5003")
    print("\n🌐 Web Interfaces:")
    print("  🧮 Calculator UI: http://localhost:5001/")
    print("  🔄 Unit Converter UI: http://localhost:5002/")
    print("  📊 Statistics UI: http://localhost:5003/")

if __name__ == "__main__":
    main()
