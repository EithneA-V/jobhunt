import os
import csv
from datetime import datetime, timedelta
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# 1. EMBEDDED RESUME TRACKS (FOR ATS SCORES)
# ==========================================
RESUMES = {
    "Analyst Focus": """
    Analytical and data-driven professional with a strong foundation in data-intensive research, spreadsheet modeling, and cross functional operations. 
    Proven track record of developing Excel-based relational data tracking matrices, engineering forecasting models, and analyzing metrics to isolate operational bottlenecks. Adept at Navigating complex qualitative and quantitative variables under compressed timelines to support corporate strategy and Risk Management.
    Skills: Resource Management models, Sustainability Metrics, Regulatory COmpliance, Risk Mitigation, Relational Tracking Matrices, Data-Intensive Research, Excel Data Modeling, Performance Metrics, Trend Forecasting, Analysis, Workflow Improvements, Process Optimization, Bottleneck Isolation, Quality Control, Supply Chain Risk Modeling. Java, C++, C, Python, Git, Microsoft Excel, Zotero, Jira, Asana.
    """,
    "Policy Focus": """
     Rigorous Policy and Governance professional with specialized expertise in environmental compliance guidelines, public policy evaluation, and structural risk analysis. Skilled in authoring data-backed policy briefs, auditing complex legal and ethical arguments, and mapping multi-stakeholder regulatory frameworks. Adept at synthesizing interdisciplinary academic literature and institutional data into clear, actionable executive summaries for senior leadership.
    Skills: Policy Brief Authoring, Regulatory Compliance, Public Policy Analysis, Environmental Compliance Guidelines, Institutional Risk Assessment, Global Governance Frameworks, Multi-Stakeholder Models, Legal & Ethical Argument Auditing, Structural Analysis, Resource Management, Data Synthesis, Reference Architecture, Executive Summaries, Publication Standards, Resource Managment Models, Sustainability metrics, Regulatory COmpliance, Risk Mitigation. Microsoft Excel, Zotero, Jira, Asana.
    """,
    "Coordinator Focus": """
     Action-oriented Project Coordinator with a Certificate of Sustainability and extensive experience leading cross-functional operations and multi-stakeholder workflows. 
    Proven ability to execute complex projects under strict timelines, manage daily personnel allocation, and coordinate delivery across multiple internal departments. Expert at tracking project lifecycle metrics, implementing workflow improvements, and optimizing team sprint velocities.
    Skills: Project Lifecycle Management, Multi-stakeholder Governance, Workflow Deployment, Sprint Velocity Optimization, Operational Bottleneck Isolation, Timeline Management, Quality Control, Cross-functional Coordination, Personnel Allocation, Performance Training, Talent Acquisition Collaboration, Stakeholder Communication. Jira, Asana, Git, Microsoft Excel, Zotero.
    """,
    "Customer Success Focus": """
     Action-oriented Customer Success professional with a strong foundation in cross-functional operations management, data automation, and multi-stakeholder workflows. Proven ability to execute complex projects under strict timelines, manage daily personnel allocation, manage delivery dependencies across internal departments, and translate complex technical logic (C, C++, Java, Python) into scalable business solutions. Expert at Customer Success Planning, tracking lifecycle metrics and mitigating risks to drive accelerated value realization and drive AI transformation across high-stakes environments.
     Customer Success & Delivery: Customer Success Planning, Trusted Advisor Relationships, Governance Rhythms, Cross-Functional Orchestration, Customer Advocacy, Value Realization.
     Risk & Project Management: Timeline Management, Mitigation of Delivery Risks, Process Optimization, Asset Allocation, Sprint Velocity Optimization.
     Technical Execution & AI Logic: Object-Oriented Programming (Java, C++, C), Python Data Manipulation, Automated Web Scraping, Structured Reference Architectures, Relational Tracking Matrices.
     Tools & Frameworks: Microsoft Excel, Jira, Asana, Git, Zotero. Methodologies: Familiarity with Agile and Scrum workflows

 """
    
}

# ==========================================
# 2. CONFIGURATION & CRITERIA SETTINGS
# ==========================================
TARGET_ROLES = [
    "business analyst", "analyst", "policy analyst", 
    "project coordinator", "sustainability coordinator", 
    "sustainability analyst", "operations analyst", 
    "environmental initiatives analyst", "sustainability initiatives analyst",
    "environmental initiatives", "sustainability initiatives", "policy coordinator",
    "customer success", "customer success manager", "customer success specialist", 
    "account manager", "client success", "client success manager", "client success specialist", 
    "customer experience", "customer experience manager", "customer experience specialist"
]

# Filepath setup
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "JobHunt")
OUTPUT_CSV = os.path.join(DESKTOP_PATH, "matched_jobs_report.csv")
LOG_FILE = os.path.join(DESKTOP_PATH, "routine_execution.log")

