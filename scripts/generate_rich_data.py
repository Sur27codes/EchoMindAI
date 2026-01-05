"""
Script to generate rich synthetic data for EchoMindAI.
"""
import csv
import random
from pathlib import Path
import os

# Configuration
DATA_DIR = Path("data/docs")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def generate_financials():
    """Generates a complex CSV file with proper numerical data."""
    filepath = DATA_DIR / "financial_results_2024.csv"
    
    headers = ["Month", "Region", "Revenue", "Expenses", "Units_Sold", "Customer_Satisfaction_Score"]
    regions = ["North America", "Europe", "Asia Pacific", "Latin America"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    rows = []
    base_revenue = 50000
    
    for i, month in enumerate(months):
        # Trend: Growth over the year
        growth_factor = 1.0 + (i * 0.05) 
        
        for region in regions:
            # Regional variances
            if region == "North America":
                mult = 1.5
            elif region == "Asia Pacific":
                mult = 1.2
            else:
                mult = 0.9
                
            rev = int(base_revenue * growth_factor * mult * random.uniform(0.9, 1.1))
            exp = int(rev * random.uniform(0.6, 0.8)) # Profit margin 20-40%
            units = int(rev / random.uniform(45, 55))
            csat = round(random.uniform(3.8, 4.9), 1)
            
            rows.append([month, region, rev, exp, units, csat])
            
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Generated {filepath}")

def generate_handbook():
    """Generates a detailed text document."""
    filepath = DATA_DIR / "employee_handbook_v3.txt"
    content = """
    GLOBAL ENTERPRISE EMPLOYEE HANDBOOK V3.0
    Effective Date: January 1, 2025

    SECTION 1: WORK CULTURE
    Our mission is to Accelerate Humanity. We value:
    1. Radical Sincerity
    2. Velocity over Accuracy (sometimes)
    3. Customer Obsession

    SECTION 2: REMOTE WORK POLICY
    Employees heavily encouraged to work from wherever they are most productive.
    - Tier 1 Locations: Home, Office, Coffee Shop.
    - Tier 2 Locations: Beach (requires manager approval if video calls are scheduled).
    - Hours: Core hours are 10:00 AM to 2:00 PM EST. The rest is flexible.

    SECTION 3: BENEFITS
    - Unlimited PTO: We trust you. Just don't abuse it.
    - Learning Budget: $5,000 per year for courses, books, or conferences.
    - Wellness: $200 monthly stipend for gym, yoga, or meditation apps.

    SECTION 4: SECURITY
    - Passwords must be 16 characters long.
    - Two-Factor Authentication (2FA) is mandatory for all internal systems.
    - Data Classification: 
        * PUBLIC: Website content.
        * INTERNAL: Most documents.
        * CONFIDENTIAL: Salary data, Project Omega specs.
    """
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Generated {filepath}")

def generate_tech_specs():
    """Generates a markdown technical spec."""
    filepath = DATA_DIR / "project_omega_specs.md"
    content = """
    # Project Omega: Technical Specifications

    ## Overview
    Project Omega is a next-generation **Quantum Parsing Engine** designed to decode encrypted subspace signals.

    ## Architecture
    - **Frontend**: Neural Interface (Brain-Computer Link)
    - **Backend**: Rust + Assembly
    - **Database**: Hyper-Graph DB (Neo4j on steroids)

    ## Key Performance Indicators
    | Metric | Target | Current |
    | :--- | :--- | :--- |
    | Latency | < 1ms | 12ms |
    | Throughput | 10PB/s | 5PB/s |
    | Error Rate | 0.0001% | 0.05% |

    ## Deployment Protocol
    1. Initiate `safety_lock.sh`
    2. Spool up the centrifuge.
    3. Deploy container `omega-core:latest`
    4. Monitor thermal output.

    ## Known Issues
    - The engine overheats if processing > 5 Petabytes of non-Euclidean data.
    - UI occasionally flickers in the ultraviolet spectrum.
    """
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Generated {filepath}")

if __name__ == "__main__":
    generate_financials()
    generate_handbook()
    generate_tech_specs()
