import requests
import utils

def scrape(seen_ids):
    url = "https://mastercard.wd1.myworkdayjobs.com/wday/cxs/mastercard/CorporateCareers/jobs"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Content-Type": "application/json"}
    target_queries = ["Software Engineer", "Data Engineer", "AI Engineer", "Machine Learning"]
    jobs = []
    
    for query in target_queries:
        payload = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": query}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            
            job_postings = response.json().get("jobPostings", [])
            for job in job_postings:
                job_id = job.get("externalPath", "")
                title = job.get("title", "")
                
                if not job_id or not title or job_id in seen_ids: continue
                
                title_lower = title.lower()
                if not utils.is_valid_title(title_lower): continue
                
                level = utils.parse_level(title_lower)
                if level == 0: continue
                
                location = job.get("locationsText", "Unknown")
                # Workday jobs return string like "Posted 2 Days Ago"
                posted_date = job.get("postedOn", "Unknown")
                
                jobs.append({
                    "Company": "Mastercard", "ID": job_id, "Title": title, 
                    "Location": location, "Tier": utils.get_location_tier(location), "Level": level,
                    "Posted_Date": posted_date,
                    "Link": f"https://mastercard.wd1.myworkdayjobs.com/en-US/CorporateCareers{job_id}"
                })
        except Exception as e:
            print(f"[Mastercard] Error on '{query}': {e}")
    return jobs