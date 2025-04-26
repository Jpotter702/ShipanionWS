"""
Analyze Bob's Response

This script analyzes Bob's spoken response to a shipping quote and compares it to the expected format.
It helps identify issues with Bob's response and provides suggestions for improvement.
"""
import argparse
import re
import sys
from typing import Dict, Any, List, Optional, Tuple

def extract_quote_details(response: str) -> Tuple[List[Dict[str, Any]], bool, bool]:
    """
    Extract shipping quote details from Bob's response.
    
    Args:
        response: Bob's spoken response
        
    Returns:
        A tuple containing:
        - A list of extracted quotes (carrier, service, price, eta)
        - Whether Bob mentioned the cheapest option first
        - Whether Bob asked for user preference
    """
    quotes = []
    
    # Extract prices with carrier and service
    price_pattern = r'(\w+)\s+(\w+(?:\s+\w+)?)\s+at\s+\$(\d+\.\d+)'
    price_matches = re.findall(price_pattern, response)
    
    for carrier, service, price in price_matches:
        # Find the ETA associated with this carrier/service
        eta_pattern = rf'{carrier}\s+{service}.*?(\d+(?:-\d+)?\s+business\s+days)'
        eta_match = re.search(eta_pattern, response, re.IGNORECASE)
        
        eta = eta_match.group(1) if eta_match else "unknown"
        
        quotes.append({
            "carrier": carrier,
            "service": service,
            "price": float(price),
            "eta": eta
        })
    
    # Check if cheapest option is mentioned first
    cheapest_first = False
    if quotes and "affordable" in response.lower() or "cheapest" in response.lower():
        # Check if the first quote is actually the cheapest
        if quotes and quotes[0]["price"] == min(q["price"] for q in quotes):
            cheapest_first = True
    
    # Check if Bob asked for user preference
    asked_preference = False
    preference_patterns = [
        r'which\s+option\s+would\s+you\s+prefer',
        r'which\s+(?:one|option)\s+(?:do|would)\s+you\s+(?:want|like|prefer)',
        r'which\s+(?:shipping|delivery)\s+(?:option|method)\s+(?:do|would)\s+you\s+(?:want|like|prefer)',
        r'do\s+you\s+have\s+a\s+preference'
    ]
    
    for pattern in preference_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            asked_preference = True
            break
    
    return quotes, cheapest_first, asked_preference

