import json
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from agents.agent_fetch_post import fetch_and_parse
from agents.agent_router import router
from agents.agent_job_filter import filter_relevant_jobs
from agents.agent_send_mail import apply_for_jobs

# ---------------- STATE ----------------
class ScrapingState(TypedDict):
    urls: List[str]
    current_index: int
    csv_file: str
    errors: List[Dict[str, Any]]
    final_error: Dict[str, str]
    matched_jobs: List[Dict[str, Any]] 

# ---------------- GRAPH ----------------
workflow = StateGraph(ScrapingState)

# Nodes add karo
workflow.set_entry_point("process_page")
workflow.add_node("process_page", fetch_and_parse)
workflow.add_node("match_jobs", filter_relevant_jobs)
workflow.add_node("apply_jobs", apply_for_jobs)

# Conditional edges update karo
workflow.add_conditional_edges("process_page",router,{"continue": "process_page","match_jobs": "match_jobs", "end": END,},)
workflow.add_edge("match_jobs", "apply_jobs")
workflow.add_edge("apply_jobs", END)

scraper_app = workflow.compile()

# ---------------- RUNNER ----------------
def run_linkedin_scraper(input_urls: List[str]):
    initial_state = {
        "urls": input_urls,
        "current_index": 0,
        "csv_file": "results.csv",
        "errors": [],
        "final_error": {},
        "matched_jobs": [],
    }

    print("🚀 Starting Web Scraping and AI Job Matching Pipeline...")
    final_state = scraper_app.invoke(initial_state)

    if final_state.get("final_error"):
        print("\n=== EXECUTION STOPPED ===")
        print(json.dumps(final_state["final_error"], indent=2))
        return final_state["final_error"]

    if final_state.get("errors"):
        with open("post_errors_log.json", "w", encoding="utf-8") as f:
            json.dump(final_state["errors"], f, indent=2)

    print("\n🎉 Workflow Finished Successfully!")
    return {"status": "success"}

# ---------------- MAIN ----------------
if __name__ == "__main__":

    urls_to_scrape = [
        "https://www.linkedin.com/search/results/content/?keywords=%23hiring%20%23machinelearning&origin=GLOBAL_SEARCH_HEADER&datePosted=%5B%22past-24h%22%5D",
        "https://www.linkedin.com/search/results/content/?keywords=hiring%3A%20ai&origin=CLUSTER_EXPANSION&datePosted=%5B%22past-24h%22%5D",
        "https://www.linkedin.com/search/results/content/?keywords=%23genai%20%23hiring&origin=CLUSTER_EXPANSION&datePosted=%5B%22past-24h%22%5D",
        "https://www.linkedin.com/search/results/content/?keywords=%23hiring%20%23GenerativeAi%20&origin=GLOBAL_SEARCH_HEADER&datePosted=%5B%22past-24h%22%5D",
        "https://www.linkedin.com/search/results/content/?keywords=Hiring%3A%20AI%2FML%20&origin=GLOBAL_SEARCH_HEADER&datePosted=%5B%22past-24h%22%5D",
        "https://www.linkedin.com/search/results/content/?keywords=%23hiring%20%23python%20&origin=GLOBAL_SEARCH_HEADER&datePosted=%5B%22past-24h%22%5D",
        "https://www.linkedin.com/search/results/content/?keywords=%23hiring%20%23datascience&origin=GLOBAL_SEARCH_HEADER&datePosted=%5B%22past-24h%22%5D",
        "https://www.linkedin.com/search/results/content/?keywords=%23hiring%20%23langgraph&origin=GLOBAL_SEARCH_HEADER&datePosted=%5B%22past-24h%22%5D",
        "https://www.linkedin.com/search/results/content/?keywords=%23hiring%20%23rag&origin=GLOBAL_SEARCH_HEADER&datePosted=%5B%22past-24h%22%5D",
        "https://www.linkedin.com/search/results/content/?keywords=%23hiring%20%23agenticai&origin=GLOBAL_SEARCH_HEADER&datePosted=%5B%22past-24h%22%5D",
        "https://www.linkedin.com/search/results/content/?keywords=%23hiring%20%23ml&origin=GLOBAL_SEARCH_HEADER&datePosted=%5B%22past-24h%22%5D",
    
    ]
    run_linkedin_scraper(urls_to_scrape)