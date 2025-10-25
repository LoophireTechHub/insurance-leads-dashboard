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
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path
import hashlib

# JobSpy import
try:
    from jobspy import scrape_jobs
except ImportError:
    logger.error("JobSpy not installed. Run: pip install python-jobspy")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("leads_pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

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
    
    def fetch_jobs_from_indeed_jobspy(self, search_term: str, results_wanted: int = 50) -> List[Dict]:
        """Fetch jobs from Indeed using JobSpy library - direct scraping"""
        logger.info(f"🔍 Scraping Indeed with JobSpy for: {search_term}")

        try:
            jobs_df = scrape_jobs(
                site_name=["indeed"],
                search_term=search_term,
                location="United States",
                results_wanted=results_wanted,
                hours_old=2160,  # 90 days
                country_indeed='USA'
            )

            if jobs_df is None or jobs_df.empty:
                logger.warning(f"  No jobs found for: {search_term}")
                return []

            logger.info(f"  ✅ Retrieved {len(jobs_df)} Indeed jobs for '{search_term}'")

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

        # Fetch from Indeed for each search term using JobSpy
        for search_term in SEARCH_TERMS:
            indeed_jobs = self.fetch_jobs_from_indeed_jobspy(search_term, results_wanted=50)

            # Normalize JobSpy data to common format and filter for insurance jobs
            insurance_count = 0
            filtered_count = 0
            for job in indeed_jobs:
                # JobSpy returns consistent field names
                normalized_job = {
                    'title': job.get('title', ''),
                    'company_name': job.get('company', ''),
                    'company_website': job.get('company_url', ''),
                    'location': job.get('location', ''),
                    'location_type': job.get('job_type', ''),  # remote, onsite, hybrid
                    'posted_date': str(job.get('date_posted', '')),
                    'platform_url': job.get('job_url', ''),
                    'description': str(job.get('description', ''))[:1000],
                    'salary_min': job.get('min_amount', ''),
                    'salary_max': job.get('max_amount', ''),
                    'salary_currency': job.get('currency', ''),
                    'employment_type': job.get('job_type', ''),
                    'source': 'indeed_jobspy'
                }

                # STRICT FILTER: Only add if insurance-related
                if self.is_insurance_related(normalized_job):
                    all_jobs.append(normalized_job)
                    insurance_count += 1
                else:
                    filtered_count += 1

            logger.info(f"  Insurance jobs: {insurance_count}, Filtered out: {filtered_count}")
            time.sleep(3)  # Rate limiting between searches

        logger.info(f"✅ Retrieved {len(all_jobs)} total insurance jobs from JobSpy")

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
        """Add Apollo.io data"""
        try:
            # Get company name from Apify data (company_name field)
            company = job.get('company_name', '') or ''
            company = company.strip() if company else ''
            if not company or company == 'N/A':
                logger.debug(f"Skipping Apollo for job '{job.get('title', 'Unknown')}' - no company name")
                return job

            logger.info(f"Enriching: {company}")
            headers = {"X-Api-Key": self.apollo_token, "Content-Type": "application/json"}
            search_data = {"q_organization_name": company, "page": 1, "per_page": 1}

            response = requests.post(
                f"{APOLLO_BASE_URL}/organizations/search",
                headers=headers,
                json=search_data,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('organizations'):
                    org = data['organizations'][0]
                    job['company_website'] = org.get('website_url', '')
                    job['company_phone'] = org.get('phone', '')
                    logger.info(f"  ✓ Found org: {org.get('name', company)}")

                    contacts = self.get_apollo_contacts(org.get('id'), company)
                    for i, contact in enumerate(contacts[:3], 1):
                        job[f'leadership_{i}_name'] = contact.get('name', '')
                        job[f'leadership_{i}_title'] = contact.get('title', '')
                        job[f'leadership_{i}_email'] = contact.get('email', '')
                    if contacts:
                        logger.info(f"  ✓ Found {len(contacts)} contacts")
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
                "q_organization_id": org_id,
                "titles": ["CEO", "President", "Director", "Manager", "VP"],
                "page": 1,
                "per_page": 3
            }
            
            response = requests.post(
                f"{APOLLO_BASE_URL}/people/search",
                headers=headers,
                json=search_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('people', [])[:3]
        except:
            pass
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
            'Leadership 1 Name', 'Leadership 1 Title', 'Leadership 1 Email',
            'Leadership 2 Name', 'Leadership 2 Title', 'Leadership 2 Email',
            'Leadership 3 Name', 'Leadership 3 Title', 'Leadership 3 Email',
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
                    'Leadership 2 Name': job.get('leadership_2_name', ''),
                    'Leadership 2 Title': job.get('leadership_2_title', ''),
                    'Leadership 2 Email': job.get('leadership_2_email', ''),
                    'Leadership 3 Name': job.get('leadership_3_name', ''),
                    'Leadership 3 Title': job.get('leadership_3_title', ''),
                    'Leadership 3 Email': job.get('leadership_3_email', ''),
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
            if lead_id not in seen_ids and lead_id not in self.collected_leads:
                seen_ids.add(lead_id)
                job['lead_id'] = lead_id
                unique_jobs.append(job)
        
        logger.info(f"Step 3: {len(unique_jobs)} unique new jobs")
        
        logger.info("Step 4: Enriching with Apollo.io...")
        for i, job in enumerate(unique_jobs, 1):
            print(f"Processing {i}/{len(unique_jobs)}", end="\r")
            enriched_job = self.enrich_with_apollo(job)
            enriched_job['urgency_score'] = self.calculate_urgency_score(enriched_job)
            time.sleep(0.5)
        
        logger.info("Step 5: Selecting top 20 leads...")
        sorted_jobs = sorted(unique_jobs, key=lambda x: x.get('urgency_score', 0), reverse=True)
        top_leads = sorted_jobs[:20]
        
        logger.info("Step 6: Saving to CSV...")
        csv_file = self.save_to_csv(top_leads)
        
        for job in top_leads:
            self.collected_leads.add(job.get('lead_id'))
        self.save_collected_leads()
        
        logger.info("="*50)
        logger.info(f"✅ Pipeline completed!")
        logger.info(f"📁 Output: {csv_file}")
        logger.info(f"📊 Saved {len(top_leads)} leads")
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
