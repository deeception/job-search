import requests
import utils
from bs4 import BeautifulSoup

def scrape(seen_ids):
    url = "https://jobs.careers.microsoft.com/global/api/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://jobs.careers.microsoft.com/global/en/search"
    }
    target_queries = ["Software Engineer", "Data Engineer", "Applied Scientist"]
    jobs = []
    
    for query in target_queries:
        params = {"lc": "India", "q": query, "p": 1}
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            if response.status_code != 200: continue
            
            job_list = response.json().get("operationResult", {}).get("result", {}).get("jobs", [])
            for job in job_list:
                job_id = str(job.get("jobId", ""))
                title = job.get("title", "")
                
                if not job_id or not title or job_id in seen_ids: continue
                
                title_lower = title.lower()
                if not utils.is_valid_title(title_lower): continue
                if utils.parse_level(title_lower) == 0: continue
                
                loc = job.get("properties", {}).get("primaryLocation", "Unknown")
                posted_date = job.get("postingDate", "Unknown")[:10]
                
                raw_desc = job.get("properties", {}).get("description", "")
                description_text = BeautifulSoup(raw_desc, "html.parser").get_text(separator=" ", strip=True) if raw_desc else "Description not available"
                    
                jobs.append({
                    "Company": "Microsoft", "ID": job_id, "Title": title,
                    "Location": loc, "Tier": utils.get_location_tier(loc), "Level": utils.parse_level(title_lower),
                    "Posted_Date": posted_date, "Description": description_text,
                    "Link": f"https://jobs.careers.microsoft.com/global/en/job/{job_id}"
                })
        except Exception as e:
            print(f"[Microsoft] Error on '{query}': {e}")
    return jobs