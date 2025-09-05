import os
import sys
import uuid
import argparse
import requests
from typing import List


def parse_csv_floats(csv: str) -> List[float]:
    if not csv:
        return []
    out = []
    for part in csv.split(','):
        part = part.strip()
        if part:
            out.append(float(part))
    return out


def resolve_url(explicit: str, env_url: str, host_env: str, port_env: str, default: str) -> str:
    if explicit:
        return explicit
    if env_url:
        return env_url
    host = os.getenv(host_env)
    port = os.getenv(port_env)
    if host and port:
        return f"http://{host}:{port}"
    return default


def post_json(url: str, payload: dict) -> dict:
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


def try_unit_convert_direct(unit_base_url: str, value: float, from_unit: str, to_unit: str):
    """Hit the Unit Converter's direct endpoint /convert with expected payload."""
    url = f"{unit_base_url.rstrip('/')}/convert"
    resp = post_json(url, {"value": value, "from_unit": from_unit, "to_unit": to_unit})
    result = resp.get("response", {}).get("result")
    if result is None:
        raise RuntimeError(f"Direct /convert returned no result: {resp}")
    return float(result), resp


def try_unit_convert_message(unit_msg_url: str, correlation_id: str, trace: List[str], value: float, from_unit: str, to_unit: str) -> (float, str, dict):
    """Try multiple /message payload shapes commonly used by unit converter agents."""
    variants = [
        ("from_unit/to_unit", {
            "operation": "convert",
            "data": {"value": value, "from_unit": from_unit, "to_unit": to_unit}
        }),
        ("from/to", {
            "operation": "convert",
            "data": {"value": value, "from": from_unit, "to": to_unit}
        }),
        ("fromUnit/toUnit", {
            "operation": "convert",
            "data": {"value": value, "fromUnit": from_unit, "toUnit": to_unit}
        }),
        ("convert_length from_unit/to_unit", {
            "operation": "convert_length",
            "data": {"value": value, "from_unit": from_unit, "to_unit": to_unit}
        }),
    ]

    last_error = None
    last_raw = None
    for name, message in variants:
        try:
            resp = post_json(unit_msg_url, {
                "sender": "pipeline_orchestrator",
                "correlation_id": correlation_id,
                "trace": trace + ["pipeline_orchestrator"],
                "message": message
            })
            result = resp.get("response", {}).get("result")
            if result is not None:
                return float(result), name, resp
            last_raw = resp
        except Exception as e:
            last_error = e
            last_raw = getattr(e, 'response', None)
    raise RuntimeError(f"All unit converter /message variants failed. last_error={last_error}, last_raw={getattr(last_raw, 'text', last_raw)}")


def main():
    parser = argparse.ArgumentParser(description="A2A Orchestrator: Calculator → Unit Converter → Statistics")
    parser.add_argument("--calculator-url", dest="calc_url", default=None, help="Calculator agent base URL (e.g., http://192.168.1.10:5001)")
    parser.add_argument("--unit-url", dest="unit_url", default=None, help="Unit converter agent base URL")
    parser.add_argument("--statistics-url", dest="stats_url", default=None, help="Statistics agent base URL")

    parser.add_argument("--numbers", default="10,20,30", help="CSV numbers for calculator add step")
    parser.add_argument("--from-unit", default="meter", help="Unit converter: from_unit")
    parser.add_argument("--to-unit", default="feet", help="Unit converter: to_unit")
    parser.add_argument("--stats-op", default="mean", choices=["mean", "median", "mode", "standard_deviation", "range"], help="Statistics operation")
    parser.add_argument("--stats-list", default=None, help="CSV numbers for statistics step; if omitted, uses [converted_value, 12.5, 8.0]")

    args = parser.parse_args()

    calc_base = resolve_url(
        args.calc_url,
        os.getenv("CALCULATOR_URL"),
        "CALCULATOR_HOST",
        "CALCULATOR_tPORT",
        "http://localhost:5001",
    )
    unit_base = resolve_url(
        args.unit_url,
        os.getenv("UNIT_CONVERTER_URL"),
        "UNIT_CONVERTER_HOST",
        "UNIT_CONVERTER_PORT",
        "http://localhost:5002",
    )
    stats_base = resolve_url(
        args.stats_url,
        os.getenv("STATISTICS_URL"),
        "STATISTICS_HOST",
        "STATISTICS_PORT",
        "http://localhost:5003",
    )

    calc_msg = f"{calc_base.rstrip('/')}/message"
    unit_msg = f"{unit_base.rstrip('/')}/message"
    stats_msg = f"{stats_base.rstrip('/')}/message"

    numbers = parse_csv_floats(args.numbers)
    correlation_id = str(uuid.uuid4())

    print("Step 1) Calculator → add", numbers)
    r1 = post_json(calc_msg, {
        "sender": "pipeline_orchestrator",
        "correlation_id": correlation_id,
        "trace": ["pipeline_orchestrator"],
        "message": {"operation": "add", "data": {"numbers": numbers}}
    })
    sum_val = r1.get("response", {}).get("result")
    if sum_val is None:
        print("Calculator did not return a result:", r1)
        sys.exit(2)
    print("  Result:", sum_val)

    print(f"Step 2) Unit Converter → convert {sum_val} {args.from_unit} → {args.to_unit}")
    # Try direct endpoint first, then fall back to /message variants
    try:
        converted_val, raw = try_unit_convert_direct(unit_base, float(sum_val), args.from_unit, args.to_unit)
        print("  Endpoint used: /convert")
        print("  Result:", converted_val)
    except Exception:
        try:
            converted_val, variant, raw = try_unit_convert_message(unit_msg, correlation_id, r1.get("trace", []), float(sum_val), args.from_unit, args.to_unit)
            print(f"  Endpoint used: /message (variant: {variant})")
            print("  Result:", converted_val)
        except Exception as e:
            print("Unit converter failed:", e)
            sys.exit(3)

    stats_numbers = parse_csv_floats(args.stats_list) if args.stats_list else [converted_val, 12.5, 8.0]
    print(f"Step 3) Statistics → {args.stats_op} on", stats_numbers)
    r3 = post_json(stats_msg, {
        "sender": "pipeline_orchestrator",
        "correlation_id": correlation_id,
        "trace": r1.get("trace", []) + ["pipeline_orchestrator"],
        "message": {
            "operation": args.stats_op,
            "data": {"numbers": stats_numbers}
        }
    })
    final_val = r3.get("response", {}).get("result")
    if final_val is None:
        print("Statistics did not return a result:", r3)
        sys.exit(4)

    print("\n✔ Final output:", final_val)
    print("correlation_id:", correlation_id)


if __name__ == "__main__":
    main()
