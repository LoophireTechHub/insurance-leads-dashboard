import requests
import os
import json

token = os.environ.get('APIFY_API_TOKEN')
actor_id = "8QfidRKcSVYICkwrq"

# Minimal input without platforms
test_input = {
    "search_terms": ["Commercial Insurance Underwriter"],
    "max_results": 10,
    "posted_since": "month",
    "location": "USA"
}

print("Testing with minimal input (no platforms field):")
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
    print("✅ Success! Run started.")
    run_data = response.json()['data']
    print(f"Run ID: {run_data['id']}")
    print(f"Status: {run_data['status']}")
    print("\nThe actor is running! This confirms the correct format.")
    print("\nCorrect fields are:")
    print("- search_terms (array)")
    print("- max_results")
    print("- posted_since")
    print("- location")
