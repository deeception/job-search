import time
import requests
import utils

def scrape(seen_ids):
    url = "https://paypal.eightfold.ai/api/pcsx/search"
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://paypal.eightfold.ai",
        "Referer": "https://paypal.eightfold.ai/careers"
    })
    
    target_queries = ["software engineer", "data engineer", "machine learning", "ai engineer"]
    # Your trace specifically queried for 'india' location
    target_locations = ["india"] 
    jobs = []
    
    for location in target_locations:
        for query in target_queries:
            params = {
                "domain": "paypal.com",
                "query": query,
                "location": location,
                "start": 0,
                "sort_by": "timestamp"  # Fetch newest roles first
            }
            
            # Using the same retry logic that solved the Microsoft rate-limiting
            for attempt in range(3):
                try:
                    time.sleep(2)  
                    response = session.get(url, params=params, timeout=15)
                    
                    if response.status_code == 429:
                        print(f"[PayPal] Rate limited on '{query}'. Sleeping 5s...")
                        time.sleep(5)
                        continue
                        
                    response.raise_for_status()
                    data = response.json()
                    
                    job_list = data.get("positions", []) or data.get("data", {}).get("positions", []) or data.get("jobs", [])
                    
                    if not job_list:
                        for val in data.values():
                            if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict) and ("name" in val[0] or "title" in val[0]):
                                job_list = val
                                break

                    for job in job_list:
                        job_id = str(job.get("position_id") or job.get("id", ""))
                        title = job.get("name") or job.get("title", "")
                        
                        if not job_id or not title or job_id in seen_ids:
                            continue
                            
                        title_lower = title.lower()
                        if not utils.is_valid_title(title_lower):
                            continue
                            
                        level = utils.parse_level(title_lower)
                        if level == 0:
                            continue
                            
                        loc = job.get("location", location)
                        jobs.append({
                            "Company": "PayPal",
                            "ID": job_id,
                            "Title": title,
                            "Location": loc,
                            "Tier": utils.get_location_tier(loc),
                            "Level": level,
                            # Use Eightfold URL routing
                            "Link": f"https://paypal.eightfold.ai/careers?pid={job_id}"
                        })
                    break  
                except Exception as e:
                    print(f"[PayPal] Error on '{query}': {e}")
                    break 
                    
    return jobs