import requests
import utils

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
                jobs.append({
                    "Company": "JPMorgan", "ID": job_id, "Title": title, 
                    "Location": location, "Tier": utils.get_location_tier(location), "Level": level,
                    "Link": f"https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/{job_id}"
                })
        except Exception as e:
            print(f"[JPMC] Error on '{query}': {e}")
    return jobs