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
  * **Responsive Design:** Stacked filters and condensed tables for clean smartphone viewing.
  * **System Prompt Injection:** Automatically injects a custom career-strategist prompt into cell A1 of the CSV to command LLMs (like Gemini) upon upload to return the top 3-5 Job IDs/Titles per company.
  * **Native Mobile Sharing:** A custom HTML/JS Base64 payload generator that triggers the native iOS/Android `navigator.share()` API to send the CSV (with descriptions and prompt) directly to WhatsApp, Mail, or Gemini.
  * **Full Analytics Suite:** Multi-tab layout featuring Data Grouping & Analytics, Historical Ingestion Logs, and live Rule Configuration.

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
├── app.py                  # Mobile-optimized Streamlit dashboard (UI, Analytics, Native Share)
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