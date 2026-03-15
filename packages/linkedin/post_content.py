import re

# ---------------- HELPERS ----------------
def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())

# ---------------- EXTRACT TEXT ----------------
def extract_post_text(post):
    # 1. Exact Tag Identifier for LinkedIn SDUI (100% reliable)
    content_tag = post.find(attrs={"data-testid": "expandable-text-box"})
    if content_tag:
        text = content_tag.get_text(" ", strip=True)
        # LinkedIn adds "... more" button text inside the tag, let's remove it
        text = re.sub(r"…\s*more$", "", text, flags=re.IGNORECASE).strip()
        return normalize_whitespace(text)

    # 2. Fallback Legacy Selectors
    text_selectors = [
        ".update-components-text",
        ".feed-shared-update-v2__description",
        ".break-words",
        ".tvm-parent-container"
    ]

    for selector in text_selectors:
        tag = post.select_one(selector)
        if tag:
            text = tag.get_text(" ", strip=True)
            if len(text) > 20:
                text = re.sub(r"…\s*more$", "", text, flags=re.IGNORECASE).strip()
                return normalize_whitespace(text)

    return ""
