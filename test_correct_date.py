import requests
import os
import json

token = os.environ.get('APIFY_API_TOKEN')
actor_id = "8QfidRKcSVYICkwrq"

# Fix posted_since format - needs number before time unit
test_input = {
    "search_terms": ["Commercial Insurance Underwriter"],
    "max_results": 10,
    "posted_since": "1 month",  # Changed from "month" to "1 month"
    "location": "USA",
    "country": "USA"
}

print("Testing with correct posted_since format:")
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
    print(f"Dataset ID: {run_data.get('defaultDatasetId')}")
    
    print("\n🎉 Perfect! The actor is running!")
    print("\nWaiting 20 seconds to check results...")
    
    import time
    time.sleep(20)
    
    # Check if we have results
    dataset_id = run_data.get('defaultDatasetId')
    results_response = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items?limit=5",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if results_response.status_code == 200:
        results = results_response.json()
        print(f"\n📊 Found {len(results)} results so far!")
        if results:
            print("\nFirst result sample:")
            print(json.dumps(results[0], indent=2)[:500] + "...")
