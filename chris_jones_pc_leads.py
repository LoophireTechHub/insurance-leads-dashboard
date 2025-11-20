#!/usr/bin/env python3
"""
Chris Jones Lead Dashboard - US-Wide Property & Casualty Insurance Jobs
Pulls P&C insurance jobs (companies <300 employees) and enriches with hiring manager contact info via Apollo API
"""

import sys
import os
from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime
import json
from pathlib import Path
import requests
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

APOLLO_BASE_URL = "https://api.apollo.io/v1"

def get_company_info_apollo(company_name: str, apollo_token: str, max_contacts: int = 3) -> dict:
    """Get company info and contacts using Apollo API"""
    try:
        headers = {"X-Api-Key": apollo_token, "Content-Type": "application/json"}

        # Search for the company first
        company_search_data = {
            "q_organization_name": company_name,
            "page": 1,
            "per_page": 1
        }

        company_response = requests.post(
            f"{APOLLO_BASE_URL}/organizations/search",
            headers=headers,
            json=company_search_data,
            timeout=10
        )

        if company_response.status_code != 200:
            return {'contacts': [], 'employee_count': None, 'website': None, 'phone': None}

        companies = company_response.json().get('organizations', [])
        if not companies:
            return {'contacts': [], 'employee_count': None, 'website': None, 'phone': None}

        company_data = companies[0]
        company_id = company_data.get('id')

        # Get company info
        company_info = {
            'employee_count': company_data.get('estimated_num_employees'),
            'website': company_data.get('website_url'),
            'phone': company_data.get('phone'),
            'industry': company_data.get('industry'),
            'contacts': []
        }

        # Search for contacts at this company using /contacts/search (reveals real emails)
        # Try broader search first without title filtering to get ANY contacts
        contact_search_data = {
            "organization_ids": [company_id],
            "page": 1,
            "per_page": max_contacts * 2  # Get more results to filter
        }

        contact_response = requests.post(
            f"{APOLLO_BASE_URL}/contacts/search",
            headers=headers,
            json=contact_search_data,
            timeout=10
        )

        if contact_response.status_code == 200:
            all_contacts = contact_response.json().get('contacts', [])

            # Prioritize contacts with real emails and important titles
            important_titles = ['ceo', 'president', 'owner', 'vp', 'vice president', 'director', 'manager', 'hr']

            # Sort contacts: prioritize those with emails AND important titles
            def contact_score(contact):
                score = 0
                if contact.get('email'):
                    score += 100  # Has email = highest priority
                title_lower = (contact.get('title', '') or '').lower()
                if any(t in title_lower for t in important_titles):
                    score += 50  # Has important title
                return score

            sorted_contacts = sorted(all_contacts, key=contact_score, reverse=True)

            for contact in sorted_contacts[:max_contacts]:
                # /contacts/search uses export credits and reveals real emails
                if contact.get('name'):  # Only add if has name
                    company_info['contacts'].append({
                        'name': contact.get('name', ''),
                        'title': contact.get('title', ''),
                        'email': contact.get('email', ''),
                        'phone': contact.get('sanitized_phone', ''),
                        'linkedin': contact.get('linkedin_url', '')
                    })

        time.sleep(0.5)  # Rate limiting
        return company_info

    except Exception as e:
        logger.debug(f"Error getting company info for {company_name}: {e}")

    return {'contacts': [], 'employee_count': None, 'website': None, 'phone': None}

