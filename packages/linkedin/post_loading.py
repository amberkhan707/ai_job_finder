import time
import requests

PINCHTAB_URL = "http://localhost:9868"

def wait_for_posts():
    for _ in range(15):
        try:
            # Bulletproof check: Look for articles, listitems, or exact text boxes
            res = requests.post(
                f"{PINCHTAB_URL}/evaluate",
                json={
                    "expression": "document.querySelectorAll('article, [role=\"listitem\"], [data-testid=\"expandable-text-box\"]').length"
                },
                timeout=10,
            )

            data = res.json()
            count = int(data.get("result", 0))

            if count > 0:
                time.sleep(3) # Thoda extra time DOM completely paint hone ke liye
                return True

            # scroll to trigger lazy loading
            requests.post(
                f"{PINCHTAB_URL}/evaluate",
                json={"expression": "window.scrollBy(0, window.innerHeight)"},
                timeout=5,
            )

        except:  # noqa: E722
            pass

        time.sleep(1)

    return False
