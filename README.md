# LinkedIn Job Apply Automation (LangGraph + Agents)

Automated pipeline to scrape LinkedIn hiring posts, filter relevant jobs using AI logic, and apply/send emails via modular agents.

---

## ⚙️ Workflow Overview

Pipeline built using **LangGraph StateGraph**:

process_page → router → process_page (loop)
→ match_jobs → apply_jobs → END


### Nodes

- **process_page** → `fetch_and_parse`
  - Scrapes LinkedIn posts from URLs
  - Stores results in CSV

- **router** → `agent_router`
  - Decides:
    - Continue scraping
    - Move to filtering
    - End execution

- **match_jobs** → `filter_relevant_jobs`
  - Filters jobs based on relevance

- **apply_jobs** → `apply_for_jobs`
  - Sends applications / emails

---

## 🧠 State Management

``` python
class ScrapingState(TypedDict):
    urls: List[str]
    current_index: int
    csv_file: str
    errors: List[Dict[str, Any]]
    final_error: Dict[str, str]
    matched_jobs: List[Dict[str, Any]]
```
### How It Works

Input LinkedIn search URLs

Scrape posts (loop across URLs)

Store results in results.csv

Filter relevant jobs

Save matched jobs

Apply/send emails automatically


## ▶️ Run the Project

### 1. Install Dependencies

```
pip install -r requirements.txt
```


### 2. Setup Environment Variables

Create `.env` file:

```
EMAIL=your_email
PASSWORD=your_password
SMTP_SERVER=your_smtp
```


(Adjust based on your email agent logic)

---

### 3. Run Script

```
python main.py
```


---

## 🔗 Input URLs

Defined in `main.py`:

LinkedIn search queries using:

- hashtags (`#hiring`, `#AI`, `#ML`, etc.)
- date filter (past 24h)

Example:

```
https://www.linkedin.com/search/results/content/?keywords=%23hiring%20%23machinelearning&datePosted=past-24h
```
