import requests
import utils
from bs4 import BeautifulSoup
import urllib.parse

def scrape(seen_ids):
    jobs = []
    target_queries = ["software engineer", "data engineer", "machine learning", "ai engineer"]
    
    # We define India here because TalentBrew requires the location to be URL encoded in the request
    location = "India"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
        "Accept": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest"
    }

    for query in target_queries:
        # Properly URL encode the search parameters to match the raw fetch trace
        encoded_query = urllib.parse.quote_plus(query)
        encoded_loc = urllib.parse.quote_plus(location)
        
        url = (
            f"https://jobs.intuit.com/search-jobs/results?ActiveFacetID=0&CurrentPage=1"
            f"&RecordsPerPage=50&Distance=50&RadiusUnitType=0"
            f"&Keywords={encoded_query}&Location={encoded_loc}"
            f"&ShowRadius=False&IsPagination=False&SortCriteria=0&SortDirection=0&SearchType=1"
        )

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # TalentBrew returns the jobs as a single chunk of pre-rendered HTML inside the "results" key
            html_content = data.get("results", "")
            if not html_content:
                continue
                
            # Parse the HTML to extract the job details
            soup = BeautifulSoup(html_content, "html.parser")
            job_items = soup.find_all("li")
            
            for item in job_items:
                link_tag = item.find("a")
                if not link_tag:
                    continue
                
                # Extract the partial link and title
                partial_link = link_tag.get("href", "")
                title = link_tag.find("h2")
                title = title.text.strip() if title else ""
                
                # Extract the location from the <span> tag
                loc_tag = link_tag.find("span", class_="job-location")
                loc_text = loc_tag.text.strip() if loc_tag else location
                
                # TalentBrew encodes the job ID into the URL path (e.g., /job/location/title/JOB_ID)
                job_id = partial_link.split("/")[-1] if "/" in partial_link else title
                
                if not job_id or not title or job_id in seen_ids:
                    continue
                    
                title_lower = title.lower()
                if not utils.is_valid_title(title_lower):
                    continue
                    
                level = utils.parse_level(title_lower)
                if level == 0:
                    continue
                
                full_link = f"https://jobs.intuit.com{partial_link}"
                
                jobs.append({
                    "Company": "Intuit",
                    "ID": job_id,
                    "Title": title,
                    "Location": loc_text,
                    "Tier": utils.get_location_tier(loc_text),
                    "Level": level,
                    "Link": full_link
                })
        except Exception as e:
            print(f"[Intuit] Error on '{query}': {e}")
            
    return jobs