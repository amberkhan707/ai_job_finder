import re
import time
import requests
from bs4 import BeautifulSoup
from typing import TypedDict, List, Dict, Any
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

def fetch_and_parse(state: ScrapingState):
    idx = state["current_index"]
    urls = state["urls"]
    if idx >= len(urls):
        return state
    url = urls[idx]

    try:
        print(f"\n[{idx+1}/{len(urls)}] Navigating to URL...")
        requests.post(f"{PINCHTAB_URL}/navigate", json={"url": url}, timeout=20)

        print("Waiting for initial posts to render...")
        wait_for_posts() 
        
        # --- NAYA: In variables ko loop ke bahar initialize karo ---
        seen_texts = set()
        total_extracted = 0
        
        print("Scrolling and extracting posts incrementally...")
        last_height = 0
        scroll_attempts = 0
        MAX_SCROLLS = 40  # Max limit badha kar 40 kar di hai
        no_change_count = 0 

        while scroll_attempts < MAX_SCROLLS:
            # 1. Pehle DOM extract kar lo, taaki purane posts DOM se hatne se pehle humare paas save ho jayein
            res_html = requests.post(
                f"{PINCHTAB_URL}/evaluate",
                json={"expression": "document.documentElement.outerHTML"},
                timeout=20
            )
            html_content = res_html.json().get("result", "")
            
            if html_content:
                soup = BeautifulSoup(html_content, "html.parser")
                
                # Authentication check sirf pehli baar (0th attempt pe) karna kaafi hai
                if scroll_attempts == 0:
                    page_title = soup.title.string.lower() if soup.title else ""
                    if "login" in page_title or "sign in" in page_title:
                        state["final_error"] = {"status": "error", "reason": "requires_authentication"}
                        return state

                # HAR SCROLL PE EXTRACTION CHALU HAI
                posts = find_posts(soup)
                new_posts_in_this_scroll = 0
                
                for post in posts:
                    text = extract_post_text(post)
                    # Agar text khali hai ya pehle hi extract ho chuka hai, toh ignore karo
                    if not text or text in seen_texts:
                        continue
                        
                    seen_texts.add(text)
                    name = extract_author(post)
                    emails = re.findall(EMAIL_REGEX, text)
                    email_cell = ";".join(emails) if emails else "NA"

                    if not is_duplicate(state["csv_file"], text):
                        append_to_csv(state["csv_file"], name, email_cell, text)
                        total_extracted += 1
                        new_posts_in_this_scroll += 1
                        
                if new_posts_in_this_scroll > 0:
                    print(f"   => Extracted {new_posts_in_this_scroll} new posts in this scroll. (Total saved: {total_extracted})")

            # 2. Extract karne ke baad Niche Scroll karo
            scroll_script = """
            window.scrollBy({top: 1500, behavior: 'smooth'}); 
            setTimeout(() => window.scrollTo(0, document.body.scrollHeight), 1000);
            """
            requests.post(f"{PINCHTAB_URL}/evaluate", json={"expression": scroll_script}, timeout=20)
            time.sleep(4) # Naye posts fetch hone ke liye network wait
            
            # 3. "Load more" button dhundo aur click karo
            click_script = """
            (function() {
                var buttons = Array.from(document.querySelectorAll('button'));
                var loadMoreBtn = buttons.find(b => b.innerText && (
                    b.innerText.toLowerCase().includes('load more') || 
                    b.innerText.toLowerCase().includes('show more results') ||
                    b.innerText.toLowerCase().includes('see more results')
                ));
                if (loadMoreBtn) {
                    loadMoreBtn.scrollIntoView({behavior: 'smooth', block: 'center'});
                    setTimeout(() => loadMoreBtn.click(), 500);
                    return true;
                }
                return false;
            })();
            """
            res_btn = requests.post(f"{PINCHTAB_URL}/evaluate", json={"expression": click_script}, timeout=20)
            if res_btn.json().get("result") is True:
                print("✅ Clicked 'Load More' button. Waiting extra time...")
                time.sleep(5) 

            # 4. Height check & Smart break logic
            res_height = requests.post(f"{PINCHTAB_URL}/evaluate", json={"expression": "document.body.scrollHeight"}, timeout=20)
            new_height = res_height.json().get("result", 0)

            if new_height == last_height:
                no_change_count += 1
                if no_change_count >= 3: # Agar 3 baar tak height na badhe tabhi roko
                    print("🏁 No more new content loading. Reached the end.")
                    break
                else:
                    print(f"⚠️ Height didn't change (Try {no_change_count}/3). Waiting a bit more...")
                    time.sleep(3)
            else:
                no_change_count = 0
                
            last_height = new_height
            scroll_attempts += 1
            print(f"🔄 Preparing next scroll... (Attempt {scroll_attempts}/{MAX_SCROLLS})")

    except Exception as e:
        state["final_error"] = {"status": "error", "reason": "pinchtab_execution_error", "details": str(e)}
        return state

    # Loop ke baad aakhiri summary
    if total_extracted == 0:
        print("No posts detected overall. (Check logic or selectors)")
        state["errors"].append({"post_index": -1, "reason": "no_posts_found_in_dom"})
    else:
        print(f"🎉 URL {idx+1} DONE! Successfully extracted {total_extracted} unique posts.")

    state["current_index"] += 1
    return state
