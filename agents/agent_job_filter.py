import csv
import json
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

def filter_relevant_jobs(state: Dict[str, Any]):
    print("\n [LLM Agent] Reading CSV and matching jobs with your profile...")
    
    csv_file = state.get("csv_file", "results.csv")
    matched_jobs = []
    
    llm = ChatGroq(model = "openai/gpt-oss-120b", api_key= API_KEY)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert recruiter for any role with below 3yr of experience in AI Engineer, Generative AI Engineer, Machine Learning Engineer, Data Science Role or Backend AI roles focused on Agentic AI systems, RAG pipelines, LLM applications, and AI automation and all the roles related to AI, python and Machine learning datascience.. Your job is to refer candidate's profile."),
        ("human", "\n\nJob Description:\n{job_desc}\n\nDoes this job matches role and experience? Answer strictly in JSON format with two keys: 'is_match' (boolean true/false) and 'reason' (a 1-sentence explanation).")
    ])
    
    chain = prompt | llm

    try:
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f) # Assuming aapke CSV me headers hain (e.g., Name, Email, Text)
            
            for row in reader:
                job_text = row.get("Text", "") # Aapke CSV ke column ka naam
                if not job_text:
                    continue
                
                # LLM ko call lagao
                response = chain.invoke({"job_desc": job_text})
                
                # JSON response parse karo
                try:
                    # Strip markdown blocks if any
                    clean_res = response.content.replace("```json", "").replace("```", "").strip()
                    result = json.loads(clean_res)
                    
                    if result.get("is_match"):
                        print(f" Match Found! Reason: {result.get('reason')}")
                        matched_jobs.append({
                            "author": row.get("Name", "Unknown"),
                            "email": row.get("Email", "NA"),
                            "job_text": job_text,
                            "match_reason": result.get("reason")
                        })
                except json.JSONDecodeError:
                    print("Error parsing LLM response for a job.")
                    
    except FileNotFoundError:
        print("❌ CSV file not found. Nothing to match.")
        
    # Nayi matched jobs ko state me save kar do
    state["matched_jobs"] = matched_jobs
    
    # Optional: Matched jobs ko ek naye CSV me save kar lo
    if matched_jobs:
        with open("final_matched_jobs.csv", "w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["author", "email", "job_text", "match_reason"])
            writer.writeheader()
            writer.writerows(matched_jobs)
        print(f"\n🎉 Saved {len(matched_jobs)} matching jobs to final_matched_jobs.csv")
    else:
        print("\n⚠️ No exact matches found for your profile in the current batch.")
        
    return state