# Create a fixed version with correct field names
import os

# Read the current file
with open('insurance_leads_pipeline.py', 'r') as f:
    content = f.read()

# Fix the field names to match what Apify expects
replacements = [
    ('"searchQuery":', '"search_query":'),
    ('"maxResults":', '"max_results":'),
    ('"postedWithinDays":', '"posted_within_days":'),
    ('"includeRemote":', '"include_remote":'),
]

for old, new in replacements:
    content = content.replace(old, new)

# Write the fixed version
with open('insurance_leads_pipeline.py', 'w') as f:
    f.write(content)

print("✅ Fixed field names in pipeline script!")
