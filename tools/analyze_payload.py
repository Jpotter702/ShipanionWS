"""
Analyze JSON Payload Format

This script analyzes a JSON payload to identify formatting issues that might cause
Bob to fail to respond or miss the quote.
"""
import json
import sys
import argparse
from typing import Dict, Any, List, Optional

def analyze_payload(payload: Dict[str, Any]) -> List[str]:
    """
    Analyze a JSON payload for formatting issues.
    
    Args:
        payload: The JSON payload to analyze
        
    Returns:
        A list of issues found in the payload
    """
    issues = []
    
    # Check message type
    if "type" not in payload:
        issues.append("Missing 'type' field")
    elif payload["type"] != "client_tool_result":
        issues.append(f"Incorrect message type: {payload['type']} (expected 'client_tool_result')")
    
    # Check tool_call_id
    if "tool_call_id" not in payload:
        issues.append("Missing 'tool_call_id' field")
    
    # Check result field
    if "result" not in payload:
        issues.append("Missing 'result' field")
    else:
        result = payload["result"]
        
        # Check if result is an array for shipping quotes
        if not isinstance(result, list):
            issues.append(f"'result' is not an array (got {type(result).__name__})")
        else:
            # Check if result is empty
            if len(result) == 0:
                issues.append("'result' array is empty")
            else:
                # Check each shipping option
                for i, option in enumerate(result):
                    option_issues = analyze_shipping_option(option, i)
                    issues.extend(option_issues)
    
    # Check is_error field
    if "is_error" not in payload:
        issues.append("Missing 'is_error' field")
    elif payload["is_error"] is True:
        # If it's an error, check for error message
        if "result" not in payload or not isinstance(payload["result"], dict) or "error" not in payload["result"]:
            issues.append("'is_error' is true but no error message provided")
    
    # Check client_tool_call field (should be present for ElevenLabs)
    if "client_tool_call" not in payload:
        issues.append("Missing 'client_tool_call' field (required for ElevenLabs)")
    else:
        client_tool_call = payload["client_tool_call"]
        
        # Check tool_name
        if "tool_name" not in client_tool_call:
            issues.append("Missing 'tool_name' in client_tool_call")
        elif client_tool_call["tool_name"] != "get_shipping_quotes":
            issues.append(f"Incorrect tool_name: {client_tool_call['tool_name']} (expected 'get_shipping_quotes')")
    
    return issues

def analyze_shipping_option(option: Dict[str, Any], index: int) -> List[str]:
    """
    Analyze a shipping option for formatting issues.
    
    Args:
        option: The shipping option to analyze
        index: The index of the option in the result array
        
    Returns:
        A list of issues found in the shipping option
    """
    issues = []
    
    # Check required fields
    required_fields = ["carrier", "service", "price", "eta"]
    for field in required_fields:
        if field not in option:
            issues.append(f"Option {index+1}: Missing '{field}' field")
    
    # Check field types
    if "carrier" in option and not isinstance(option["carrier"], str):
        issues.append(f"Option {index+1}: 'carrier' is not a string (got {type(option['carrier']).__name__})")
    
    if "service" in option and not isinstance(option["service"], str):
        issues.append(f"Option {index+1}: 'service' is not a string (got {type(option['service']).__name__})")
    
    if "price" in option:
        if not isinstance(option["price"], (int, float)):
            issues.append(f"Option {index+1}: 'price' is not a number (got {type(option['price']).__name__})")
    
    if "eta" in option and not isinstance(option["eta"], str):
        issues.append(f"Option {index+1}: 'eta' is not a string (got {type(option['eta']).__name__})")
    
    return issues

def main():
    """Parse command line arguments and analyze the payload."""
    parser = argparse.ArgumentParser(description="Analyze JSON payload format")
    parser.add_argument("file", nargs="?", help="JSON file to analyze (if not provided, reads from stdin)")
    args = parser.parse_args()
    
    try:
        # Read JSON from file or stdin
        if args.file:
            with open(args.file, "r") as f:
                payload = json.load(f)
        else:
            payload = json.load(sys.stdin)
        
        # Analyze the payload
        issues = analyze_payload(payload)
        
        # Print the results
        if issues:
            print(f"Found {len(issues)} issues:")
            for i, issue in enumerate(issues):
                print(f"{i+1}. {issue}")
            sys.exit(1)
        else:
            print("No issues found in the payload.")
            sys.exit(0)
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
