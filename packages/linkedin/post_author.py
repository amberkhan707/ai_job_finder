import re

# ---------------- EXTRACT NAME ----------------
def extract_author(post):
    # 1. Smart SDUI Approach (Find profile link and extract clean text)
    profile_links = post.find_all("a", href=re.compile(r"linkedin\.com/in/"))
    
    for link in profile_links:
        # Skip avatar images without text
        if not link.get_text(strip=True):
            continue
            
        # LinkedIn heavily hides the clean name in an aria-hidden span
        hidden_span = link.find("span", attrs={"aria-hidden": "true"})
        if hidden_span and hidden_span.contents:
            name = str(hidden_span.contents[0]).strip()
            if name and name.lower() not in ["feed post", "linkedin", "view profile"]:
                return name.split('\n')[0].strip()
        
        # Safe raw text fallback
        raw_text = link.get_text(" ", strip=True)
        clean_name = raw_text.split('\n')[0].split(',')[0].strip() # Clean "Vatsal Shah, Hiring..."
        if clean_name and clean_name.lower() not in ["feed post", "linkedin"]:
            return clean_name

    # 2. Old Class Selectors Fallback
    name_selectors = [
        ".update-components-actor__name",
        ".feed-shared-actor__name",
        ".app-aware-link",
        "a[data-control-name]"
    ]

    for selector in name_selectors:
        tag = post.select_one(selector)
        if tag:
            text = tag.get_text(strip=True)
            if text and text.lower() != "linkedin":
                return text.split("\n")[0].strip()

    return "NA"
