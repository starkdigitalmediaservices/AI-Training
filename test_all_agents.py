"""
Test script for all three math agents
Run this after starting all agents to test communication
"""

import requests
import json
import time
from datetime import datetime

class MathAgentsTester:
    def __init__(self):
        self.agents = {
            'calculator': 'http://localhost:5001',
            'unit_converter': 'http://localhost:5002',
            'statistics': 'http://localhost:5003'
        }
    
    def check_agent_health(self, agent_name):
        """Check if an agent is online"""
        try:
            response = requests.get(f"{self.agents[agent_name]}/health", timeout=3)
            if response.status_code == 200:
                print(f"✅ {agent_name} is online")
                return True
            else:
                print(f"❌ {agent_name} is offline (status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ {agent_name} is offline (error: {str(e)})")
            return False
    
    def test_calculator_agent(self):
        """Test calculator agent individually"""
        print("\n🧮 Testing Calculator Agent")
        print("-" * 30)
        
        tests = [
            {
                "name": "Addition",
                "data": {"operation": "add", "data": {"numbers": [10, 20, 30]}}
            },
            {
                "name": "Multiplication", 
                "data": {"operation": "multiply", "data": {"numbers": [4, 5, 2]}}
            },
            {
                "name": "Square Root",
                "data": {"operation": "square_root", "data": {"number": 16}}
            },
            {
                "name": "Percentage",
                "data": {"operation": "percentage", "data": {"value": 150, "percentage": 20}}
            }
        ]
        
        for test in tests:
            try:
                response = requests.post(
                    f"{self.agents['calculator']}/calculate",
                    json=test["data"],
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("response", {}).get("result", "No result")
                    print(f"✅ {test['name']}: {answer}")
                else:
                    print(f"❌ {test['name']}: Failed (status: {response.status_code})")
            except Exception as e:
                print(f"❌ {test['name']}: Error - {str(e)}")
    
    def test_unit_converter_agent(self):
        """Test unit converter agent individually"""
        print("\n🔄 Testing Unit Converter Agent")
        print("-" * 35)
        
        tests = [
            {
                "name": "Length (meter to feet)",
                "data": {"value": 10, "from_unit": "meter", "to_unit": "feet"}
            },
            {
                "name": "Temperature (celsius to fahrenheit)",
                "data": {"value": 25, "from_unit": "celsius", "to_unit": "fahrenheit"}
            },
            {
                "name": "Weight (kilogram to pound)",
                "data": {"value": 5, "from_unit": "kilogram", "to_unit": "pound"}
            }
        ]
        
        for test in tests:
            try:
                response = requests.post(
                    f"{self.agents['unit_converter']}/convert",
                    json=test["data"],
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("response", {}).get("result", "No result")
                    from_val = test["data"]["value"]
                    from_unit = test["data"]["from_unit"]
                    to_unit = test["data"]["to_unit"]
                    print(f"✅ {test['name']}: {from_val} {from_unit} = {answer:.2f} {to_unit}")
                else:
                    print(f"❌ {test['name']}: Failed (status: {response.status_code})")
            except Exception as e:
                print(f"❌ {test['name']}: Error - {str(e)}")
    
    def test_statistics_agent(self):
        """Test statistics agent individually"""
        print("\n📊 Testing Statistics Agent")
        print("-" * 30)
        
        test_data = [10, 15, 20, 25, 30, 25, 15]
        
        tests = [
            {
                "name": "Mean (Average)",
                "data": {"operation": "mean", "data": {"numbers": test_data}}
            },
            {
                "name": "Median",
                "data": {"operation": "median", "data": {"numbers": test_data}}
            },
            {
                "name": "Mode",
                "data": {"operation": "mode", "data": {"numbers": test_data}}
            },
            {
                "name": "Range",
                "data": {"operation": "range", "data": {"numbers": test_data}}
            }
        ]
        
        print(f"Test data: {test_data}")
        
        for test in tests:
            try:
                response = requests.post(
                    f"{self.agents['statistics']}/stats",
                    json=test["data"],
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("response", {}).get("result", "No result")
                    print(f"✅ {test['name']}: {answer}")
                else:
                    print(f"❌ {test['name']}: Failed (status: {response.status_code})")
            except Exception as e:
                print(f"❌ {test['name']}: Error - {str(e)}")
    
    def test_inter_agent_communication(self):
        """Test agents communicating with each other"""
        print("\n🤝 Testing Inter-Agent Communication")
        print("-" * 40)
        
        # Test 1: Unit Converter calling Calculator
        print("Test 1: Unit Converter → Calculator")
        try:
            # Simulate unit converter asking calculator to do math
            response = requests.post(
                f"{self.agents['calculator']}/message",
                json={
                    "sender": "unit_converter_agent",
                    "message": {
                        "operation": "multiply",
                        "data": {"numbers": [10, 3.28084]}  # 10 meters to feet
                    }
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", {}).get("result", "No result")
                print(f"✅ Unit Converter asked Calculator: 10 × 3.28084 = {answer}")
            else:
                print("❌ Unit Converter → Calculator: Failed")
        except Exception as e:
            print(f"❌ Unit Converter → Calculator: Error - {str(e)}")
        
        # Test 2: Statistics calling Calculator
        print("\nTest 2: Statistics → Calculator")
        try:
            response = requests.post(
                f"{self.agents['calculator']}/message",
                json={
                    "sender": "statistics_agent",
                    "message": {
                        "operation": "add",
                        "data": {"numbers": [10, 20, 30, 40]}
                    }
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", {}).get("result", "No result")
                print(f"✅ Statistics asked Calculator: sum([10,20,30,40]) = {answer}")
            else:
                print("❌ Statistics → Calculator: Failed")
        except Exception as e:
            print(f"❌ Statistics → Calculator: Error - {str(e)}")
    
    def test_complex_workflow(self):
        """Test a complex workflow involving all agents"""
        print("\n🎯 Testing Complex Workflow")
        print("-" * 35)
        
        print("Scenario: Calculate average temperature in Fahrenheit, then convert to Celsius")
        temp_data_f = [68, 72, 75, 70, 73]  # Temperatures in Fahrenheit
        
        # Step 1: Calculate average using Statistics agent
        print(f"Step 1: Calculate average of {temp_data_f} °F")
        try:
            stats_response = requests.post(
                f"{self.agents['statistics']}/stats",
                json={"operation": "mean", "data": {"numbers": temp_data_f}},
                timeout=5
            )
            
            if stats_response.status_code == 200:
                avg_result = stats_response.json()
                avg_temp_f = avg_result.get("response", {}).get("result", 0)
                print(f"✅ Average temperature: {avg_temp_f} °F")
                
                # Step 2: Convert average to Celsius using Unit Converter
                print(f"Step 2: Convert {avg_temp_f} °F to Celsius")
                
                convert_response = requests.post(
                    f"{self.agents['unit_converter']}/convert",
                    json={"value": avg_temp_f, "from_unit": "fahrenheit", "to_unit": "celsius"},
                    timeout=5
                )
                
                if convert_response.status_code == 200:
                    convert_result = convert_response.json()
                    avg_temp_c = convert_result.get("response", {}).get("result", 0)
                    print(f"✅ Final result: {avg_temp_c:.2f} °C")
                    print(f"🎉 Complex workflow completed successfully!")
                else:
                    print("❌ Step 2 failed: Unit conversion")
            else:
                print("❌ Step 1 failed: Statistics calculation")
                
        except Exception as e:
            print(f"❌ Complex workflow failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Math Agents System Test")
        print("=" * 50)
        
        # Check agent health first
        print("Checking agent status...")
        online_agents = []
        for agent in self.agents.keys():
            if self.check_agent_health(agent):
                online_agents.append(agent)
        
        if len(online_agents) < 3:
            print(f"\n⚠️ Warning: Only {len(online_agents)}/3 agents are online")
            print("Make sure to start all agents before running tests!")
        
        # Run individual tests
        if 'calculator' in online_agents:
            self.test_calculator_agent()
        
        if 'unit_converter' in online_agents:
            self.test_unit_converter_agent()
        
        if 'statistics' in online_agents:
            self.test_statistics_agent()
        
        # Run communication tests
        if len(online_agents) >= 2:
            self.test_inter_agent_communication()
        
        # Run complex workflow test
        if len(online_agents) == 3:
            self.test_complex_workflow()
        
        print(f"\n✨ Testing completed! {len(online_agents)}/3 agents tested.")

def main():
    tester = MathAgentsTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
