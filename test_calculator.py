import requests
import json


def test_calculator():
    """Test your calculator agent"""
    BASE_URL = "http://localhost:5001"

    print("Testing Calculator Agent")
    print("=" * 30)

    # Test 1: Health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("Health check passed")
        else:
            print("Health check failed")
            return
    except Exception:
        print("Agent not running - start it first!")
        return

    # Test 2: Basic calculations
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
            "name": "Division",
            "data": {"operation": "divide", "data": {"numbers": [100, 2, 5]}}
        },
        {
            "name": "Square Root",
            "data": {"operation": "square_root", "data": {"number": 16}}
        }
    ]

    for test in tests:
        try:
            response = requests.post(
                f"{BASE_URL}/calculate",
                json=test["data"],
            )

            if response.status_code == 200:
                result = response.json()
                answer = result["response"].get("result")
                print(f"{test['name']}: {answer}")
            else:
                print(f"{test['name']}: Failed (status {response.status_code})")
        except Exception as e:
            print(f"{test['name']}: Error - {str(e)}")


if __name__ == "__main__":
    test_calculator()
