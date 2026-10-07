import json
import csv
import os
from datetime import datetime

# Import modular scrapers
import amazon
import visa
import jpmorgan
import mastercard
import microsoft
import paypal
import intuit
import goldmansachs
TRACKER_FILE = "seen_jobs_tracker.json"

def get_seen_jobs():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f: 
            return set(json.load(f))
    return set()

def save_seen_jobs(seen_set):
    with open(TRACKER_FILE, "w") as f: 
        json.dump(list(seen_set), f)

def run_pipeline():
    print("Loading tracker and scraping corporate portals...")
    seen_ids = get_seen_jobs()
    
    # Run all scrapers modularly
    new_jobs = []
    new_jobs.extend(amazon.scrape(seen_ids))
    new_jobs.extend(jpmorgan.scrape(seen_ids))
    new_jobs.extend(visa.scrape(seen_ids))
    new_jobs.extend(mastercard.scrape(seen_ids))
    new_jobs.extend(microsoft.scrape(seen_ids))
    new_jobs.extend(paypal.scrape(seen_ids))
    new_jobs.extend(intuit.scrape(seen_ids))
    new_jobs.extend(goldmansachs.scrape(seen_ids))
    
    if not new_jobs:
        print("No new jobs found matching your criteria.")
        return

    # Deduplicate within the current run
    unique_jobs = {}
    for job in new_jobs:
        unique_jobs[job["ID"]] = job
    new_jobs = list(unique_jobs.values())

    # Sort priority: Location Tier (1 is best) -> Level (1 is best, ascending)
    new_jobs.sort(key=lambda x: (x["Tier"], x["Level"]))

    # Generate CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"job_matches_{timestamp}.csv"
    
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Company", "Title", "Location", "Tier", "Level", "Link"])
        writer.writeheader()
        for job in new_jobs:
            writer.writerow({
                "Company": job["Company"],
                "Title": job["Title"],
                "Location": job["Location"],
                "Tier": f"Tier {job['Tier']}",
                "Level": f"SDE {job['Level']}" if job['Level'] != 1.5 else "Unspecified/Mid",
                "Link": job["Link"]
            })
            seen_ids.add(job["ID"])
            
    save_seen_jobs(seen_ids)
    print(f"Success! {len(new_jobs)} new jobs exported to {csv_filename}")

if __name__ == "__main__":
    run_pipeline()