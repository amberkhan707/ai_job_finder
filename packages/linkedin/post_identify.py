from bs4 import BeautifulSoup
import re

def find_posts(soup: BeautifulSoup):
    # 1. SDUI Strict approach (Search page heavily uses this)
    posts = soup.find_all("div", attrs={"role": "listitem"})
    if posts:
        return posts

    # 2. Component Key fallback
    posts = soup.find_all("div", attrs={"componentkey": re.compile(r"FeedType|SearchResult")})
    if posts:
        return posts

    # 3. Old UI / Home Feed fallback
    posts = soup.select("article, .feed-shared-update-v2, .occludable-update")
    return posts
