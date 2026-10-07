import requests
import utils

def scrape(seen_ids):
    url = "https://amazon.jobs/api/jobs/search?is_als=true"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Content-Type": "application/json"}
    target_queries = ["Software Development Engineer I", "SDE 1", "AI Engineer", "Data Engineer"]
    jobs = []
    
    for query in target_queries:
        payload = {
            "accessLevel": "EXTERNAL", "query": query, "size": 40, "start": 0,
            "sort": {"sortOrder": "DESCENDING", "sortType": "SCORE"},
            "filterFacets": [{"name": "category", "requestedFacetCount": 9999, "values": [{"name": "Software Development"}]}]
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status() 
            for hit in response.json().get("searchHits", []):
                fields = hit.get("fields", {})
                if not fields: continue
                    
                job_id = fields.get("icimsJobId", [""])[0]
                title = fields.get("title", [""])[0]
                if not job_id or not title or job_id in seen_ids: continue
                
                title_lower = title.lower()
                if not utils.is_valid_title(title_lower): continue
                
                level = utils.parse_level(title_lower)
                if level == 0: continue
                
                location = fields.get("location", [""])[0]
                # Amazon jobs return posting date as "createdDate" (e.g. "October 14, 2026")
                posted_date = fields.get("createdDate", ["Unknown"])[0]
                
                jobs.append({
                    "Company": "Amazon", "ID": job_id, "Title": title, 
                    "Location": location, "Tier": utils.get_location_tier(location), "Level": level,
                    "Posted_Date": posted_date,
                    "Link": f"https://amazon.jobs/en/jobs/{job_id}"
                })
        except Exception as e:
            print(f"[Amazon] Error on '{query}': {e}")
    return jobs