# Create folder if it doesn't exist
os.makedirs(DESKTOP_PATH, exist_ok=True)


# ==========================================
# 3. CORE PROCESSING LOGIC
# ==========================================
def log_message(msg):
	print(msg)
	with open (LOG_FILE, mode="a", encoding="utf-8") as lf:
		lf.write(f"{msg}\n")

def calculate_ats_score(job_description, resume_text):
    """Calculates a match percentage using Cosine Similarity."""
    if not job_description or not resume_text:
        return 0.0

    try:
        documents = [resume_text, job_description]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform(documents)
        similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])
        return round(float(similarity[0][0]) * 100, 1)
    except Exception:
        return 0.0


def fetch_jobs_from_api():
    """
    Fetches live openings. Uses a fallback mock framework if API
    credentials are not yet provided by the user. API creds currently included are Adzuna API endpoint
    """
    # Replace these placeholders with real API credentials if using Adzuna, JSearch, etc.
    API_ID = "a4ae685c"
    API_KEY = "2d2562c59603ed2a391e97b25f49fd48"

    #Query Adzuna's Canadian job index
    
    base_url = "https://api.adzuna.com/v1/api"
    url = f"{base_url}/jobs/ca/search/1"  # Page 1 of results
    search_phrase = "analyst"
    params = {
        "app_id": API_ID,
        "app_key": API_KEY,
        "results_per_page": 50,
        "what": search_phrase,
        "content-type": "application/json",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            jobs = []

            for job in data.get("results", []):
                jobs.append(
                    {
                        "title": job.get("title", ""),
                        "company": job.get("company", {}).get("display_name", "Unknown"),
                        "location": job.get("location", {}).get("display_name", "Canada"),
                        "description": job.get("description", ""),
                        "url": job.get("redirect_url", ""),
                        "date_posted": datetime.strptime(job.get("created", "")[:19], "%Y-%m-%dT%H:%M:%S") if job.get("created") else datetime.now()
                    }
                )
            return jobs
           
        else:
            log_message(f"API Error: Server returned status code {response.status_code}")
            return []
    except Exception as e:
        log_message(f"Network error trying to contact API: {str(e)}")
        return[]

def run_routine():
    """Main process execution window loop."""
    log_message(f"--- Routine Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    raw_jobs = fetch_jobs_from_api()
    print(f"DEBUG: Adzuna returned {len(raw_jobs)} jobs for processing.")
    valid_matches = []
    
    three_days_ago = datetime.now() - timedelta(days=3)

    for job in raw_jobs:
        title_lower = job["title"].lower()
        loc_lower = job["location"].lower()

        # 1. Title Filter Matches
        matches_role = any(role in title_lower for role in TARGET_ROLES) or "analyst" in title_lower or "coordinator" in title_lower or "customer success" in title_lower

        # 2. Geographic Boundaries Filter (Toronto or Remote Canada)
        is_toronto = "toronto" in loc_lower
        is_remote_canada = "remote" in loc_lower and ("canada" in loc_lower or "on" in loc_lower)
        is_broad_region = "ontario" in loc_lower or loc_lower == "on" in loc_lower
        matches_location = is_toronto or is_remote_canada or is_broad_region

        # 3. Temporal Filter (Last 3 Days Only)
        is_recent = job["date_posted"] >= three_days_ago

        if matches_role and matches_location and is_recent:
            # Evaluate against all four resumes
            desc_text = job["description"]
            score_analyst = calculate_ats_score(desc_text, RESUMES["Analyst Focus"])
            score_policy = calculate_ats_score(desc_text, RESUMES["Policy Focus"])
            score_coord = calculate_ats_score(desc_text, RESUMES["Coordinator Focus"])
            score_customer_success = calculate_ats_score(desc_text, RESUMES["Customer Success Focus"])


            valid_matches.append({
                "Date Found": datetime.now().strftime("%Y-%m-%d"),
                #"Date Posted": datetime.date_posted().strftime("%Y-%m-%d")
                "Title": job["title"],
                "Company": job["company"],
                "Location": job["location"],
                "Analyst ATS %": score_analyst,
                "Policy ATS %": score_policy,
                "Coordinator ATS %": score_coord,
                "Customer Success ATS %": score_customer_success,
                "URL": job.get("url", "")
            })

    # Save to Spreadsheet
    if valid_matches:
        file_exists = os.path.isfile(OUTPUT_CSV)
        fieldnames = list(valid_matches[0].keys())

        with open(OUTPUT_CSV, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(valid_matches)

        log_message(f"Success: Found and appended {len(valid_matches)} new job matches.")
    else:
        log_message("Execution finished: No new matching jobs posted within the last 3 days.")


if __name__ == "__main__":
    run_routine()
        
