import requests
import utils
from bs4 import BeautifulSoup

def get_job_description(external_path):
    url = f"https://visa.wd5.myworkdayjobs.com/wday/cxs/visa/Visa{external_path}"
    headers = {
        "User-Agent": "Mozilla/5.0", 
        "Accept": "application/json"
    }
    try:
        r = requests.get(url, headers=headers, timeout=5)
        job_data = r.json().get("jobPostingInfo", {})
        html_desc = job_data.get("jobDescription", "")
        if html_desc:
            soup = BeautifulSoup(html_desc, "html.parser")
            return soup.get_text(separator=" ", strip=True)
    except Exception:
        pass
    return "Description not available"

def scrape(seen_ids):
    url = "https://visa.wd5.myworkdayjobs.com/wday/cxs/visa/Visa/jobs"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Content-Type": "application/json"}
    target_queries = ["Software Engineer", "Data Engineer", "AI Engineer", "Backend Developer"]
    jobs = []
    
    for query in target_queries:
        payload = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": query}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            for job in response.json().get("jobPostings", []):
                job_id = job.get("externalPath", "")
                title = job.get("title", "")
                if not job_id or not title or job_id in seen_ids: 
                    continue
                
                title_lower = title.lower()
                if not utils.is_valid_title(title_lower): 
                    continue
                
                level = utils.parse_level(title_lower)
                if level == 0: 
                    continue
                
                location = job.get("locationsText", "Unknown")
                posted_date = str(job.get("postedOn", "Unknown"))
                
                description_text = get_job_description(job_id)
                
                jobs.append({
                    "Company": "Visa", 
                    "ID": job_id, 
                    "Title": title, 
                    "Location": location, 
                    "Tier": utils.get_location_tier(location), 
                    "Level": level,
                    "Posted_Date": posted_date,
                    "Description": description_text,
                    "Link": f"https://visa.wd5.myworkdayjobs.com/en-US/Visa{job_id}"
                })
        except Exception as e:
            print(f"[Visa] Error on '{query}': {e}")
            
    return jobs