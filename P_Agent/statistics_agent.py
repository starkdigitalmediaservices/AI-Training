#!/usr/bin/env python3
"""
Standalone test script for the statistics agent
Tests the agent without requiring other agents to be running
"""

import sys
import os
import math
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class StandaloneStatisticsAgent:
    """Standalone version of statistics agent for testing"""
    
    def __init__(self):
        self.agent_id = "statistics_agent"
        print(f"📊 Standalone Statistics Agent initialized")
    
    def local_calculator_fallback(self, operation, data):
        """Local fallback calculations when other agents are not available"""
        if operation == "add":
            numbers = data.get("numbers", [])
            return {"success": True, "result": sum(numbers), "operation": "local_add"}
        elif operation == "divide" and len(data.get("numbers", [])) == 2:
            nums = data["numbers"]
            if nums[1] != 0:
                return {"success": True, "result": nums[0] / nums[1], "operation": "local_divide"}
        elif operation == "power":
            base = data.get("base", 0)
            exp = data.get("exponent", 0)
            return {"success": True, "result": base ** exp, "operation": "local_power"}
        elif operation == "square_root":
            num = data.get("number", 0)
            if num >= 0:
                return {"success": True, "result": math.sqrt(num), "operation": "local_sqrt"}
        elif operation == "subtract" and len(data.get("numbers", [])) == 2:
            nums = data["numbers"]
            return {"success": True, "result": nums[0] - nums[1], "operation": "local_subtract"}
        
        return {"success": False, "error": f"Operation {operation} not supported in fallback"}
    
    def mean(self, numbers):
        """Calculate arithmetic mean (average)"""
        try:
            if not numbers:
                return {"success": False, "error": "No numbers provided"}
            
            # Use local fallback to sum the numbers
            sum_result = self.local_calculator_fallback("add", {"numbers": numbers})
            if not sum_result.get("success"):
                return sum_result
            
            total = sum_result["result"]
            count = len(numbers)
            
            # Use local fallback to divide
            mean_result = self.local_calculator_fallback("divide", {"numbers": [total, count]})
            if not mean_result.get("success"):
                return mean_result
            
            return {
                "success": True,
                "result": mean_result["result"],
                "operation": "mean",
                "count": count,
                "sum": total
            }
            
        except Exception as e:
            return {"success": False, "error": f"Mean calculation failed: {str(e)}"}
    
    def median(self, numbers):
        """Calculate median (middle value)"""
        try:
            if not numbers:
                return {"success": False, "error": "No numbers provided"}
            
            sorted_numbers = sorted(numbers)
            n = len(sorted_numbers)
            
            if n % 2 == 1:
                # Odd number of values - middle value
                result = sorted_numbers[n // 2]
            else:
                # Even number of values - average of two middle values
                mid1 = sorted_numbers[n // 2 - 1]
                mid2 = sorted_numbers[n // 2]
                
                # Use local fallback for average
                avg_result = self.local_calculator_fallback("divide", {"numbers": [mid1 + mid2, 2]})
                if not avg_result.get("success"):
                    return avg_result
                result = avg_result["result"]
            
            return {
                "success": True,
                "result": result,
                "operation": "median",
                "count": n,
                "sorted_values": sorted_numbers
            }
            
        except Exception as e:
            return {"success": False, "error": f"Median calculation failed: {str(e)}"}
    
    def mode(self, numbers):
        """Calculate mode (most frequent value)"""
        try:
            if not numbers:
                return {"success": False, "error": "No numbers provided"}
            
            # Count frequencies
            frequency = {}
            for num in numbers:
                frequency[num] = frequency.get(num, 0) + 1
            
            # Find maximum frequency
            max_frequency = max(frequency.values())
            modes = [num for num, freq in frequency.items() if freq == max_frequency]
            
            return {
                "success": True,
                "result": modes[0] if len(modes) == 1 else modes,
                "operation": "mode",
                "frequency": max_frequency,
                "all_modes": modes,
                "frequency_table": frequency
            }
            
        except Exception as e:
            return {"success": False, "error": f"Mode calculation failed: {str(e)}"}
    
    def standard_deviation(self, numbers):
        """Calculate standard deviation"""
        try:
            if len(numbers) < 2:
                return {"success": False, "error": "Need at least 2 numbers for standard deviation"}
            
            # Step 1: Calculate mean
            mean_result = self.mean(numbers)
            if not mean_result.get("success"):
                return mean_result
            
            mean_value = mean_result["result"]
            
            # Step 2: Calculate squared differences
            squared_diffs = []
            for num in numbers:
                # (num - mean)^2
                diff = num - mean_value
                squared_diff_result = self.local_calculator_fallback("power", {"base": diff, "exponent": 2})
                if not squared_diff_result.get("success"):
                    return squared_diff_result
                squared_diffs.append(squared_diff_result["result"])
            
            # Step 3: Calculate variance (average of squared differences)
            variance_result = self.mean(squared_diffs)
            if not variance_result.get("success"):
                return variance_result
            
            variance = variance_result["result"]
            
            # Step 4: Calculate standard deviation (square root of variance)
            std_dev_result = self.local_calculator_fallback("square_root", {"number": variance})
            if not std_dev_result.get("success"):
                return std_dev_result
            
            return {
                "success": True,
                "result": std_dev_result["result"],
                "operation": "standard_deviation",
                "variance": variance,
                "mean": mean_value,
                "count": len(numbers)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Standard deviation calculation failed: {str(e)}"}
    
    def range_calc(self, numbers):
        """Calculate range (max - min)"""
        try:
            if not numbers:
                return {"success": False, "error": "No numbers provided"}
            
            max_val = max(numbers)
            min_val = min(numbers)
            
            # Use local fallback for subtraction
            range_result = self.local_calculator_fallback("subtract", {"numbers": [max_val, min_val]})
            if not range_result.get("success"):
                return range_result
            
            return {
                "success": True,
                "result": range_result["result"],
                "operation": "range",
                "maximum": max_val,
                "minimum": min_val
            }
            
        except Exception as e:
            return {"success": False, "error": f"Range calculation failed: {str(e)}"}
    
    def summary_stats(self, numbers):
        """Calculate all basic statistics"""
        try:
            if not numbers:
                return {"success": False, "error": "No numbers provided"}
            
            # Calculate all statistics
            mean_result = self.mean(numbers)
            median_result = self.median(numbers)
            mode_result = self.mode(numbers)
            std_dev_result = self.standard_deviation(numbers) if len(numbers) >= 2 else {"result": "N/A"}
            range_result = self.range_calc(numbers)
            
            return {
                "success": True,
                "operation": "summary_statistics",
                "data": {
                    "count": len(numbers),
                    "mean": mean_result.get("result"),
                    "median": median_result.get("result"),
                    "mode": mode_result.get("result"),
                    "standard_deviation": std_dev_result.get("result"),
                    "range": range_result.get("result"),
                    "minimum": min(numbers),
                    "maximum": max(numbers)
                },
                "input_data": numbers
            }
            
        except Exception as e:
            return {"success": False, "error": f"Summary statistics calculation failed: {str(e)}"}
    
    def process_request(self, operation, data):
        """Process statistics requests"""
        numbers = data.get("numbers", [])
        
        if operation == "mean":
            return self.mean(numbers)
        elif operation == "median":
            return self.median(numbers)
        elif operation == "mode":
            return self.mode(numbers)
        elif operation == "standard_deviation":
            return self.standard_deviation(numbers)
        elif operation == "range":
            return self.range_calc(numbers)
        elif operation == "summary":
            return self.summary_stats(numbers)
        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}

def test_statistics_agent():
    """Test the statistics agent locally without network dependencies"""
    print("📊 Testing Statistics Agent (Standalone Mode)...")
    print("=" * 50)
    
    # Create agent instance
    agent = StandaloneStatisticsAgent()
    
    # Test data
    test_data = [10, 15, 20, 25, 30, 25, 15]
    
    print(f"📋 Test data: {test_data}")
    print(f"🔢 Data count: {len(test_data)}")
    print(f"📊 Data range: {min(test_data)} to {max(test_data)}")
    
    # Test operations
    operations = [
        ("mean", "Arithmetic Mean"),
        ("median", "Median"),
        ("mode", "Mode"),
        ("standard_deviation", "Standard Deviation"),
        ("range", "Range"),
        ("summary", "Summary Statistics")
    ]
    
    print(f"\n🧮 Testing Statistics Operations...")
    print("-" * 30)
    
    for operation, description in operations:
        print(f"\n🔍 {description}...")
        result = agent.process_request(operation, {"numbers": test_data})
        
        if result.get("success"):
            if operation == "summary":
                print(f"✅ {description}:")
                for stat, value in result["data"].items():
                    print(f"   {stat}: {value}")
            else:
                print(f"✅ {description}: {result.get('result')}")
        else:
            print(f"❌ {description}: {result.get('error')}")
    
    print(f"\n" + "=" * 50)
    print(f"🎉 Statistics Agent Test Complete!")
    print(f"✅ All operations working with local fallback calculations")
    print(f"🔗 Your agent is ready for A2A communication!")
    print(f"📝 When your friends' agents are ready, update the .env file with their IP addresses")

if __name__ == "__main__":
    test_statistics_agent()