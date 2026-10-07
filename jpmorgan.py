import requests
import utils
from bs4 import BeautifulSoup

def get_job_description(job_id):
    """Fetches the full description from Oracle HCM's detail endpoint."""
    url = "https://jpmc.fa.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails"
    headers = {
        "User-Agent": "Mozilla/5.0", 
        "Accept": "application/json"
    }
    # Notice the %22 which URL-encodes the double quotes around the ID
    params = {
        "expand": "all",
        "onlyData": "true",
        "finder": f'ById;Id="{job_id}",siteNumber=CX_1001'
    }
    
    try:
        r = requests.get(url, params=params, headers=headers, timeout=5)
        # Oracle HCM often hides the description deep in an array
        items = r.json().get("items", [])
        if not items:
            return "Description not available"
            
        job_data = items[0]
        # Check standard Oracle fields for the description
        html_desc = job_data.get("ExternalDescriptionStr") or job_data.get("ShortDescription") or job_data.get("Description", "")
        
        if html_desc:
            soup = BeautifulSoup(html_desc, "html.parser")
            return soup.get_text(separator=" ", strip=True)
    except Exception:
        pass
    return "Description not available"

def scrape(seen_ids):
    url = "https://jpmc.fa.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    target_queries = ["Software Engineer I", "Associate Software Engineer", "Python Engineer", "AI Engineer"]
    jobs = []
    
    for query in target_queries:
        finder_string = f'findReqs;siteNumber=CX_1001,facetsList=LOCATIONS,limit=40,offset=0,keyword="{query}",sortBy=POSTING_DATES_DESC,executeSpellCheckFlag=false'
        params = {"onlyData": "true", "expand": "requisitionList.workLocation", "finder": finder_string}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status() 
            requisitions = response.json().get("items", [{}])[0].get("requisitionList", [])
            
            for job in requisitions:
                job_id = job.get("Id", "")
                title = job.get("Title", "")
                if not job_id or not title or job_id in seen_ids: continue
                
                title_lower = title.lower()
                if not utils.is_valid_title(title_lower): continue
                
                level = utils.parse_level(title_lower)
                if level == 0: continue
                
                location = job.get("PrimaryLocation", "Multiple Locations")
                posted_date = job.get("PostingDate", "Unknown")
                
                # --- NEW: Fetch the description ---
                description_text = get_job_description(job_id)
                
                jobs.append({
                    "Company": "JPMorgan", "ID": job_id, "Title": title, 
                    "Location": location, "Tier": utils.get_location_tier(location), "Level": level,
                    "Posted_Date": posted_date[:10] if posted_date != "Unknown" else "Unknown",
                    "Description": description_text, # Added description
                    "Link": f"https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/{job_id}"
                })
        except Exception as e:
            print(f"[JPMC] Error on '{query}': {e}")
            
    return jobs