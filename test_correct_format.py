import requests
import os
import json

token = os.environ.get('APIFY_API_TOKEN')
actor_id = "8QfidRKcSVYICkwrq"

# Try with search_terms instead of search_query
test_input = {
    "search_terms": ["Commercial Insurance Underwriter"],  # Array of search terms
    "max_results": 10,
    "posted_since": "month",
    "country": "USA",
    "platforms": ["LinkedIn"]
}

print("Testing with corrected input:")
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
    print("Success! Run started.")
    run_id = response.json()['data']['id']
    print(f"Run ID: {run_id}")
