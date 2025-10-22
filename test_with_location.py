import requests
import os
import json

token = os.environ.get('APIFY_API_TOKEN')
actor_id = "8QfidRKcSVYICkwrq"

# Add location field
test_input = {
    "search_terms": ["Commercial Insurance Underwriter"],
    "max_results": 10,
    "posted_since": "month",
    "location": "USA",  # Added location field
    "country": "USA",
    "platforms": ["LinkedIn"]
}

print("Testing with location field added:")
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
    
    # Wait a moment and check the status
    import time
    time.sleep(5)
    
    # Check status
    status_response = requests.get(
        f"https://api.apify.com/v2/actor-runs/{run_data['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if status_response.status_code == 200:
        status_data = status_response.json()['data']
        print(f"Current status: {status_data['status']}")
