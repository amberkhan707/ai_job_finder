import json
import re
import requests
from bs4 import BeautifulSoup
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from packages.csv_function.csv_work import append_to_csv, is_duplicate
from packages.linkedin.post_author import extract_author
from packages.linkedin.post_content import extract_post_text
from packages.linkedin.post_identify import find_posts
from packages.linkedin.post_loading import wait_for_posts


# ---------------- CONSTANTS ----------------
EMAIL_REGEX = r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
PINCHTAB_URL = "http://localhost:9868"

# ---------------- STATE ----------------
class ScrapingState(TypedDict):
    urls: List[str]
    current_index: int
    csv_file: str
    errors: List[Dict[str, Any]]
    final_error: Dict[str, str]

# ---------------- MAIN NODE ----------------
def fetch_and_parse(state: ScrapingState):
    
    idx = state["current_index"]
    urls = state["urls"]
    if idx >= len(urls):
        return state
    url = urls[idx]

    try:
        print(f"\n[{idx+1}/{len(urls)}] Navigating...")

        requests.post(f"{PINCHTAB_URL}/navigate",json={"url": url},timeout=20,)

        print("Waiting for posts to render...")
        wait_for_posts()
        print("Extracting DOM...")
        
        res = requests.post(f"{PINCHTAB_URL}/evaluate",json={"expression": "document.documentElement.outerHTML"},timeout=20,)
        html_content = res.json().get("result", "")

    except Exception as e:
        state["final_error"] = {
            "status": "error",
            "reason": "pinchtab_execution_error",
            "details": str(e),
        }
        return state

    # save debug html
    with open(f"debug_page_{idx}.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    if not html_content.strip():
        state["final_error"] = {
            "status": "error",
            "reason": "empty_html_returned",
        }
        return state

    soup = BeautifulSoup(html_content, "html.parser")

    page_title = ""
    if soup.title and soup.title.string:
        page_title = soup.title.string.lower()

    if "login" in page_title or "sign in" in page_title:

        state["final_error"] = {
            "status": "error",
            "reason": "requires_authentication",
        }

        return state

    posts = find_posts(soup)

    if not posts:
        print("No posts detected in DOM. (Check debug HTML)")
        state["errors"].append(
            {
                "post_index": -1,
                "reason": "no_posts_found_in_dom",
            }
        )
    else:
        print(f"✅ {len(posts)} posts detected")

    seen_texts = set()

    for i, post in enumerate(posts, start=1):
        text = extract_post_text(post)
        if not text:
            continue
        if text in seen_texts:
            continue

        seen_texts.add(text)
        name = extract_author(post)
        emails = re.findall(EMAIL_REGEX, text)
        email_cell = ";".join(emails) if emails else "NA"

        if not is_duplicate(state["csv_file"], text):
            append_to_csv(state["csv_file"], name, email_cell, text)

    print(f"--> Saved results from URL {idx+1}")

    state["current_index"] += 1
    return state

# ---------------- Node ----------------
def router(state: ScrapingState):

    if state.get("final_error"):
        return "end"
    if state["current_index"] < len(state["urls"]):
        return "continue"

    return "end"

# ---------------- GRAPH ----------------
workflow = StateGraph(ScrapingState)
workflow.add_node("process_page", fetch_and_parse)
workflow.set_entry_point("process_page")
workflow.add_conditional_edges("process_page",router,{"continue": "process_page","end": END,},)

scraper_app = workflow.compile()

# ---------------- RUNNER ----------------
def run_linkedin_scraper(input_urls: List[str]):

    initial_state = {
        "urls": input_urls,
        "current_index": 0,
        "csv_file": "results.csv",
        "errors": [],
        "final_error": {},
    }

    final_state = scraper_app.invoke(initial_state)

    if final_state.get("final_error"):

        print("\n=== EXECUTION STOPPED ===")
        print(json.dumps(final_state["final_error"], indent=2))

        return final_state["final_error"]

    if final_state.get("errors"):

        with open("post_errors_log.json", "w", encoding="utf-8") as f:
            json.dump(final_state["errors"], f, indent=2)

    print("\n🎉 Scraping finished. Data appended to results.csv")

    return {"status": "success"}

# ---------------- MAIN ----------------
if __name__ == "__main__":

    urls_to_scrape = [
        "https://www.linkedin.com/search/results/content/?keywords=hiring%3A%20ai&origin=CLUSTER_EXPANSION&datePosted=%5B%22past-24h%22%5D",
        "https://www.linkedin.com/search/results/content/?keywords=%23genai%20%23hiring&origin=CLUSTER_EXPANSION&datePosted=%5B%22past-24h%22%5D",
    ]

    run_linkedin_scraper(urls_to_scrape)