# Requisition Intelligence Engine 💼

An automated, mobile-optimized Applicant Tracking System (ATS) extraction pipeline and Streamlit dashboard. This system dynamically tracks, filters, and analyzes enterprise engineering roles from major tech and finance firms, outputting structured data including levels, location tiers, posted dates, and full job descriptions.

## 🚀 Current Status: Phase 1 Completed

### ✅ What is Done (Fully Implemented)
* **Production-Ready Extractors (The "Big 5"):**
  * **Amazon** (Direct API)
  * **Goldman Sachs** (Custom GraphQL with 2-step description fetch)
  * **Visa** (Workday ATS with 2-step description fetch)
  * **Mastercard** (Workday ATS with 2-step description fetch)
  * **JPMorgan Chase** (Oracle HCM with 2-step description fetch)
* **Data Enrichment & Cleaning:**
  * Successfully bypassing pagination to retrieve full Job Descriptions (JDs) and ATS Posted Dates.
  * Automated parsing of Career Levels (e.g., SDE 1, SDE 2) and Location Tiers based on custom definitions.
* **State & Persistence Layer:**
  * `seen_jobs_tracker.json`: Prevents re-alerting on jobs that have already been processed.
  * `job_history_ledger.csv`: A chronological database of all historical job ingestions.
  * `config.json`: Dynamic rules engine for managing title inclusions, exclusions, and location tiering.
* **Mobile-Optimized Streamlit UI (`app.py`):**
  * **Tab 1 (Active Opportunities):** Condensed mobile-friendly table, advanced sorting/filtering, and a "Share to Gemini" Markdown payload generator.
  * **Tab 2 (Analytics):** Grouping and charting of historical requisition data.
  * **Tab 3 (History):** Granular, day-by-day ingestion logs.
  * **Tab 4 (Configuration):** Live-updating UI to edit extraction rules without touching the code.

---

## 🛑 What is NOT Done (Blocked / Deferred to Phase 2)

### ❌ Blocked Companies
* **Microsoft** (Eightfold AI)
* **PayPal** (Eightfold AI)
* **Walmart** (GraphQL / Custom)
* **Intuit**

### 🔍 Reason for Deferment
These platforms recently upgraded their Web Application Firewalls (Cloudflare) and ATS security protocols. They now enforce **dynamic CSRF tokens**, TLS fingerprinting, and HTTP/2 multiplexing signatures that instantly block standard Python `requests` calls with `403 Forbidden`, `400 Bad Request`, or `429 Too Many Requests` errors. 

### 🛠️ Future Roadmap (Phase 2)
1. **Headless Browser Integration:** To scrape the blocked companies, the architecture will need to integrate **Selenium** or **Playwright** to spoof legitimate browser sessions and harvest real CSRF tokens.
2. **Containerization:** Deploying Selenium requires a heavier Linux/Docker setup on the host server (Streamlit Cloud deployment will need appropriate `packages.txt` for headless Chrome dependencies).
3. **Auto-Scheduling:** Migrate from manual UI-triggered extraction to automated cron-jobs (e.g., via GitHub Actions) that ping the endpoints daily and update the ledger.

---

## 📂 Project Structure
```text
├── app.py                  # Mobile-optimized Streamlit dashboard
├── master.py               # Backend orchestration and CSV generation script
├── utils.py                # Core logic for leveling, tiering, and config loading
├── config.json             # Modifiable rules engine (Whitelists/Blacklists/Tiers)
├── seen_jobs_tracker.json  # Deduplication state memory
├── job_history_ledger.csv  # Persistent analytics database
├── amazon.py               # Scraper module
├── goldmansachs.py         # Scraper module
├── visa.py                 # Scraper module
├── mastercard.py           # Scraper module
└── jpmorgan.py             # Scraper module