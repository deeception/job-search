import time
import requests
import utils

def scrape(seen_ids):
    url = "https://apply.careers.microsoft.com/api/pcsx/search"
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*"
    })
    
    target_queries = ["Software Engineer", "Data Engineer", "AI Engineer", "Machine Learning"]
    target_locations = ["India", "United Kingdom", "Ireland"]
    jobs = []
    
    for location in target_locations:
        for query in target_queries:
            params = {
                "domain": "microsoft.com",
                "query": query,
                "location": location,
                "start": 0,
                "filter_include_remote": 1,
                "hl": "en"
            }
            
            for attempt in range(3):
                try:
                    time.sleep(2)  
                    response = session.get(url, params=params, timeout=15)
                    
                    if response.status_code == 429:
                        print(f"[Microsoft] Rate limited on '{query}' in {location}. Sleeping 5s...")
                        time.sleep(5)
                        continue
                        
                    response.raise_for_status()
                    data = response.json()
                    
                    # Eightfold nests their payloads unpredictably. Search multiple possible structures.
                    job_list = data.get("positions") or data.get("data", {}).get("positions") or data.get("data", {}).get("jobs") or data.get("jobs") or []
                    
                    # Hard-fallback: scan the entire JSON tree for an array of job objects
                    if not job_list:
                        for key, val in data.items():
                            if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict) and ("name" in val[0] or "title" in val[0]):
                                job_list = val
                                break

                    for job in job_list:
                        # CRITICAL FIX: Microsoft uses "name" instead of "title"
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
                            "Company": "Microsoft",
                            "ID": job_id,
                            "Title": title,
                            "Location": loc,
                            "Tier": utils.get_location_tier(loc),
                            "Level": level,
                            "Link": f"https://apply.careers.microsoft.com/careers?pid={job_id}"
                        })
                    break  
                except Exception as e:
                    print(f"[Microsoft] Error on '{query}': {e}")
                    break 
                    
    return jobs