def analyze_response(response: str, expected_quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze Bob's response and compare it to the expected quotes.
    
    Args:
        response: Bob's spoken response
        expected_quotes: The expected shipping quotes
        
    Returns:
        An analysis of Bob's response
    """
    # Extract quotes from Bob's response
    extracted_quotes, cheapest_first, asked_preference = extract_quote_details(response)
    
    # Check if all expected carriers are mentioned
    expected_carriers = set(q["carrier"] for q in expected_quotes)
    extracted_carriers = set(q["carrier"] for q in extracted_quotes)
    missing_carriers = expected_carriers - extracted_carriers
    
    # Check if all expected prices are mentioned
    expected_prices = set(q["price"] for q in expected_quotes)
    extracted_prices = set(q["price"] for q in extracted_quotes)
    missing_prices = expected_prices - extracted_prices
    
    # Calculate overall score
    score = 0
    max_score = 100
    
    # Points for mentioning all carriers (30 points)
    carrier_score = 30 * (len(extracted_carriers) / len(expected_carriers)) if expected_carriers else 0
    score += carrier_score
    
    # Points for mentioning all prices (30 points)
    price_score = 30 * (len(extracted_prices) / len(expected_prices)) if expected_prices else 0
    score += price_score
    
    # Points for mentioning cheapest option first (20 points)
    score += 20 if cheapest_first else 0
    
    # Points for asking for user preference (20 points)
    score += 20 if asked_preference else 0
    
    # Prepare analysis
    analysis = {
        "extracted_quotes": extracted_quotes,
        "mentioned_carriers": list(extracted_carriers),
        "missing_carriers": list(missing_carriers),
        "mentioned_prices": list(extracted_prices),
        "missing_prices": list(missing_prices),
        "cheapest_first": cheapest_first,
        "asked_preference": asked_preference,
        "score": score,
        "max_score": max_score
    }
    
    return analysis

def print_analysis(analysis: Dict[str, Any]):
    """
    Print the analysis of Bob's response.
    
    Args:
        analysis: The analysis of Bob's response
    """
    print("\n=== BOB'S RESPONSE ANALYSIS ===")
    
    # Print extracted quotes
    print("\nExtracted Quotes:")
    if analysis["extracted_quotes"]:
        for i, quote in enumerate(analysis["extracted_quotes"]):
            print(f"  {i+1}. {quote['carrier']} {quote['service']} - ${quote['price']} ({quote['eta']})")
    else:
        print("  No quotes extracted")
    
    # Print carriers
    print("\nCarriers:")
    print(f"  Mentioned: {', '.join(analysis['mentioned_carriers']) if analysis['mentioned_carriers'] else 'None'}")
    print(f"  Missing: {', '.join(analysis['missing_carriers']) if analysis['missing_carriers'] else 'None'}")
    
    # Print prices
    print("\nPrices:")
    print(f"  Mentioned: {', '.join(f'${p}' for p in analysis['mentioned_prices']) if analysis['mentioned_prices'] else 'None'}")
    print(f"  Missing: {', '.join(f'${p}' for p in analysis['missing_prices']) if analysis['missing_prices'] else 'None'}")
    
    # Print other checks
    print("\nOther Checks:")
    print(f"  Cheapest Option First: {'✓' if analysis['cheapest_first'] else '✗'}")
    print(f"  Asked for Preference: {'✓' if analysis['asked_preference'] else '✗'}")
    
    # Print score
    print(f"\nOverall Score: {analysis['score']}/{analysis['max_score']} ({analysis['score']}%)")
    
    # Print recommendations
    print("\nRecommendations:")
    if analysis["missing_carriers"]:
        print(f"  - Ensure Bob mentions all carriers: {', '.join(analysis['missing_carriers'])}")
    
    if analysis["missing_prices"]:
        print(f"  - Ensure Bob mentions all prices: {', '.join(f'${p}' for p in analysis['missing_prices'])}")
    
    if not analysis["cheapest_first"]:
        print("  - Instruct Bob to clearly identify and present the cheapest option first")
    
    if not analysis["asked_preference"]:
        print("  - Ensure Bob asks for the user's preference after presenting the quotes")
    
    if analysis["score"] < 70:
        print("  - Consider updating the tool prompt in Agent Studio (see AGENT_STUDIO_PROMPT_GUIDE.md)")
    
    print("\n===============================")

def main():
    """Parse command line arguments and analyze Bob's response."""
    parser = argparse.ArgumentParser(description="Analyze Bob's response to shipping quotes")
    parser.add_argument("--response", help="Bob's spoken response (if not provided, will prompt for input)")
    parser.add_argument("--expected", help="JSON file containing expected quotes (if not provided, will use default)")
    args = parser.parse_args()
    
    # Get Bob's response
    if args.response:
        response = args.response
    else:
        print("Enter Bob's spoken response (press Ctrl+D or Ctrl+Z on a new line when done):")
        response = sys.stdin.read().strip()
    
    # Use default expected quotes
    expected_quotes = [
        {
            "carrier": "UPS",
            "service": "Ground",
            "price": 12.99,
            "eta": "3-5 business days"
        },
        {
            "carrier": "USPS",
            "service": "Priority Mail",
            "price": 9.99,
            "eta": "2-3 business days"
        },
        {
            "carrier": "FedEx",
            "service": "Express Saver",
            "price": 14.99,
            "eta": "1-2 business days"
        }
    ]
    
    # Analyze the response
    analysis = analyze_response(response, expected_quotes)
    
    # Print the analysis
    print_analysis(analysis)

if __name__ == "__main__":
    main()
