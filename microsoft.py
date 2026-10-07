import time
import requests
import utils

def scrape(seen_ids):
    url = "https://apply.careers.microsoft.com/api/pcsx/search"
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "Accept": "application/json, text/plain, */*"})
    
    target_queries = ["Software Engineer", "Data Engineer", "AI Engineer", "Machine Learning"]
    target_locations = ["India", "United Kingdom", "Ireland"]
    jobs = []
    
    for location in target_locations:
        for query in target_queries:
            params = {"domain": "microsoft.com", "query": query, "location": location, "start": 0, "filter_include_remote": 1, "hl": "en"}
            for attempt in range(3):
                try:
                    time.sleep(2)  
                    response = session.get(url, params=params, timeout=15)
                    
                    if response.status_code == 429:
                        time.sleep(5)
                        continue
                        
                    response.raise_for_status()
                    data = response.json()
                    
                    job_list = data.get("positions") or data.get("data", {}).get("positions") or data.get("data", {}).get("jobs") or data.get("jobs") or []
                    
                    if not job_list:
                        for key, val in data.items():
                            if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict) and ("name" in val[0] or "title" in val[0]):
                                job_list = val
                                break

                    for job in job_list:
                        job_id = str(job.get("position_id") or job.get("id", ""))
                        title = job.get("name") or job.get("title", "")
                        
                        if not job_id or not title or job_id in seen_ids: continue
                            
                        title_lower = title.lower()
                        if not utils.is_valid_title(title_lower): continue
                            
                        level = utils.parse_level(title_lower)
                        if level == 0: continue
                            
                        loc = job.get("location", location)
                        # Eightfold exposes posting timestamp
                        posted_date = job.get("posted_date") or job.get("creation_date", "Unknown")
                        
                        jobs.append({
                            "Company": "Microsoft", "ID": job_id, "Title": title,
                            "Location": loc, "Tier": utils.get_location_tier(loc), "Level": level,
                            "Posted_Date": str(posted_date)[:10] if str(posted_date) != "Unknown" else "Unknown",
                            "Link": f"https://apply.careers.microsoft.com/careers?pid={job_id}"
                        })
                    break  
                except Exception as e:
                    break 
    return jobs