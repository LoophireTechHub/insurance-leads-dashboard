#!/usr/bin/env python3
"""
Insurance Leads Pipeline - Production Version
Pulls jobs from Apify, enriches with Apollo, scores by urgency
"""

import os
import sys
import json
import logging
import requests
import csv
import time
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path
import hashlib

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

APIFY_ACTOR_ID = "8QfidRKcSVYICkwrq"
APIFY_BASE_URL = "https://api.apify.com/v2"
APOLLO_BASE_URL = "https://api.apollo.io/v1"

SEARCH_TERMS = [
    "Commercial Insurance Underwriter",
    "Commercial Lines Manager",
    "Insurance Risk Manager",
    "Commercial P&C Specialist",
    "Commercial Insurance Broker",
    "Risk Assessment Manager"
]

class LeadsPipeline:
    def __init__(self):
        self.apify_token = os.environ.get('APIFY_API_TOKEN')
        self.apollo_token = os.environ.get('APOLLO_API_TOKEN')
        
        if not self.apify_token:
            raise ValueError("APIFY_API_TOKEN not set")
        if not self.apollo_token:
            raise ValueError("APOLLO_API_TOKEN not set")
        
        self.output_dir = Path("leads_output")
        self.output_dir.mkdir(exist_ok=True)
        
        self.collected_leads_file = Path("collected_leads.json")
        self.collected_leads = self.load_collected_leads()
        
        logger.info("Pipeline initialized successfully")
    
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
        unique_str = f"{job.get('company', '')}{job.get('title', '')}{job.get('location', '')}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def fetch_jobs_from_apify(self) -> List[Dict]:
        """Fetch jobs using correct Apify format"""
        logger.info(f"Starting Apify search for {len(SEARCH_TERMS)} job titles...")
        
        actor_input = {
            "search_terms": SEARCH_TERMS,
            "max_results": 50,
            "posted_since": "1 month",
            "location": "United States",
            "country": "United States"
        }
        
        response = requests.post(
            f"{APIFY_BASE_URL}/acts/{APIFY_ACTOR_ID}/runs",
            headers={
                "Authorization": f"Bearer {self.apify_token}",
                "Content-Type": "application/json"
            },
            json=actor_input
        )
        
        if response.status_code != 201:
            logger.error(f"Failed to start: {response.text}")
            return []
        
        run_data = response.json()['data']
        run_id = run_data['id']
        logger.info(f"Actor run started: {run_id}")
        
        logger.info("Waiting for results (this may take 1-3 minutes)...")
        max_wait = 300
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_response = requests.get(
                f"{APIFY_BASE_URL}/actor-runs/{run_id}",
                headers={"Authorization": f"Bearer {self.apify_token}"}
            )
            
            if status_response.status_code == 200:
                status = status_response.json()['data']['status']
                if status in ['SUCCEEDED', 'FAILED', 'ABORTED']:
                    logger.info(f"Run completed with status: {status}")
                    break
            time.sleep(5)
            print(".", end="", flush=True)
        
        print()
        
        dataset_id = run_data['defaultDatasetId']
        results_response = requests.get(
            f"{APIFY_BASE_URL}/datasets/{dataset_id}/items",
            headers={"Authorization": f"Bearer {self.apify_token}"}
        )
        
        if results_response.status_code == 200:
            jobs = results_response.json()
            logger.info(f"Retrieved {len(jobs)} total jobs")
            return jobs
        
        return []
    
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
            company = job.get('company', '').strip()
            if not company or company == 'N/A':
                return job
            
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
                    
                    contacts = self.get_apollo_contacts(org.get('id'), company)
                    for i, contact in enumerate(contacts[:3], 1):
                        job[f'leadership_{i}_name'] = contact.get('name', '')
                        job[f'leadership_{i}_title'] = contact.get('title', '')
                        job[f'leadership_{i}_email'] = contact.get('email', '')
        except Exception as e:
            logger.debug(f"Apollo enrichment error: {e}")
        
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
        """Check if job is insurance-related"""
        title = (job.get('title') or '').lower()
        company = (job.get('company_name') or '').lower()
        description = (job.get('description') or '')[:1000].lower()
        
        insurance_keywords = [
            'insurance', 'underwriter', 'commercial lines', 'p&c',
            'casualty', 'risk manager', 'broker', 'claims', 'surety',
            'actuary', 'policy', 'premium', 'coverage'
        ]
        
        return any(kw in title for kw in insurance_keywords) or                any(kw in company for kw in insurance_keywords) or                any(kw in description for kw in insurance_keywords)

    def save_to_csv(self, jobs: List[Dict]) -> str:
        """Save to CSV with all fields"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.output_dir / f"insurance_leads_{timestamp}.csv"
        
        fieldnames = [
            'Job Title', 'Company Name', 'Location', 'Job URL', 'Posted Date',
            'Days Open', 'Company Website', 'Phone Number',
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
                
                row = {
                    'Job Title': job.get('title', ''),
                    'Company Name': job.get('company_name', ''),
                    'Location': job.get('location', ''),
                    'Job URL': job.get('platform_url', job.get('official_url', '')),
                    'Posted Date': job.get('posted_date', ''),
                    'Days Open': days_open,
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
        logger.info("Starting Insurance Leads Pipeline")
        logger.info("="*50)
        
        logger.info("Step 1: Fetching jobs from Apify...")
        jobs = self.fetch_jobs_from_apify()
        
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
        filtered_jobs = [job for job in filtered_jobs if self.is_insurance_related(job)]
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
