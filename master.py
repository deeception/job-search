import json
import csv
import os
from datetime import datetime

# Import the 5 functional modular scrapers
import amazon
import visa
import jpmorgan
import mastercard
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
    
    new_jobs = []
    # Execute the 5 clean scrapers
    new_jobs.extend(amazon.scrape(seen_ids))
    new_jobs.extend(jpmorgan.scrape(seen_ids))
    new_jobs.extend(visa.scrape(seen_ids))
    new_jobs.extend(mastercard.scrape(seen_ids))
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
    new_jobs.sort(key=lambda x: (x.get("Tier", "Tier 4"), x.get("Level", 99)))

    # Generate CSV with new columns
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"job_matches_{timestamp}.csv"
    
    # Added Posted_Date and Description to fieldnames
    fieldnames = ["Company", "Title", "Location", "Tier", "Level", "Posted_Date", "Description", "Link"]
    
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for job in new_jobs:
            writer.writerow({
                "Company": job.get("Company", "Unknown"),
                "Title": job.get("Title", "Unknown"),
                "Location": job.get("Location", "Unknown"),
                "Tier": str(job.get("Tier", "Unknown")),
                "Level": f"SDE {job['Level']}" if job.get('Level') != 1.5 else "Unspecified/Mid",
                "Posted_Date": job.get("Posted_Date", "Unknown"),
                "Description": job.get("Description", "Description not available"),
                "Link": job.get("Link", "")
            })
            seen_ids.add(job["ID"])
            
    save_seen_jobs(seen_ids)
    print(f"Success! {len(new_jobs)} new jobs exported to {csv_filename}")

if __name__ == "__main__":
    run_pipeline()