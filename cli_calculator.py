import os
import sys
import argparse
import requests


def parse_number_list(csv: str):
    try:
        return [float(x.strip()) for x in csv.split(',') if x.strip() != '']
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid number in list. Use comma-separated numbers, e.g., 1,2,3")


def build_payload(args):
    op = args.operation
    data = {}

    if op in {"add", "subtract", "multiply", "divide"}:
        if args.numbers is None:
            raise ValueError("--numbers is required for add/subtract/multiply/divide")
        data = {"numbers": args.numbers}

    elif op == "square_root":
        if args.number is None:
            raise ValueError("--number is required for square_root")
        data = {"number": args.number}

    elif op == "power":
        if args.base is None or args.exponent is None:
            raise ValueError("--base and --exponent are required for power")
        data = {"base": args.base, "exponent": args.exponent}

    elif op == "percentage":
        if args.value is None or args.percentage is None:
            raise ValueError("--value and --percentage are required for percentage")
        data = {"value": args.value, "percentage": args.percentage}

    else:
        raise ValueError(f"Unknown operation: {op}")

    return {"operation": op, "data": data}


def interactive_prompt():
    print("Calculator CLI (interactive mode)")
    print("Select operation:")
    print("  1) add")
    print("  2) subtract")
    print("  3) multiply")
    print("  4) divide")
    print("  5) square_root")
    print("  6) power")
    print("  7) percentage")

    choice = input("Enter choice [1-7]: ").strip()
    mapping = {
        '1': 'add', '2': 'subtract', '3': 'multiply', '4': 'divide',
        '5': 'square_root', '6': 'power', '7': 'percentage'
    }
    op = mapping.get(choice)
    if not op:
        print("Invalid choice.")
        sys.exit(1)

    class Args:
        pass
    args = Args()
    args.operation = op

    if op in {"add", "subtract", "multiply", "divide"}:
        csv = input("Enter comma-separated numbers (e.g., 10,20,30): ").strip()
        args.numbers = parse_number_list(csv)
        args.number = args.base = args.exponent = args.value = args.percentage = None
    elif op == "square_root":
        args.number = float(input("Enter number: ").strip())
        args.numbers = args.base = args.exponent = args.value = args.percentage = None
    elif op == "power":
        args.base = float(input("Enter base: ").strip())
        args.exponent = float(input("Enter exponent: ").strip())
        args.numbers = args.number = args.value = args.percentage = None
    elif op == "percentage":
        args.value = float(input("Enter value: ").strip())
        args.percentage = float(input("Enter percentage: ").strip())
        args.numbers = args.number = args.base = args.exponent = None

    return args


def main():
    parser = argparse.ArgumentParser(description="CLI client for Calculator Agent")
    parser.add_argument("--base-url", default=os.getenv("CALCULATOR_URL", "http://localhost:5001"), help="Calculator service base URL")
    parser.add_argument("-o", "--operation", choices=[
        "add", "subtract", "multiply", "divide", "square_root", "power", "percentage"
    ], help="Operation to perform")
    parser.add_argument("--numbers", type=parse_number_list, help="Comma-separated numbers for add/subtract/multiply/divide")
    parser.add_argument("--number", type=float, help="Single number for square_root")
    parser.add_argument("--base", type=float, help="Base for power")
    parser.add_argument("--exponent", type=float, help="Exponent for power")
    parser.add_argument("--value", type=float, help="Value for percentage")
    parser.add_argument("--percentage", type=float, help="Percentage for percentage")

    args = parser.parse_args()

    if not args.operation:
        # Interactive mode
        args = interactive_prompt()
        # Use default base URL in interactive mode
        base_url = os.getenv("CALCULATOR_URL", "http://localhost:5001")
    else:
        base_url = args.base_url

    try:
        payload = build_payload(args)
    except Exception as e:
        print(f"Input error: {e}")
        sys.exit(2)

    try:
        resp = requests.post(f"{base_url}/calculate", json=payload, timeout=10)
        if resp.status_code != 200:
            print(f"Request failed with status {resp.status_code}: {resp.text}")
            sys.exit(3)
        body = resp.json()
        result = body.get("response", {}).get("result")
        print(f"Result: {result}")
    except requests.RequestException as e:
        print(f"Request error: {e}")
        sys.exit(4)


if __name__ == "__main__":
    main()
