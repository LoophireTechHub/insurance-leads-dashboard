#!/usr/bin/env python3
"""
Enhanced Insurance Leads Pipeline - Multi-Signal Detection
Tracks: Job Postings, Headcount Growth, News, Funding, Leadership Changes
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
from typing import List, Dict, Optional
from pathlib import Path
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("leads_pipeline_enhanced.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Try to import JobSpy
try:
    from jobspy import scrape_jobs
    import pandas as pd
    JOBSPY_AVAILABLE = True
except ImportError:
    JOBSPY_AVAILABLE = False
    logger.warning("JobSpy not available - job posting signals will be limited")

APOLLO_BASE_URL = "https://api.apollo.io/v1"

# Target insurance company criteria
TARGET_CRITERIA = {
    'industries': ['Insurance', 'Insurance Agencies and Brokerages', 'Commercial Insurance'],
    'employee_ranges': ["1,10", "10,20", "20,50", "51,100", "101,200", "201,500", "501,1000"],  # 1-1000 employees
    'job_titles': ["CEO", "CFO", "President", "VP", "Director", "Manager", "Owner", "Partner"],
}

class EnhancedLeadsPipeline:
    def __init__(self):
        self.apollo_token = os.environ.get('APOLLO_API_TOKEN')

        if not self.apollo_token:
            raise ValueError("APOLLO_API_TOKEN not set")

        self.output_dir = Path("leads_output")
        self.output_dir.mkdir(exist_ok=True)

        # Historical tracking for headcount growth
        self.history_file = Path("company_history.json")
        self.company_history = self.load_company_history()

        logger.info("Enhanced Pipeline initialized successfully")

    def load_company_history(self) -> Dict:
        """Load historical company data for growth tracking"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_company_history(self):
        """Save company history for tracking"""
        with open(self.history_file, 'w') as f:
            json.dump(self.company_history, f, indent=2)

    def search_insurance_companies(self, limit: int = 500) -> List[Dict]:
        """Search for insurance companies via Apollo with pagination"""
        logger.info(f"🔍 Searching for insurance companies via Apollo...")

        companies = []
        headers = {"X-Api-Key": self.apollo_token, "Content-Type": "application/json"}

        # Paginate through results for each industry
        for industry in TARGET_CRITERIA['industries']:
            industry_companies = []
            page = 1
            max_pages = 5  # Get 5 pages = 500 companies per industry

            while page <= max_pages and len(industry_companies) < 200:
                try:
                    search_data = {
                        "q_organization_keyword_tags": [industry],
                        "organization_num_employees_ranges": TARGET_CRITERIA['employee_ranges'],
                        "organization_locations": ["United States"],
                        "page": page,
                        "per_page": 100
                    }

                    response = requests.post(
                        f"{APOLLO_BASE_URL}/organizations/search",
                        headers=headers,
                        json=search_data,
                        timeout=15
                    )

                    if response.status_code == 200:
                        data = response.json()
                        orgs = data.get('organizations', [])
                        if not orgs:
                            break  # No more results
                        industry_companies.extend(orgs)
                        logger.info(f"  ✓ Page {page}: Found {len(orgs)} companies in {industry}")
                        page += 1
                    else:
                        logger.warning(f"  ✗ Apollo search failed: {response.status_code}")
                        break

                    time.sleep(1)  # Rate limiting

                except Exception as e:
                    logger.error(f"Error searching {industry} page {page}: {e}")
                    break

            companies.extend(industry_companies)
            logger.info(f"  📊 Total for {industry}: {len(industry_companies)} companies")

        # Deduplicate by company ID
        seen_ids = set()
        unique_companies = []
        for company in companies:
            company_id = company.get('id')
            if company_id and company_id not in seen_ids:
                seen_ids.add(company_id)
                unique_companies.append(company)

        logger.info(f"✅ Total unique companies found: {len(unique_companies)}")
        return unique_companies[:limit]

    def detect_headcount_growth(self, company: Dict) -> Dict:
        """Detect if company is growing based on headcount"""
        company_id = company.get('id')
        company_name = company.get('name', 'Unknown')
        current_headcount = company.get('estimated_num_employees', 0)

        growth_signal = {
            'is_growing': False,
            'growth_rate': 0.0,
            'previous_headcount': current_headcount,
            'current_headcount': current_headcount,
            'days_tracked': 0
        }

        # Check historical data
        if company_id in self.company_history:
            history = self.company_history[company_id]
            previous_headcount = history.get('headcount', current_headcount)
            last_check = history.get('last_check', datetime.now().isoformat())

            try:
                last_check_date = datetime.fromisoformat(last_check)
                days_tracked = (datetime.now() - last_check_date).days

                if days_tracked >= 7 and previous_headcount > 0:
                    # Calculate growth rate
                    headcount_change = current_headcount - previous_headcount
                    growth_rate = (headcount_change / previous_headcount) * 100

                    growth_signal['previous_headcount'] = previous_headcount
                    growth_signal['growth_rate'] = round(growth_rate, 2)
                    growth_signal['days_tracked'] = days_tracked
                    growth_signal['is_growing'] = growth_rate >= 10  # 10%+ growth

                    if growth_rate >= 10:
                        logger.info(f"  🚀 GROWTH SIGNAL: {company_name} +{growth_rate}% ({previous_headcount} → {current_headcount})")
            except:
                pass

        # Update history
        self.company_history[company_id] = {
            'name': company_name,
            'headcount': current_headcount,
            'last_check': datetime.now().isoformat()
        }

        return growth_signal

    def search_company_jobs(self, company_name: str) -> Dict:
        """Search for active job postings from a company - returns count and job details"""
        if not JOBSPY_AVAILABLE:
            return {'count': 0, 'jobs': []}

        try:
            jobs_df = scrape_jobs(
                site_name=["indeed", "linkedin"],
                search_term=f'"{company_name}" insurance',  # Broader search
                location="United States",
                results_wanted=30,  # Increased from 20
                hours_old=720,  # 30 days
                country_indeed='USA',
                linkedin_fetch_description=False
            )

            if jobs_df is not None and not jobs_df.empty:
                # Filter for actual company matches
                company_lower = company_name.lower()
                matching_jobs = jobs_df[
                    jobs_df['company'].str.lower().str.contains(company_lower, na=False, regex=False)
                ]

                # EXCLUDE these roles completely
                exclude_keywords = [
                    # Entry level
                    'entry level', 'entry-level', 'junior', 'intern', 'trainee',
                    # Customer service / claims
                    'customer service', 'call center', 'claims adjuster', 'claims representative',
                    'claims processor', 'claims examiner',
                    # Generic sales without insurance context
                    'salesperson', 'sales rep',
                    # Remote indicators in title
                    'remote', 'work from home', 'work-from-home', 'wfh'
                ]

                # INCLUDE these insurance-specific roles
                include_keywords = [
                    # Sales & Production
                    'producer', 'account manager', 'account executive', 'account specialist',
                    'commercial lines', 'personal lines', 'broker', 'agent',
                    # Risk & Underwriting
                    'underwriter', 'risk advisor', 'risk consultant', 'risk manager',
                    # Operations & Management
                    'operations manager', 'operations director', 'operations specialist',
                    'marketing manager', 'marketing director', 'marketing coordinator',
                    'business development', 'client services',
                    # Finance & Admin
                    'accountant', 'accounting manager', 'finance manager', 'controller',
                    # Leadership
                    'director', 'vp', 'vice president', 'ceo', 'cfo', 'coo',
                    'president', 'executive', 'manager', 'supervisor',
                    # Technical
                    'insurance analyst', 'insurance specialist', 'insurance coordinator'
                ]

                filtered_jobs = []
                for _, job in matching_jobs.iterrows():
                    title = str(job.get('title', '') or '').lower()
                    location = str(job.get('location', '') or '').lower()
                    description = str(job.get('description', '') or '').lower()

                    # SKIP if title contains any exclude keywords
                    if any(keyword in title for keyword in exclude_keywords):
                        continue

                    # SKIP if location indicates remote-only (no hybrid/onsite mention)
                    remote_indicators = ['remote', 'work from home', 'wfh', 'telecommute']
                    onsite_indicators = ['hybrid', 'onsite', 'on-site', 'on site', 'in-office', 'office']

                    has_remote = any(indicator in location for indicator in remote_indicators)
                    has_onsite = any(indicator in location for indicator in onsite_indicators)

                    # If remote without onsite/hybrid, skip
                    if has_remote and not has_onsite:
                        continue

                    # ONLY include if title matches insurance roles
                    if any(keyword in title for keyword in include_keywords):
                        filtered_jobs.append(job)

                # Extract job details from filtered jobs
                job_list = []
                for job in filtered_jobs:
                    job_list.append({
                        'title': str(job.get('title', '') or ''),
                        'location': str(job.get('location', '') or ''),
                        'url': str(job.get('job_url', '') or ''),
                        'date_posted': str(job.get('date_posted', '') or ''),
                        'source': str(job.get('site', '') or '')
                    })

                return {'count': len(job_list), 'jobs': job_list}
        except Exception as e:
            logger.debug(f"Job search error for {company_name}: {e}")

        return {'count': 0, 'jobs': []}

    def search_company_news(self, company_name: str, domain: str) -> Dict:
        """Search for recent company news (funding, expansion, etc.)"""
        # This is a placeholder - you can integrate with:
        # - Google News API
        # - NewsAPI.org
        # - Crunchbase API for funding data

        news_signal = {
            'has_news': False,
            'news_type': None,
            'news_date': None,
            'news_summary': None
        }

        # TODO: Implement news API integration
        # For now, return placeholder

        return news_signal

    def get_leadership_contacts(self, company_id: str, company_name: str) -> List[Dict]:
        """Get leadership contacts from company"""
        try:
            headers = {"X-Api-Key": self.apollo_token, "Content-Type": "application/json"}
            search_data = {
                "organization_ids": [company_id],
                "person_titles": TARGET_CRITERIA['job_titles'],
                "page": 1,
                "per_page": 5
            }

            response = requests.post(
                f"{APOLLO_BASE_URL}/mixed_people/search",
                headers=headers,
                json=search_data,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                people = data.get('people', [])
                return people[:5]
        except Exception as e:
            logger.debug(f"Error getting contacts for {company_name}: {e}")

        return []

    def calculate_composite_score(self, signals: Dict) -> float:
        """Calculate composite lead score from multiple signals"""
        score = 0.0

        # Job posting velocity (30%)
        job_count = signals.get('active_jobs', 0)
        if job_count >= 5:
            score += 30
        elif job_count >= 3:
            score += 20
        elif job_count >= 1:
            score += 10

        # Headcount growth (25%)
        growth = signals.get('headcount_growth', {})
        if growth.get('is_growing'):
            growth_rate = growth.get('growth_rate', 0)
            if growth_rate >= 30:
                score += 25
            elif growth_rate >= 20:
                score += 20
            elif growth_rate >= 10:
                score += 15

        # News/Funding (20%)
        if signals.get('news', {}).get('has_news'):
            score += 20

        # Has contacts available (15%)
        if signals.get('contact_count', 0) > 0:
            score += 15

        # Company size fit (10%)
        headcount = signals.get('current_headcount', 0)
        if 20 <= headcount <= 200:
            score += 10
        elif 10 <= headcount <= 500:
            score += 5

        return min(score, 100.0)

    def is_insurance_company(self, company: Dict) -> bool:
        """Filter to ensure company is actually in insurance industry"""
        industry = (company.get('industry', '') or '').lower()
        company_name = (company.get('name', '') or '').lower()

        # Exclude non-insurance industries
        excluded_industries = [
            'staffing', 'recruiting', 'information technology', 'it services',
            'publishing', 'human resources', 'consulting', 'outsourcing',
            'offshoring', 'higher education', 'mental health', 'nonprofit',
            'financial services', 'government'
        ]

        # Check if industry matches excluded list
        for excluded in excluded_industries:
            if excluded in industry:
                return False

        # Whitelist insurance-related keywords
        insurance_keywords = ['insurance', 'underwriting', 'broker', 'risk management']

        # Check if company name or industry contains insurance keywords
        has_insurance_keyword = any(keyword in industry or keyword in company_name
                                   for keyword in insurance_keywords)

        return has_insurance_keyword

    def process_companies(self, companies: List[Dict]) -> List[Dict]:
        """Process companies and gather all signals"""
        logger.info("📊 Processing companies and gathering signals...")

        enriched_leads = []
        filtered_count = 0

        for i, company in enumerate(companies, 1):
            print(f"Processing {i}/{len(companies)}: {company.get('name', 'Unknown')}", end="\r")

            try:
                # Filter out non-insurance companies
                if not self.is_insurance_company(company):
                    filtered_count += 1
                    continue

                # No headcount filtering - accept all sizes
                current_headcount = company.get('estimated_num_employees', 0)

                company_id = company.get('id')
                company_name = company.get('name', '')
                domain = company.get('primary_domain', '')

                # Gather all signals
                signals = {
                    'company_id': company_id,
                    'company_name': company_name,
                    'website': company.get('website_url', ''),
                    'phone': company.get('phone', ''),
                    'location': f"{company.get('city', '')}, {company.get('state', '')}",
                    'current_headcount': company.get('estimated_num_employees', 0),
                    'industry': company.get('industry', ''),
                }

                # Signal 1: Headcount Growth
                growth_signal = self.detect_headcount_growth(company)
                signals['headcount_growth'] = growth_signal

                # Signal 2: Active Job Postings
                if JOBSPY_AVAILABLE:
                    job_data = self.search_company_jobs(company_name)
                    signals['active_jobs'] = job_data['count']
                    signals['job_details'] = job_data['jobs']
                else:
                    signals['active_jobs'] = 0
                    signals['job_details'] = []

                # Signal 3: News/Funding
                news_signal = self.search_company_news(company_name, domain)
                signals['news'] = news_signal

                # Signal 4: Get Leadership Contacts
                contacts = self.get_leadership_contacts(company_id, company_name)
                signals['contact_count'] = len(contacts)
                signals['contacts'] = contacts[:3]  # Top 3

                # Calculate composite score
                signals['composite_score'] = self.calculate_composite_score(signals)

                # Only include leads with active job postings (remove growth requirement)
                if signals['active_jobs'] > 0:
                    enriched_leads.append(signals)

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                logger.error(f"Error processing {company.get('name')}: {e}")

        print()  # New line after progress
        logger.info(f"✅ Processed {len(companies)} companies")
        logger.info(f"   - Filtered out {filtered_count} non-insurance companies")
        logger.info(f"   - {len(enriched_leads)} insurance companies qualified as leads")

        return enriched_leads

    def save_to_csv(self, leads: List[Dict]) -> str:
        """Save enriched leads to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.output_dir / f"enhanced_leads_{timestamp}.csv"

        fieldnames = [
            'Composite Score', 'Company Name', 'Location', 'Website', 'Phone',
            'Current Headcount', 'Growth Rate %', 'Previous Headcount', 'Days Tracked',
            'Active Jobs', 'Industry',
            'Contact 1 Name', 'Contact 1 Title', 'Contact 1 Email', 'Contact 1 Phone', 'Contact 1 LinkedIn',
            'Contact 2 Name', 'Contact 2 Title', 'Contact 2 Email', 'Contact 2 Phone', 'Contact 2 LinkedIn',
            'Contact 3 Name', 'Contact 3 Title', 'Contact 3 Email', 'Contact 3 Phone', 'Contact 3 LinkedIn',
        ]

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for lead in leads:
                contacts = lead.get('contacts', [])
                growth = lead.get('headcount_growth', {})

                row = {
                    'Composite Score': f"{lead.get('composite_score', 0):.1f}",
                    'Company Name': lead.get('company_name', ''),
                    'Location': lead.get('location', ''),
                    'Website': lead.get('website', ''),
                    'Phone': lead.get('phone', ''),
                    'Current Headcount': lead.get('current_headcount', 0),
                    'Growth Rate %': growth.get('growth_rate', 0),
                    'Previous Headcount': growth.get('previous_headcount', 0),
                    'Days Tracked': growth.get('days_tracked', 0),
                    'Active Jobs': lead.get('active_jobs', 0),
                    'Industry': lead.get('industry', ''),
                }

                # Add contacts
                for i, contact in enumerate(contacts[:3], 1):
                    row[f'Contact {i} Name'] = contact.get('name', '')
                    row[f'Contact {i} Title'] = contact.get('title', '')
                    row[f'Contact {i} Email'] = contact.get('email', '')
                    row[f'Contact {i} Phone'] = contact.get('phone_numbers', [{}])[0].get('sanitized_number', '') if contact.get('phone_numbers') else ''
                    row[f'Contact {i} LinkedIn'] = contact.get('linkedin_url', '')

                # Fill empty contact fields
                for i in range(len(contacts) + 1, 4):
                    row[f'Contact {i} Name'] = ''
                    row[f'Contact {i} Title'] = ''
                    row[f'Contact {i} Email'] = ''
                    row[f'Contact {i} Phone'] = ''
                    row[f'Contact {i} LinkedIn'] = ''

                writer.writerow(row)

        logger.info(f"📁 Saved to: {csv_file}")

        # Also save job details to JSON for dashboard
        json_file = self.output_dir / f"enhanced_leads_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=2)
        logger.info(f"📁 Job details saved to: {json_file}")

        return str(csv_file)

    def run(self):
        """Main execution"""
        logger.info("="*60)
        logger.info("Enhanced Insurance Leads Pipeline - Multi-Signal Detection")
        logger.info("="*60)

        # Step 1: Search for insurance companies
        companies = self.search_insurance_companies(limit=200)

        if not companies:
            logger.warning("No companies found")
            return

        # Step 2: Process and enrich with signals
        enriched_leads = self.process_companies(companies)

        # Step 3: Sort by composite score
        enriched_leads.sort(key=lambda x: x.get('composite_score', 0), reverse=True)

        # Step 4: Save results
        csv_file = self.save_to_csv(enriched_leads)

        # Step 5: Save history for growth tracking
        self.save_company_history()

        # Summary
        logger.info("="*60)
        logger.info("📊 SUMMARY")
        logger.info("="*60)
        logger.info(f"Companies searched: {len(companies)}")
        logger.info(f"Qualified leads: {len(enriched_leads)}")

        high_score = len([l for l in enriched_leads if l.get('composite_score', 0) >= 50])
        growing = len([l for l in enriched_leads if l.get('headcount_growth', {}).get('is_growing')])
        hiring = len([l for l in enriched_leads if l.get('active_jobs', 0) > 0])

        logger.info(f"  - High score (50+): {high_score}")
        logger.info(f"  - Growing companies: {growing}")
        logger.info(f"  - Actively hiring: {hiring}")
        logger.info(f"📁 Output: {csv_file}")
        logger.info("="*60)

if __name__ == "__main__":
    try:
        pipeline = EnhancedLeadsPipeline()
        pipeline.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
