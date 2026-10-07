import requests
import utils
from bs4 import BeautifulSoup

def scrape(seen_ids):
    # Switched from GraphQL to Walmart's REST job search API
    url = "https://careers.walmart.com/api/jobs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    target_queries = ["Software Engineer", "Data Engineer", "Machine Learning"]
    jobs = []
    
    for query in target_queries:
        params = {
            "page": 1,
            "sort": "relevance",
            "keyword": query,
            "country": "India"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            if response.status_code != 200: continue
            
            for job in response.json().get("jobSearchResult", {}).get("jobSpecs", []):
                job_id = str(job.get("reqId", ""))
                title = job.get("jobTitle", "")
                
                if not job_id or not title or job_id in seen_ids: continue
                
                title_lower = title.lower()
                if not utils.is_valid_title(title_lower): continue
                if utils.parse_level(title_lower) == 0: continue
                
                loc = f"{job.get('city', '')}, {job.get('state', '')}".strip(", ")
                posted_date = job.get("postedDate", "Unknown")[:10]
                
                raw_desc = job.get("jobDescription", "")
                description_text = BeautifulSoup(raw_desc, "html.parser").get_text(separator=" ", strip=True) if raw_desc else "Description not available"
                    
                jobs.append({
                    "Company": "Walmart", "ID": job_id, "Title": title,
                    "Location": loc, "Tier": utils.get_location_tier(loc), "Level": utils.parse_level(title_lower),
                    "Posted_Date": posted_date, "Description": description_text,
                    "Link": f"https://careers.walmart.com/us/jobs/{job_id}"
                })
        except Exception as e:
            print(f"[Walmart] Error on '{query}': {e}")
    return jobs