def get_chris_jones_pc_jobs():
    """Get Property & Casualty insurance jobs across US (companies <300 employees) with contact enrichment"""

    print("=" * 80)
    print("CHRIS JONES LEAD DASHBOARD - US-WIDE PROPERTY & CASUALTY")
    print("=" * 80)
    print()
    print("🔍 Searching LinkedIn, Indeed, and ZipRecruiter for P&C insurance jobs...")
    print("📍 Coverage: Entire United States")
    print("📅 Looking back 45 days")
    print("🎯 Target: P&C jobs at companies <300 employees")
    print("👤 Enriching with Apollo contact data...")
    print()

    # Check for Apollo API token
    apollo_token = os.environ.get('APOLLO_API_TOKEN')
    if not apollo_token:
        print("⚠️  Warning: APOLLO_API_TOKEN not set - contacts will not be enriched")
        apollo_enabled = False
    else:
        apollo_enabled = True
        print("✅ Apollo API connected")
        print()

    try:
        # Search for commercial insurance jobs across US - Multiple searches to get 500+
        all_jobs = []
        search_sites = ["linkedin", "indeed", "zip_recruiter"]

        # Search 1: Property & Casualty Producers
        print("🔍 Search 1/6: P&C Producers...")
        jobs1 = scrape_jobs(
            site_name=search_sites,
            search_term="property casualty producer OR P&C producer OR property and casualty producer",
            location="United States",
            results_wanted=200,
            hours_old=1080,
            linkedin_fetch_description=False
        )
        if jobs1 is not None and not jobs1.empty:
            print(f"   Found {len(jobs1)} jobs")
            all_jobs.append(jobs1)

        # Search 2: P&C Account Managers
        print("🔍 Search 2/6: P&C Account Managers...")
        jobs2 = scrape_jobs(
            site_name=search_sites,
            search_term="property casualty account manager OR P&C account manager",
            location="United States",
            results_wanted=200,
            hours_old=1080,
            linkedin_fetch_description=False
        )
        if jobs2 is not None and not jobs2.empty:
            print(f"   Found {len(jobs2)} jobs")
            all_jobs.append(jobs2)

        # Search 3: P&C Underwriters
        print("🔍 Search 3/6: P&C Underwriters...")
        jobs3 = scrape_jobs(
            site_name=search_sites,
            search_term="property casualty underwriter OR P&C underwriter",
            location="United States",
            results_wanted=200,
            hours_old=1080,
            linkedin_fetch_description=False
        )
        if jobs3 is not None and not jobs3.empty:
            print(f"   Found {len(jobs3)} jobs")
            all_jobs.append(jobs3)

        # Search 4: P&C Brokers
        print("🔍 Search 4/6: P&C Brokers...")
        jobs4 = scrape_jobs(
            site_name=search_sites,
            search_term="property casualty broker OR P&C broker",
            location="United States",
            results_wanted=200,
            hours_old=1080,
            linkedin_fetch_description=False
        )
        if jobs4 is not None and not jobs4.empty:
            print(f"   Found {len(jobs4)} jobs")
            all_jobs.append(jobs4)

        # Search 5: Commercial Lines (related to P&C)
        print("🔍 Search 5/6: Commercial Lines...")
        jobs5 = scrape_jobs(
            site_name=search_sites,
            search_term="commercial lines producer OR commercial lines account manager",
            location="United States",
            results_wanted=200,
            hours_old=1080,
            linkedin_fetch_description=False
        )
        if jobs5 is not None and not jobs5.empty:
            print(f"   Found {len(jobs5)} jobs")
            all_jobs.append(jobs5)

        # Search 6: P&C Account Executives
        print("🔍 Search 6/6: P&C Account Executives...")
        jobs6 = scrape_jobs(
            site_name=search_sites,
            search_term="property casualty account executive OR P&C account executive",
            location="United States",
            results_wanted=200,
            hours_old=1080,
            linkedin_fetch_description=False
        )
        if jobs6 is not None and not jobs6.empty:
            print(f"   Found {len(jobs6)} jobs")
            all_jobs.append(jobs6)

        # Combine all searches
        if not all_jobs:
            print("❌ No jobs found")
            return

        jobs_df = pd.concat(all_jobs, ignore_index=True)
        print(f"\n📊 Total jobs before deduplication: {len(jobs_df)}")

        # Remove duplicates based on job_url
        jobs_df = jobs_df.drop_duplicates(subset=['job_url'], keep='first')
        print(f"📊 Total jobs after deduplication: {len(jobs_df)}")

        if jobs_df is None or jobs_df.empty:
            print("❌ No jobs found")
            return

        print(f"✅ Found {len(jobs_df)} total jobs\n")
        print("🔍 Filtering for commercial insurance roles...\n")

        # EXCLUDE these roles completely
        exclude_keywords = [
            # Entry level
            'entry level', 'entry-level', 'junior', 'intern', 'trainee',
            # Customer service / claims
            'customer service', 'call center', 'claims adjuster', 'claims rep',
            'claims examiner', 'claims processor', 'claims specialist',
            # Support roles
            'administrative', 'assistant', 'coordinator', 'clerk',
            # Non-insurance roles
            'podcast', 'tv producer', 'webinar producer', 'video producer',
            'pawn broker', 'pawn shop', 'real estate broker', 'mortgage broker',
            'freight broker', 'customs broker', 'data broker', 'loan broker',
            'lending broker', 'financial broker'
        ]

        # MUST contain insurance-related keywords
        insurance_keywords = [
            'insurance', 'producer', 'underwriter', 'broker', 'agent',
            'commercial lines', 'commercial insurance', 'risk'
        ]

        # INCLUDE these commercial insurance roles
        include_keywords = [
            # Commercial Insurance Specific
            'commercial lines', 'commercial insurance', 'commercial producer',
            'commercial account manager', 'commercial underwriter', 'commercial broker',
            # Producer & Sales
            'producer', 'account manager', 'account executive', 'broker',
            'sales executive', 'sales manager', 'business development',
            # Underwriting
            'underwriter', 'underwriting', 'risk manager', 'risk advisor',
            'risk consultant', 'risk specialist',
            # Agent roles
            'insurance agent', 'insurance specialist', 'insurance consultant',
            # Leadership
            'director', 'vp', 'vice president', 'manager', 'senior',
            'supervisor', 'team lead', 'head of'
        ]

        # Filter jobs
        filtered_jobs = []
        for _, job in jobs_df.iterrows():
            title = str(job.get('title', '') or '').lower()
            company = str(job.get('company', '') or '').lower()
            description = str(job.get('description', '') or '').lower()

            # Skip excluded roles
            if any(keyword in title for keyword in exclude_keywords):
                continue

            # MUST have insurance keyword in title or company
            has_insurance_context = any(keyword in title or keyword in company
                                       for keyword in insurance_keywords)
            if not has_insurance_context:
                continue

            # Include only relevant roles
            if any(keyword in title for keyword in include_keywords):
                filtered_jobs.append(job)

        # Convert to DataFrame and sort by date
        if not filtered_jobs:
            print("❌ No relevant jobs found after filtering")
            return

        result_df = pd.DataFrame(filtered_jobs)
        result_df['date_posted'] = pd.to_datetime(result_df['date_posted'], errors='coerce')
        result_df = result_df.sort_values('date_posted', ascending=False, na_position='last')

        print(f"✅ Found {len(result_df)} commercial insurance jobs\n")

        # Take top 500+ (or all if less than 500)
        team_jobs = result_df.head(600)

        # Enrich with Apollo contacts
        if apollo_enabled:
            print("=" * 80)
            print("👤 ENRICHING JOBS WITH CONTACT INFORMATION")
            print("=" * 80)
            print()

            # Get unique companies
            unique_companies = team_jobs['company'].unique()
            print(f"📊 Found {len(unique_companies)} unique companies to enrich")
            print("⏳ This may take a few minutes...")
            print()

            # Create company -> info mapping (contacts + company size)
            company_info_map = {}
            for i, company_name in enumerate(unique_companies, 1):
                if pd.isna(company_name) or company_name == '':
                    continue

                print(f"  [{i}/{len(unique_companies)}] {company_name}...", end="\r")
                company_info = get_company_info_apollo(company_name, apollo_token, max_contacts=3)
                if company_info:
                    company_info_map[company_name] = company_info

                time.sleep(0.6)  # Rate limiting

            print()
            print(f"✅ Enriched {len(company_info_map)} companies with contact and company data\n")

            # Add company info and contacts to jobs
            for idx, job in team_jobs.iterrows():
                company_name = job.get('company')
                if company_name in company_info_map:
                    info = company_info_map[company_name]

                    # Add company info
                    team_jobs.at[idx, 'company_size'] = info.get('employee_count', '')
                    team_jobs.at[idx, 'company_website'] = info.get('website', '')
                    team_jobs.at[idx, 'company_phone'] = info.get('phone', '')
                    team_jobs.at[idx, 'company_industry'] = info.get('industry', '')

                    # Add contacts
                    contacts = info.get('contacts', [])
                    for i, contact in enumerate(contacts[:3], 1):
                        team_jobs.at[idx, f'contact_{i}_name'] = contact.get('name', '')
                        team_jobs.at[idx, f'contact_{i}_title'] = contact.get('title', '')
                        team_jobs.at[idx, f'contact_{i}_email'] = contact.get('email', '')
                        team_jobs.at[idx, f'contact_{i}_phone'] = contact.get('phone', '')
                        team_jobs.at[idx, f'contact_{i}_linkedin'] = contact.get('linkedin', '')

        # Filter companies to 300 employees or less
        if apollo_enabled:
            print("=" * 80)
            print("🔍 FILTERING COMPANIES BY SIZE (300 EMPLOYEES OR LESS)")
            print("=" * 80)
            print()

            original_count = len(team_jobs)

            # Filter jobs where company_size is <= 300 or unknown
            team_jobs = team_jobs[
                (team_jobs['company_size'].isna()) |
                (team_jobs['company_size'] == '') |
                (team_jobs['company_size'].astype(str).str.strip() == '') |
                (pd.to_numeric(team_jobs['company_size'], errors='coerce') <= 300)
            ].copy()

            filtered_count = original_count - len(team_jobs)
            print(f"📊 Original jobs: {original_count}")
            print(f"📊 Filtered out (>300 employees): {filtered_count}")
            print(f"✅ Remaining jobs: {len(team_jobs)}")
            print()

        print("=" * 80)
        print(f"CHRIS JONES P&C LEADS SUMMARY - {len(team_jobs)} JOBS")
        print("=" * 80)
        print()

        # Calculate stats
        commercial_specific = len([j for _, j in team_jobs.iterrows()
                                  if 'commercial' in str(j.get('title', '')).lower()])

        # Count by role type
        producers = len([j for _, j in team_jobs.iterrows()
                        if 'producer' in str(j.get('title', '')).lower()])
        account_mgrs = len([j for _, j in team_jobs.iterrows()
                           if 'account manager' in str(j.get('title', '')).lower()])
        underwriters = len([j for _, j in team_jobs.iterrows()
                           if 'underwriter' in str(j.get('title', '')).lower()])
        brokers = len([j for _, j in team_jobs.iterrows()
                      if 'broker' in str(j.get('title', '')).lower()])

        print(f"📊 Role Breakdown:")
        print(f"   - Commercial-Specific Roles: {commercial_specific}")
        print(f"   - Producers: {producers}")
        print(f"   - Account Managers: {account_mgrs}")
        print(f"   - Underwriters: {underwriters}")
        print(f"   - Brokers: {brokers}")
        print()

        # Count recent jobs
        seven_days_ago = datetime.now() - pd.Timedelta(days=7)
        recent = len(team_jobs[team_jobs['date_posted'] >= seven_days_ago])
        print(f"📅 Posted in Last 7 Days: {recent}")

        # Count enriched jobs
        if apollo_enabled:
            enriched_count = len([j for _, j in team_jobs.iterrows()
                                 if pd.notna(j.get('contact_1_email', ''))])
            print(f"👤 Jobs with Contact Info: {enriched_count}")
        print()

        # Save to CSV for Chris Jones
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("chris_jones_leads/output")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"chris_jones_pc_jobs_{timestamp}.csv"

        # Save with all columns including company info and contacts
        save_columns = ['title', 'company', 'location', 'date_posted', 'job_url']
        if apollo_enabled:
            save_columns.extend([
                'company_size', 'company_website', 'company_phone', 'company_industry',
                'contact_1_name', 'contact_1_title', 'contact_1_email', 'contact_1_phone', 'contact_1_linkedin',
                'contact_2_name', 'contact_2_title', 'contact_2_email', 'contact_2_phone', 'contact_2_linkedin',
                'contact_3_name', 'contact_3_title', 'contact_3_email', 'contact_3_phone', 'contact_3_linkedin'
            ])

        team_jobs[save_columns].to_csv(output_file, index=False)

        print(f"📁 Saved to: {output_file}")

        # Also save as JSON for dashboard
        json_output = []
        for _, job in team_jobs.iterrows():
            job_data = {
                'title': str(job.get('title', '') or ''),
                'company': str(job.get('company', '') or ''),
                'location': str(job.get('location', '') or ''),
                'date_posted': job.get('date_posted').strftime('%Y-%m-%d') if pd.notna(job.get('date_posted')) else 'N/A',
                'url': str(job.get('job_url', '') or ''),
                'source': str(job.get('site', '') or job.get('source', '') or 'Indeed'),  # Add job source
                'description': str(job.get('description', '') or '')[:200]  # First 200 chars
            }

            # Add company info if available
            if apollo_enabled:
                company_size = job.get('company_size', '')
                if pd.notna(company_size) and company_size:
                    job_data['company_size'] = int(company_size) if str(company_size).isdigit() else str(company_size)
                    job_data['company_website'] = str(job.get('company_website', '') or '')
                    job_data['company_phone'] = str(job.get('company_phone', '') or '')
                    job_data['company_industry'] = str(job.get('company_industry', '') or '')

                # Add contacts
                job_data['contacts'] = []
                for i in range(1, 4):
                    contact_name = job.get(f'contact_{i}_name', '')
                    if pd.notna(contact_name) and contact_name:
                        job_data['contacts'].append({
                            'name': str(job.get(f'contact_{i}_name', '') or ''),
                            'title': str(job.get(f'contact_{i}_title', '') or ''),
                            'email': str(job.get(f'contact_{i}_email', '') or ''),
                            'phone': str(job.get(f'contact_{i}_phone', '') or ''),
                            'linkedin': str(job.get(f'contact_{i}_linkedin', '') or '')
                        })

            json_output.append(job_data)

        json_file = output_dir / f"chris_jones_pc_jobs_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2)

        print(f"📁 JSON saved to: {json_file}")

        # Create dashboard data file
        dashboard_data = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_jobs': len(team_jobs),
            'commercial_specific': commercial_specific,
            'producers': producers,
            'account_managers': account_mgrs,
            'underwriters': underwriters,
            'brokers': brokers,
            'recent_7_days': recent,
            'enriched_count': enriched_count if apollo_enabled else 0,
            'jobs': json_output
        }

        dashboard_file = Path("chris_jones_leads/docs/chris_jones_pc_data.json")
        dashboard_file.parent.mkdir(parents=True, exist_ok=True)

        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2)

        print(f"📁 Dashboard data saved to: {dashboard_file}")
        print()
        print("=" * 80)
        print("✅ CHRIS JONES P&C LEADS COMPLETE")
        print("=" * 80)

    except Exception as error:
        print(f"❌ Error: {error}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_chris_jones_pc_jobs()
