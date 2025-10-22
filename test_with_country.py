import requests
import os
import json

token = os.environ.get('APIFY_API_TOKEN')
actor_id = "8QfidRKcSVYICkwrq"

# Add country back, but no platforms
test_input = {
    "search_terms": ["Commercial Insurance Underwriter"],
    "max_results": 10,
    "posted_since": "month",
    "location": "USA",
    "country": "USA"
}

print("Testing with location AND country (no platforms):")
print(json.dumps(test_input, indent=2))

response = requests.post(
    f"https://api.apify.com/v2/acts/{actor_id}/runs",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json=test_input
)

print(f"\nResponse status: {response.status_code}")
if response.status_code != 201:
    print("Error:")
    print(json.dumps(response.json(), indent=2))
else:
    print("✅ SUCCESS! Run started!")
    run_data = response.json()['data']
    print(f"Run ID: {run_data['id']}")
    print(f"Status: {run_data['status']}")
    print("\n🎉 We found the correct format!")
    print("\nRequired fields:")
    print("- search_terms (array of strings)")
    print("- max_results (number)")
    print("- posted_since (string: 'month', 'week', etc.)")
    print("- location (string: 'USA')")
    print("- country (string: 'USA')")
    print("\nNOT allowed: platforms")
