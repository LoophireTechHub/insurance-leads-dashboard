# Fix the field names to match what the Apify actor expects
import os

# Read the current file
with open('insurance_leads_pipeline.py', 'r') as f:
    lines = f.readlines()

# Find and replace the actor_input section
new_lines = []
for i, line in enumerate(lines):
    if '"posted_within_days":' in line:
        # Replace with posted_since and set it to "month" to get jobs from last 30 days
        new_lines.append(line.replace('"posted_within_days": None', '"posted_since": "month"'))
    elif 'actor_input = {' in line:
        # Mark where we found the actor input
        new_lines.append(line)
    else:
        new_lines.append(line)

# Write the fixed version
with open('insurance_leads_pipeline.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Fixed posted_since field!")
print("📝 Set to 'month' to get jobs from last 30 days")
