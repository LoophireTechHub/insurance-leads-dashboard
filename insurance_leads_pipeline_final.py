#!/usr/bin/env python3
"""
Insurance Leads Pipeline - Production Version with JobSpy
Pulls jobs from Indeed via JobSpy, enriches with Apollo, scores by urgency
"""

import os
import sys
import json
import logging
import requests
import csv
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path
import hashlib

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("leads_pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# JobSpy import (after logging is configured)
try:
    from jobspy import scrape_jobs
    import pandas as pd
except ImportError as e:
    logger.error(f"Required library not installed: {e}")
    logger.error("Run: pip install python-jobspy pandas")
    sys.exit(1)

APOLLO_BASE_URL = "https://api.apollo.io/v1"

# Precise insurance search terms with Boolean operators to exclude tech jobs
SEARCH_TERMS = [
    '"Commercial Insurance Underwriter" insurance -software -developer -web',
    '"Commercial Lines Manager" insurance -software -developer -web',
    '"Insurance Risk Manager" insurance -software -developer -web',
    '"Commercial P&C Specialist" insurance -software -developer -web',
    '"Commercial Insurance Broker" insurance -software -developer -web',
    '"Risk Assessment Manager" insurance -software -developer -web'
]

class LeadsPipeline:
    def __init__(self):
        self.apollo_token = os.environ.get('APOLLO_API_TOKEN')

        if not self.apollo_token:
            raise ValueError("APOLLO_API_TOKEN not set")

        self.output_dir = Path("leads_output")
        self.output_dir.mkdir(exist_ok=True)

        self.collected_leads_file = Path("collected_leads.json")
        self.collected_leads = self.load_collected_leads()

        logger.info("Pipeline initialized successfully with JobSpy")
    
    def load_collected_leads(self) -> set:
        if self.collected_leads_file.exists():
            try:
                with open(self.collected_leads_file, 'r') as f:
                    data = json.load(f)
                    return set(data)
            except:
                return set()
        return set()
    
    def save_collected_leads(self):
        with open(self.collected_leads_file, 'w') as f:
            json.dump(list(self.collected_leads), f, indent=2)
    
    def generate_lead_id(self, job: Dict) -> str:
        unique_str = f"{job.get('company_name', '')}{job.get('title', '')}{job.get('location', '')}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def fetch_jobs_from_multiple_sources(self, search_term: str, results_wanted: int = 50) -> List[Dict]:
        """Fetch jobs from multiple job boards using JobSpy library"""
        logger.info(f"🔍 Scraping multiple job boards with JobSpy for: {search_term}")

        try:
            # Scrape from Indeed, LinkedIn, and Google (Google aggregates from many sources)
            jobs_df = scrape_jobs(
                site_name=["indeed", "linkedin", "google"],
                search_term=search_term,
                location="United States",
                results_wanted=results_wanted,
                hours_old=2160,  # 90 days
                country_indeed='USA',
                linkedin_fetch_description=False,  # Faster scraping
                offset=0  # Start from beginning
            )

            if jobs_df is None or jobs_df.empty:
                logger.warning(f"  No jobs found for: {search_term}")
                return []

            logger.info(f"  ✅ Retrieved {len(jobs_df)} jobs from multiple sources for '{search_term}'")

            # Convert DataFrame to list of dicts
            jobs_list = jobs_df.to_dict('records')
            return jobs_list

        except Exception as e:
            logger.error(f"  ❌ JobSpy error for '{search_term}': {e}")
            return []

    def fetch_jobs_with_jobspy(self) -> List[Dict]:
        """Fetch jobs using JobSpy - fast and accurate"""
        logger.info(f"🚀 Starting JobSpy scraping for {len(SEARCH_TERMS)} insurance job types...")

        all_jobs = []

        # Fetch from multiple job boards for each search term using JobSpy
        for search_term in SEARCH_TERMS:
            multi_source_jobs = self.fetch_jobs_from_multiple_sources(search_term, results_wanted=50)

            # Normalize JobSpy data to common format and filter for insurance jobs
            insurance_count = 0
            filtered_count = 0
            for job in multi_source_jobs:
                # JobSpy returns consistent field names
                # Convert all values to strings to handle floats/None
                normalized_job = {
                    'title': str(job.get('title', '') or ''),
                    'company_name': str(job.get('company', '') or ''),
                    'company_website': str(job.get('company_url', '') or ''),
                    'location': str(job.get('location', '') or ''),
                    'location_type': str(job.get('job_type', '') or ''),
                    'posted_date': str(job.get('date_posted', '') or ''),
                    'platform_url': str(job.get('job_url', '') or ''),
                    'description': str(job.get('description', '') or '')[:1000],
                    'salary_min': str(job.get('min_amount', '') or ''),
                    'salary_max': str(job.get('max_amount', '') or ''),
                    'salary_currency': str(job.get('currency', '') or ''),
                    'employment_type': str(job.get('job_type', '') or ''),
                    'source': str(job.get('site', 'unknown') or 'unknown')  # Track which job board
                }

                # STRICT FILTER: Only add if insurance-related
                if self.is_insurance_related(normalized_job):
                    all_jobs.append(normalized_job)
                    insurance_count += 1
                else:
                    filtered_count += 1

            logger.info(f"  Insurance jobs: {insurance_count}, Filtered out: {filtered_count}")
            time.sleep(3)  # Rate limiting between searches

        logger.info(f"✅ Retrieved {len(all_jobs)} total insurance jobs from multiple sources")

        # Log source breakdown
        source_counts = {}
        for job in all_jobs:
            source = job.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        logger.info(f"  Source breakdown: {source_counts}")

        # Deduplicate jobs based on company + title + location
        unique_jobs = []
        seen_combinations = set()

        for job in all_jobs:
            # Create unique key from company, title, and location
            key = f"{job.get('company_name', '').lower()}|{job.get('title', '').lower()}|{job.get('location', '').lower()}"

            if key not in seen_combinations and job.get('company_name'):
                seen_combinations.add(key)
                unique_jobs.append(job)

        logger.info(f"After deduplication: {len(unique_jobs)} unique jobs")

        # Log sample job structure for debugging
        if unique_jobs:
            sample_job = unique_jobs[0]
            logger.info(f"Sample job fields: {list(sample_job.keys())}")
            logger.info(f"Sample company: '{sample_job.get('company_name', 'MISSING')}'")
            logger.info(f"Sample title: '{sample_job.get('title', 'MISSING')}'")
            logger.info(f"Sample source: '{sample_job.get('source', 'MISSING')}'")

        return unique_jobs
    
    def filter_jobs_by_date(self, jobs: List[Dict]) -> List[Dict]:
        """Filter to jobs posted 14+ days ago"""
        filtered = []
        cutoff_date = datetime.now() - timedelta(days=14)
        
        for job in jobs:
            try:
                posted_date_str = job.get('posted_date', '')
                if not posted_date_str:
                    continue
                
                posted_date = None
                for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                    try:
                        if 'T' in posted_date_str:
                            posted_date = datetime.fromisoformat(posted_date_str.split('.')[0])
                        else:
                            posted_date = datetime.strptime(posted_date_str, fmt)
                        break
                    except:
                        continue
                
                if posted_date and posted_date <= cutoff_date:
                    job['posted_date_parsed'] = posted_date
                    filtered.append(job)
            except Exception as e:
                logger.debug(f"Date parsing error: {e}")
        
        logger.info(f"Filtered to {len(filtered)} jobs posted 14+ days ago")
        return filtered
    
    def enrich_with_apollo(self, job: Dict) -> Dict:
        """Add Apollo.io data with improved matching"""
        try:
            # Get company name and location from job data
            company = job.get('company_name', '') or ''
            company = company.strip() if company else ''
            location = job.get('location', '') or ''

            if not company or company == 'N/A' or company == 'nan':
                logger.debug(f"Skipping Apollo for job '{job.get('title', 'Unknown')}' - no company name")
                return job

            logger.info(f"Enriching: {company} ({location})")
            headers = {"X-Api-Key": self.apollo_token, "Content-Type": "application/json"}

            # Search for organizations with company name, location context, and size filter
            search_data = {
                "q_organization_name": company,
                "organization_num_employees_ranges": ["10,20", "20,50", "51,100", "101,200", "201,500"],  # 10-500 employees
                "page": 1,
                "per_page": 5  # Get more results to find best match
            }

            response = requests.post(
                f"{APOLLO_BASE_URL}/organizations/search",
                headers=headers,
                json=search_data,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                orgs = data.get('organizations', [])

                if orgs:
                    # Find best matching organization
                    best_match = None
                    location_state = location.split(',')[-1].strip() if ',' in location else ''

                    for org in orgs:
                        org_name = org.get('name', '').lower()
                        company_lower = company.lower()

                        # Check if name matches closely
                        if org_name == company_lower or company_lower in org_name or org_name in company_lower:
                            # Check if location matches (US-based)
                            primary_domain = org.get('primary_domain') or ''
                            org_country = primary_domain.endswith('.com') or org.get('country') == 'United States'

                            # Check location match (state)
                            org_city = org.get('city', '').lower()
                            org_state = org.get('state', '').lower()
                            location_matches = location_state and (location_state.lower() in org_state or org_state in location.lower())

                            # Prioritize: 1) US + location match, 2) US only, 3) any match
                            if location_matches and org_country:
                                best_match = org
                                break  # Perfect match - stop searching
                            elif org_country and not best_match:
                                best_match = org  # Good match - keep looking for better
                            elif not best_match:
                                best_match = org  # Acceptable match - keep looking

                    if best_match:
                        # Verify company size is within range (10-500 employees)
                        employee_count = best_match.get('estimated_num_employees', 0)
                        if employee_count < 10 or employee_count > 500:
                            logger.info(f"  ✗ Skipped: {best_match.get('name')} - {employee_count} employees (outside 10-500 range)")
                            return job

                        job['company_website'] = best_match.get('website_url', '')
                        job['company_phone'] = best_match.get('phone', '')
                        logger.info(f"  ✓ Matched: {best_match.get('name')} | {best_match.get('city', 'Unknown')}, {best_match.get('state', 'Unknown')} | {employee_count} employees")

                        # Get contacts from the matched organization
                        contacts = self.get_apollo_contacts(best_match.get('id'), company)
                        for i, contact in enumerate(contacts[:3], 1):
                            job[f'leadership_{i}_name'] = contact.get('name', '')
                            job[f'leadership_{i}_title'] = contact.get('title', '')
                            job[f'leadership_{i}_email'] = contact.get('email', '')
                            job[f'leadership_{i}_linkedin'] = contact.get('linkedin_url', '')
                            job[f'leadership_{i}_phone'] = contact.get('phone_numbers', [{}])[0].get('sanitized_number', '') if contact.get('phone_numbers') else ''
                        if contacts:
                            logger.info(f"  ✓ Found {len(contacts)} contacts")
                    else:
                        logger.warning(f"  ✗ No good match found for: {company}")
                else:
                    logger.warning(f"  ✗ No org found for: {company}")
            else:
                logger.warning(f"  ✗ Apollo API error {response.status_code} for: {company}")
        except Exception as e:
            logger.error(f"Apollo enrichment error for {job.get('company_name', 'Unknown')}: {e}")

        return job
    
    def get_apollo_contacts(self, org_id: str, company: str) -> List[Dict]:
        """Get leadership contacts"""
        try:
            headers = {"X-Api-Key": self.apollo_token, "Content-Type": "application/json"}
            search_data = {
                "organization_ids": [org_id],  # Changed from q_organization_id to organization_ids (array)
                "person_titles": ["CEO", "CFO", "President", "VP", "Director", "Manager", "Owner", "Partner"],
                "page": 1,
                "per_page": 3
            }

            logger.debug(f"  Searching people for org_id: {org_id}")

            response = requests.post(
                f"{APOLLO_BASE_URL}/mixed_people/search",  # Changed from /people/search to /mixed_people/search
                headers=headers,
                json=search_data,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                people = data.get('people', [])
                if people:
                    logger.debug(f"  Got {len(people)} people: {[p.get('name') for p in people]}")
                return people[:3]
            else:
                logger.warning(f"  People search failed: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            logger.warning(f"  Error getting contacts: {e}")
        return []
    
    def calculate_urgency_score(self, job: Dict) -> float:
        """Score 0-100, older = higher"""
        try:
            posted_date = job.get('posted_date_parsed')
            if not posted_date:
                return 0.0
            
            days_open = (datetime.now() - posted_date).days
            
            if days_open <= 14:
                return 0.0
            elif days_open >= 90:
                return 100.0
            else:
                return ((days_open - 14) / 76) * 100
        except:
            return 0.0
    

    def is_insurance_related(self, job: Dict) -> bool:
        """ULTRA STRICT: Only allow exact insurance job titles - ZERO tolerance for web dev"""
        title = (job.get('title') or '').lower()
        description = (job.get('description') or '')[:1000].lower()

        # IMMEDIATE REJECTION: Web developer/software keywords in title
        web_dev_reject_keywords = [
            'web developer', 'web design', 'software developer', 'software engineer',
            'full stack', 'front end', 'front-end', 'backend', 'back-end', 'back end',
            'react', 'angular', 'vue', 'javascript', 'python developer', 'java developer',
            'php', 'wordpress', 'node.js', 'nodejs', '.net developer', 'c# developer',
            'ruby', 'programmer', 'coding', 'devops', 'data engineer', 'ml engineer',
            'app developer', 'mobile developer', 'ios developer', 'android developer',
            'ui developer', 'ux developer', 'web app', 'software dev',
            'drupal', 'magento', 'laravel', 'django', 'flask', 'spring', 'hibernate',
            'css', 'html', 'typescript', 'sql developer', 'database developer',
            'cloud engineer', 'solutions architect', 'technical architect', 'it specialist',
            'systems administrator', 'network engineer', 'security engineer', 'qa engineer',
            'test engineer', 'automation engineer', 'site reliability', 'sre', 'platform engineer'
        ]

        # Reject if ANY web dev keyword in title
        for keyword in web_dev_reject_keywords:
            if keyword in title:
                logger.info(f"  ❌ REJECTED (web dev): '{title}' contains '{keyword}'")
                return False

        # REQUIRED: Title MUST contain insurance-specific keywords
        required_title_keywords = [
            'insurance', 'underwriter', 'underwriting', 'broker', 'brokerage',
            'claims', 'actuary', 'actuarial', 'risk manager', 'risk management',
            'p&c', 'p & c', 'property casualty', 'commercial lines', 'personal lines',
            'surety', 'reinsurance', 'loss control'
        ]

        # Title must have insurance keyword
        title_has_insurance = any(kw in title for kw in required_title_keywords)
        if not title_has_insurance:
            logger.info(f"  ❌ REJECTED (no insurance keyword in title): '{title}'")
            return False

        # If description is too short or empty, just rely on title
        if len(description) < 50:
            logger.info(f"  ✅ APPROVED (title match, short description): '{title}'")
            return True

        # Description should also confirm insurance context (if it's substantial)
        description_keywords = [
            'insurance', 'underwrite', 'broker', 'policy', 'premium', 'coverage',
            'claims', 'risk', 'casualty', 'liability', 'actuary'
        ]
        description_has_insurance = any(kw in description for kw in description_keywords)
        if not description_has_insurance:
            logger.info(f"  ❌ REJECTED (no insurance context in description): '{title}'")
            return False

        # PASSED ALL CHECKS
        logger.info(f"  ✅ APPROVED: '{title}'")
        return True

    def save_to_csv(self, jobs: List[Dict]) -> str:
        """Save to CSV with all fields"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.output_dir / f"insurance_leads_{timestamp}.csv"

        fieldnames = [
            'Job Title', 'Company Name', 'Location', 'Location Type', 'Job URL', 'Posted Date',
            'Days Open', 'Salary Range', 'Employment Type', 'Source', 'Company Website', 'Phone Number',
            'Leadership 1 Name', 'Leadership 1 Title', 'Leadership 1 Email', 'Leadership 1 Phone', 'Leadership 1 LinkedIn',
            'Leadership 2 Name', 'Leadership 2 Title', 'Leadership 2 Email', 'Leadership 2 Phone', 'Leadership 2 LinkedIn',
            'Leadership 3 Name', 'Leadership 3 Title', 'Leadership 3 Email', 'Leadership 3 Phone', 'Leadership 3 LinkedIn',
            'Urgency Score'
        ]

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for job in jobs:
                days_open = 0
                if job.get('posted_date_parsed'):
                    days_open = (datetime.now() - job['posted_date_parsed']).days

                # Format salary range
                salary_range = ''
                if job.get('salary_min') and job.get('salary_max'):
                    currency = job.get('salary_currency', 'USD')
                    salary_range = f"{currency} {job['salary_min']}-{job['salary_max']}"

                row = {
                    'Job Title': job.get('title', ''),
                    'Company Name': job.get('company_name', ''),
                    'Location': job.get('location', ''),
                    'Location Type': job.get('location_type', ''),
                    'Job URL': job.get('platform_url', ''),
                    'Posted Date': job.get('posted_date', ''),
                    'Days Open': days_open,
                    'Salary Range': salary_range,
                    'Employment Type': job.get('employment_type', ''),
                    'Source': job.get('source', 'indeed'),
                    'Company Website': job.get('company_website', ''),
                    'Phone Number': job.get('company_phone', ''),
                    'Leadership 1 Name': job.get('leadership_1_name', ''),
                    'Leadership 1 Title': job.get('leadership_1_title', ''),
                    'Leadership 1 Email': job.get('leadership_1_email', ''),
                    'Leadership 1 Phone': job.get('leadership_1_phone', ''),
                    'Leadership 1 LinkedIn': job.get('leadership_1_linkedin', ''),
                    'Leadership 2 Name': job.get('leadership_2_name', ''),
                    'Leadership 2 Title': job.get('leadership_2_title', ''),
                    'Leadership 2 Email': job.get('leadership_2_email', ''),
                    'Leadership 2 Phone': job.get('leadership_2_phone', ''),
                    'Leadership 2 LinkedIn': job.get('leadership_2_linkedin', ''),
                    'Leadership 3 Name': job.get('leadership_3_name', ''),
                    'Leadership 3 Title': job.get('leadership_3_title', ''),
                    'Leadership 3 Email': job.get('leadership_3_email', ''),
                    'Leadership 3 Phone': job.get('leadership_3_phone', ''),
                    'Leadership 3 LinkedIn': job.get('leadership_3_linkedin', ''),
                    'Urgency Score': f"{job.get('urgency_score', 0):.2f}"
                }
                writer.writerow(row)

        return str(csv_file)
    
    def run(self):
        """Main pipeline execution"""
        logger.info("="*50)
        logger.info("Starting Insurance Leads Pipeline with JobSpy")
        logger.info("="*50)

        logger.info("Step 1: Fetching jobs from Indeed via JobSpy...")
        jobs = self.fetch_jobs_with_jobspy()
        
        if not jobs:
            logger.warning("No jobs fetched")
            return
        
        logger.info("Step 2: Filtering for jobs 14+ days old...")
        filtered_jobs = self.filter_jobs_by_date(jobs)
        
        if not filtered_jobs:
            logger.info("No jobs older than 14 days found")
            filtered_jobs = jobs[:20]
        
        unique_jobs = []
        # Filter for insurance-related jobs only
        # Keep all jobs from Apify since they are already filtered
        # filtered_jobs already contains relevant jobs from search terms
        logger.info(f"Filtered to {len(filtered_jobs)} insurance-related jobs")
        seen_ids = set()
        for job in filtered_jobs:
            lead_id = self.generate_lead_id(job)
            # REMOVED: lead_id not in self.collected_leads
            # Allow leads to reappear each day with shuffling for variety
            if lead_id not in seen_ids:
                seen_ids.add(lead_id)
                job['lead_id'] = lead_id
                unique_jobs.append(job)

        logger.info(f"Step 3: {len(unique_jobs)} unique jobs (deduplicated within this run)")
        
        logger.info("Step 4: Enriching with Apollo.io...")
        for i, job in enumerate(unique_jobs, 1):
            print(f"Processing {i}/{len(unique_jobs)}", end="\r")
            enriched_job = self.enrich_with_apollo(job)
            enriched_job['urgency_score'] = self.calculate_urgency_score(enriched_job)
            time.sleep(0.5)
        
        logger.info("Step 5: Selecting top 50 leads with company diversity...")

        # Deduplicate by company - keep only the highest urgency job per company
        company_jobs = {}
        for job in unique_jobs:
            company = job.get('company_name', '').lower().strip()
            if not company or company == 'nan' or company == 'n/a':
                # Keep jobs without company names
                if 'no_company' not in company_jobs:
                    company_jobs['no_company'] = []
                company_jobs['no_company'].append(job)
            else:
                if company not in company_jobs:
                    company_jobs[company] = []
                company_jobs[company].append(job)

        # For each company, keep only the highest urgency job
        diverse_jobs = []
        for company, jobs_list in company_jobs.items():
            # Sort by urgency score descending
            jobs_list.sort(key=lambda x: x.get('urgency_score', 0), reverse=True)
            # Take only the top job from this company
            diverse_jobs.append(jobs_list[0])

        logger.info(f"  Reduced from {len(unique_jobs)} to {len(diverse_jobs)} jobs (one per company)")

        # Group jobs into tiers, then shuffle within each tier
        high_urgency = [j for j in diverse_jobs if j.get('urgency_score', 0) > 75]
        medium_urgency = [j for j in diverse_jobs if 50 < j.get('urgency_score', 0) <= 75]
        low_urgency = [j for j in diverse_jobs if j.get('urgency_score', 0) <= 50]

        # Shuffle each tier
        random.shuffle(high_urgency)
        random.shuffle(medium_urgency)
        random.shuffle(low_urgency)

        # Combine shuffled tiers
        shuffled_jobs = high_urgency + medium_urgency + low_urgency

        # Take top 50 from shuffled list
        top_leads = shuffled_jobs[:50]

        logger.info(f"  Selected {len(high_urgency)} high urgency (>75), {len(medium_urgency)} medium (50-75), {len(low_urgency)} low (<=50)")
        logger.info(f"  Final selection: {len(top_leads)} leads")
        
        logger.info("Step 6: Saving to CSV...")
        csv_file = self.save_to_csv(top_leads)

        # REMOVED: collected_leads tracking
        # Leads are now shuffled daily for variety instead of being permanently excluded

        logger.info("Step 7: Generating HTML dashboard...")
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "generate_dashboard.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info("  ✅ Dashboard generated successfully")
            else:
                logger.warning(f"  ⚠️ Dashboard generation had issues: {result.stderr}")
        except Exception as e:
            logger.warning(f"  ⚠️ Could not generate dashboard: {e}")

        logger.info("="*50)
        logger.info(f"✅ Pipeline completed!")
        logger.info(f"📁 CSV Output: {csv_file}")
        logger.info(f"📊 Saved {len(top_leads)} leads")
        logger.info(f"🌐 Dashboard: docs/index.html")
        logger.info("="*50)

if __name__ == "__main__":
    try:
        pipeline = LeadsPipeline()
        pipeline.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
