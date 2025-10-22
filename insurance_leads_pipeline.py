#!/usr/bin/env python3
"""
Insurance Leads Pipeline
Pulls job listings from Apify, enriches with Apollo.io data, and generates qualified leads
"""

import os
import sys
import json
import logging
import requests
import csv
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import hashlib

# Configure logging
log_dir = Path(".")
log_file = log_dir / "leads_pipeline.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
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

PLATFORMS = ["LinkedIn", "Indeed", "Glassdoor", "ZipRecruiter"]
MAX_RESULTS_PER_SEARCH = 50
MIN_DAYS_POSTED = 14
COUNTRY = "USA"
TOP_LEADS_COUNT = 20

class LeadsPipeline:
    """Main pipeline class for insurance leads generation"""
    
    def __init__(self):
        """Initialize the pipeline with API tokens and file paths"""
        self.apify_token = os.environ.get('APIFY_API_TOKEN')
        self.apollo_token = os.environ.get('APOLLO_API_TOKEN')
        
        if not self.apify_token:
            logger.error("APIFY_API_TOKEN environment variable not set")
            raise ValueError("APIFY_API_TOKEN environment variable not set")
        
        if not self.apollo_token:
            logger.error("APOLLO_API_TOKEN environment variable not set")
            raise ValueError("APOLLO_API_TOKEN environment variable not set")
        
        # Create output directory if it doesn't exist
        self.output_dir = Path("leads_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize collected leads tracking
        self.collected_leads_file = Path("collected_leads.json")
        self.collected_leads = self.load_collected_leads()
        
        logger.info("Pipeline initialized successfully")
    
    def load_collected_leads(self) -> set:
        """Load previously collected lead IDs to prevent duplicates"""
        if self.collected_leads_file.exists():
            try:
                with open(self.collected_leads_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} previously collected leads")
                    return set(data)
            except Exception as e:
                logger.error(f"Error loading collected leads: {e}")
                return set()
        return set()
    
    def save_collected_leads(self):
        """Save collected lead IDs to file"""
        try:
            with open(self.collected_leads_file, 'w') as f:
                json.dump(list(self.collected_leads), f, indent=2)
            logger.info(f"Saved {len(self.collected_leads)} collected lead IDs")
        except Exception as e:
            logger.error(f"Error saving collected leads: {e}")
    
    def generate_lead_id(self, job: Dict) -> str:
        """Generate a unique ID for a job listing"""
        unique_str = f"{job.get('company', '')}{job.get('title', '')}{job.get('location', '')}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def fetch_jobs_from_apify(self) -> List[Dict]:
        """Fetch job listings from Apify for all search terms"""
        all_jobs = []
        
        for search_term in SEARCH_TERMS:
            logger.info(f"Fetching jobs for search term: {search_term}")
            
            try:
                # Prepare the actor input
                actor_input = {
                    "search_query": search_term,
                    "max_results": MAX_RESULTS_PER_SEARCH,
                    "country": COUNTRY,
                    "platforms": PLATFORMS,
                    "posted_since": "month",  # We'll filter by MIN_DAYS_POSTED later
                    "include_remote": True
                }
                
                # Start the actor run
                run_url = f"{APIFY_BASE_URL}/acts/{APIFY_ACTOR_ID}/runs"
                headers = {
                    "Authorization": f"Bearer {self.apify_token}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    run_url,
                    headers=headers,
                    json=actor_input,
                    timeout=30
                )
                
                if response.status_code != 201:
                    logger.error(f"Failed to start Apify actor: {response.status_code} - {response.text}")
                    continue
                
                run_data = response.json()
                run_id = run_data['data']['id']
                
                # Wait for the run to complete
                logger.info(f"Waiting for Apify run {run_id} to complete...")
                self.wait_for_apify_run(run_id)
                
                # Get the results
                results_url = f"{APIFY_BASE_URL}/actor-runs/{run_id}/dataset/items"
                response = requests.get(
                    results_url,
                    headers={"Authorization": f"Bearer {self.apify_token}"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    jobs = response.json()
                    logger.info(f"Retrieved {len(jobs)} jobs for '{search_term}'")
                    
                    # Filter jobs by posting date (14+ days ago)
                    filtered_jobs = self.filter_jobs_by_date(jobs)
                    all_jobs.extend(filtered_jobs)
                else:
                    logger.error(f"Failed to get results: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error fetching jobs for '{search_term}': {e}")
                continue
            
            # Rate limiting between searches
            time.sleep(2)
        
        logger.info(f"Total jobs fetched: {len(all_jobs)}")
        return all_jobs
    
    def wait_for_apify_run(self, run_id: str, max_wait: int = 300):
        """Wait for an Apify actor run to complete"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                url = f"{APIFY_BASE_URL}/actor-runs/{run_id}"
                headers = {"Authorization": f"Bearer {self.apify_token}"}
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    run_data = response.json()
                    status = run_data['data']['status']
                    
                    if status in ['SUCCEEDED', 'FAILED', 'ABORTED']:
                        if status != 'SUCCEEDED':
                            logger.warning(f"Apify run ended with status: {status}")
                        return
                    
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error checking run status: {e}")
                time.sleep(5)
        
        logger.warning(f"Timeout waiting for Apify run {run_id}")
    
    def filter_jobs_by_date(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs to only include those posted 14+ days ago"""
        filtered = []
        cutoff_date = datetime.now() - timedelta(days=MIN_DAYS_POSTED)
        
        for job in jobs:
            try:
                # Parse posted date - this may vary by platform
                posted_date_str = job.get('postedDate', job.get('posted_date', ''))
                if not posted_date_str:
                    continue
                
                # Try different date formats
                posted_date = None
                for date_format in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                    try:
                        posted_date = datetime.strptime(posted_date_str.split('T')[0], '%Y-%m-%d')
                        break
                    except:
                        continue
                
                if posted_date and posted_date <= cutoff_date:
                    job['posted_date_parsed'] = posted_date
                    filtered.append(job)
                    
            except Exception as e:
                logger.debug(f"Error parsing date for job: {e}")
                continue
        
        logger.info(f"Filtered to {len(filtered)} jobs posted 14+ days ago")
        return filtered
    
    def enrich_with_apollo(self, job: Dict) -> Dict:
        """Enrich job data with Apollo.io company and leadership information"""
        try:
            company_name = job.get('company', job.get('company_name', ''))
            if not company_name:
                logger.warning("No company name found for job")
                return job
            
            # Search for company in Apollo
            search_url = f"{APOLLO_BASE_URL}/organizations/search"
            headers = {
                "api_key": self.apollo_token,
                "Content-Type": "application/json"
            }
            
            search_data = {
                "q_organization_name": company_name,
                "page": 1,
                "per_page": 1
            }
            
            response = requests.post(search_url, headers=headers, json=search_data, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"Apollo search failed for {company_name}: {response.status_code}")
                return job
            
            data = response.json()
            if not data.get('organizations'):
                logger.warning(f"No Apollo data found for {company_name}")
                return job
            
            org = data['organizations'][0]
            
            # Add company information
            job['company_website'] = org.get('website_url', '')
            job['company_phone'] = org.get('phone', '')
            
            # Get leadership contacts
            contacts = self.get_apollo_contacts(org.get('id'), company_name)
            for i, contact in enumerate(contacts[:3], 1):
                job[f'leadership_contact_{i}_name'] = contact.get('name', '')
                job[f'leadership_contact_{i}_title'] = contact.get('title', '')
                job[f'leadership_contact_{i}_email'] = contact.get('email', '')
            
            # Fill in empty contact slots
            for i in range(len(contacts) + 1, 4):
                job[f'leadership_contact_{i}_name'] = ''
                job[f'leadership_contact_{i}_title'] = ''
                job[f'leadership_contact_{i}_email'] = ''
            
            logger.info(f"Enriched data for {company_name}")
            
        except Exception as e:
            logger.error(f"Error enriching job with Apollo: {e}")
        
        return job
    
    def get_apollo_contacts(self, org_id: str, company_name: str) -> List[Dict]:
        """Get leadership contacts from Apollo for a company"""
        try:
            contacts_url = f"{APOLLO_BASE_URL}/people/search"
            headers = {
                "api_key": self.apollo_token,
                "Content-Type": "application/json"
            }
            
            # Search for leadership titles
            leadership_titles = [
                "CEO", "President", "Vice President", "Director", 
                "Head of", "Chief", "Manager", "Owner", "Founder"
            ]
            
            search_data = {
                "q_organization_id": org_id,
                "titles": leadership_titles,
                "page": 1,
                "per_page": 3
            }
            
            response = requests.post(contacts_url, headers=headers, json=search_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                contacts = []
                for person in data.get('people', [])[:3]:
                    contacts.append({
                        'name': person.get('name', ''),
                        'title': person.get('title', ''),
                        'email': person.get('email', '')
                    })
                return contacts
            else:
                logger.warning(f"Failed to get contacts for {company_name}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Apollo contacts: {e}")
            return []
    
    def calculate_urgency_score(self, job: Dict) -> float:
        """Calculate urgency score based on days posted (0-100, older = higher)"""
        try:
            posted_date = job.get('posted_date_parsed')
            if not posted_date:
                return 0.0
            
            days_open = (datetime.now() - posted_date).days
            
            # Score calculation: min 14 days = 0, max 90+ days = 100
            if days_open <= MIN_DAYS_POSTED:
                return 0.0
            elif days_open >= 90:
                return 100.0
            else:
                # Linear scaling between 14 and 90 days
                return ((days_open - MIN_DAYS_POSTED) / (90 - MIN_DAYS_POSTED)) * 100
                
        except Exception as e:
            logger.error(f"Error calculating urgency score: {e}")
            return 0.0
    
    def deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs and jobs already collected"""
        unique_jobs = []
        seen_ids = set()
        
        for job in jobs:
            lead_id = self.generate_lead_id(job)
            
            if lead_id not in seen_ids and lead_id not in self.collected_leads:
                seen_ids.add(lead_id)
                job['lead_id'] = lead_id
                unique_jobs.append(job)
        
        logger.info(f"Deduplicated from {len(jobs)} to {len(unique_jobs)} unique new jobs")
        return unique_jobs
    
    def process_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Process all jobs: enrich, score, and prepare for output"""
        processed_jobs = []
        
        for i, job in enumerate(jobs, 1):
            logger.info(f"Processing job {i}/{len(jobs)}")
            
            # Enrich with Apollo data
            enriched_job = self.enrich_with_apollo(job)
            
            # Calculate urgency score
            enriched_job['urgency_score'] = self.calculate_urgency_score(enriched_job)
            
            # Calculate days open
            if enriched_job.get('posted_date_parsed'):
                enriched_job['days_open'] = (datetime.now() - enriched_job['posted_date_parsed']).days
            else:
                enriched_job['days_open'] = 0
            
            processed_jobs.append(enriched_job)
            
            # Rate limiting for Apollo API
            time.sleep(1)
        
        return processed_jobs
    
    def save_to_csv(self, jobs: List[Dict]) -> str:
        """Save jobs to CSV file with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = self.output_dir / f"insurance_leads_{timestamp}.csv"
        
        # Define CSV columns
        fieldnames = [
            'Job Title', 'Company Name', 'Location', 'Job URL', 'Posted Date',
            'Days Open', 'Company Website', 'Phone Number',
            'Leadership Contact 1 Name', 'Leadership Contact 1 Title', 'Leadership Contact 1 Email',
            'Leadership Contact 2 Name', 'Leadership Contact 2 Title', 'Leadership Contact 2 Email',
            'Leadership Contact 3 Name', 'Leadership Contact 3 Title', 'Leadership Contact 3 Email',
            'Urgency Score'
        ]
        
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for job in jobs:
                    row = {
                        'Job Title': job.get('title', job.get('job_title', '')),
                        'Company Name': job.get('company', job.get('company_name', '')),
                        'Location': job.get('location', ''),
                        'Job URL': job.get('url', job.get('job_url', '')),
                        'Posted Date': job.get('postedDate', job.get('posted_date', '')),
                        'Days Open': job.get('days_open', 0),
                        'Company Website': job.get('company_website', ''),
                        'Phone Number': job.get('company_phone', ''),
                        'Leadership Contact 1 Name': job.get('leadership_contact_1_name', ''),
                        'Leadership Contact 1 Title': job.get('leadership_contact_1_title', ''),
                        'Leadership Contact 1 Email': job.get('leadership_contact_1_email', ''),
                        'Leadership Contact 2 Name': job.get('leadership_contact_2_name', ''),
                        'Leadership Contact 2 Title': job.get('leadership_contact_2_title', ''),
                        'Leadership Contact 2 Email': job.get('leadership_contact_2_email', ''),
                        'Leadership Contact 3 Name': job.get('leadership_contact_3_name', ''),
                        'Leadership Contact 3 Title': job.get('leadership_contact_3_title', ''),
                        'Leadership Contact 3 Email': job.get('leadership_contact_3_email', ''),
                        'Urgency Score': f"{job.get('urgency_score', 0):.2f}"
                    }
                    writer.writerow(row)
            
            logger.info(f"Saved {len(jobs)} leads to {csv_filename}")
            return str(csv_filename)
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            raise
    
    def run(self):
        """Main pipeline execution"""
        logger.info("="*50)
        logger.info("Starting Insurance Leads Pipeline")
        logger.info("="*50)
        
        try:
            # Step 1: Fetch jobs from Apify
            logger.info("Step 1: Fetching job listings from Apify...")
            jobs = self.fetch_jobs_from_apify()
            
            if not jobs:
                logger.warning("No jobs fetched from Apify")
                return
            
            # Step 2: Deduplicate jobs
            logger.info("Step 2: Deduplicating jobs...")
            unique_jobs = self.deduplicate_jobs(jobs)
            
            if not unique_jobs:
                logger.info("No new unique jobs to process")
                return
            
            # Step 3: Process jobs (enrich and score)
            logger.info("Step 3: Processing jobs (enriching with Apollo and scoring)...")
            processed_jobs = self.process_jobs(unique_jobs)
            
            # Step 4: Sort by urgency score and select top leads
            logger.info("Step 4: Selecting top leads by urgency score...")
            sorted_jobs = sorted(processed_jobs, key=lambda x: x.get('urgency_score', 0), reverse=True)
            top_leads = sorted_jobs[:TOP_LEADS_COUNT]
            
            logger.info(f"Selected top {len(top_leads)} leads")
            
            # Step 5: Save to CSV
            logger.info("Step 5: Saving leads to CSV...")
            csv_file = self.save_to_csv(top_leads)
            
            # Step 6: Update collected leads tracking
            for job in top_leads:
                self.collected_leads.add(job.get('lead_id'))
            self.save_collected_leads()
            
            logger.info("="*50)
            logger.info(f"Pipeline completed successfully!")
            logger.info(f"Output file: {csv_file}")
            logger.info(f"Total leads collected to date: {len(self.collected_leads)}")
            logger.info("="*50)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise

def main():
    """Main entry point"""
    try:
        pipeline = LeadsPipeline()
        pipeline.run()
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
