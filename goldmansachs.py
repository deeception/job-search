import requests
import utils
from bs4 import BeautifulSoup

def get_job_description(job_id):
    """Makes a secondary GraphQL call to fetch the full job description."""
    url = "https://api-higher.gs.com/gateway/api/v1/graphql"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://higher.gs.com"
    }
    
    query = """
    query GetRoleById($externalSourceId: String!, $externalSourceFetch: Boolean) {
      role(externalSourceId: $externalSourceId, externalSourceFetch: $externalSourceFetch) {
        descriptionHtml
      }
    }
    """
    
    payload = {
        "operationName": "GetRoleById",
        "variables": {
            "externalSourceId": str(job_id),
            "externalSourceFetch": True
        },
        "query": query
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        data = response.json()
        html_desc = data.get("data", {}).get("role", {}).get("descriptionHtml", "")
        
        if html_desc:
            # Strip HTML tags to return clean text for the CSV
            soup = BeautifulSoup(html_desc, "html.parser")
            return soup.get_text(separator=" ", strip=True)
    except Exception:
        pass
    return "Description not available"

def scrape(seen_ids):
    url = "https://api-higher.gs.com/gateway/api/v1/graphql"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://higher.gs.com",
        "Referer": "https://higher.gs.com/results"
    }

    target_queries = ["software engineer", "data engineer", "machine learning", "ai engineer"]
    jobs = []

    graphql_query = """
    query GetRoles($searchQueryInput: RoleSearchQueryInput!) {
      roleSearch(searchQueryInput: $searchQueryInput) {
        totalCount
        items {
          roleId
          corporateTitle
          jobTitle
          locations {
            primary
            state
            country
            city
          }
          externalSource {
            sourceId
          }
        }
      }
    }
    """

    for query in target_queries:
        payload = {
            "operationName": "GetRoles",
            "variables": {
                "searchQueryInput": {
                    "page": {"pageSize": 50, "pageNumber": 0},
                    "sort": {"sortStrategy": "RELEVANCE", "sortOrder": "DESC"},
                    "filters": [{"filterCategoryType": "LOCATION", "filters": [
                        {"filter": "India", "subFilters": [
                            {"filter": "Karnataka", "subFilters": [{"filter": "Bengaluru", "subFilters": []}]},
                            {"filter": "Telangana", "subFilters": [{"filter": "Hyderabad", "subFilters": []}]}
                        ]}
                    ]}],
                    "experiences": ["EARLY_CAREER", "PROFESSIONAL"],
                    "searchTerm": query
                }
            },
            "query": graphql_query
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            job_list = data.get("data", {}).get("roleSearch", {}).get("items", [])
            
            for job in job_list:
                ext_source = job.get("externalSource") or {}
                raw_id = str(ext_source.get("sourceId") or job.get("roleId") or "")
                job_id = raw_id.split("_")[0].strip()
                
                if not job_id or len(job_id) > 10 or "-" in job_id: continue
                if job_id in seen_ids: continue
                
                title = job.get("jobTitle", "")
                if not title: continue

                title_lower = title.lower()
                if not utils.is_valid_title(title_lower): continue
                    
                level = utils.parse_level(title_lower)
                if level == 0: continue
                
                loc_list = job.get("locations", [])
                if loc_list:
                    primary_loc = loc_list[0]
                    city = primary_loc.get("city", "")
                    country = primary_loc.get("country", "")
                    loc = f"{city}, {country}".strip(", ")
                else:
                    loc = "India"
                
                # --- NEW: Fetch the description ---
                description_text = get_job_description(job_id)
                
                jobs.append({
                    "Company": "Goldman Sachs",
                    "ID": job_id,
                    "Title": title,
                    "Location": loc,
                    "Tier": utils.get_location_tier(loc),
                    "Level": level,
                    "Posted_Date": "Unknown",
                    "Description": description_text, # Added to dictionary
                    "Link": f"https://higher.gs.com/roles/{job_id}"
                })
        except Exception as e:
            print(f"[GoldmanSachs] Error on '{query}': {e}")

    return jobs