import smtplib
import os
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "..", "final_matched_jobs.csv")
RESUME_PATH = os.path.join(BASE_DIR, "..", "Amber_Resume.pdf")

def apply_for_jobs(state: Dict[str, Any]):
    print("\n [Email Agent] Starting automated job applications...")
    
    # State se matched jobs uthao, agar state me nahi hai toh CSV padh lo
    matched_jobs = state.get("matched_jobs", [])
    if not matched_jobs:
        try:
            with open("final_matched_jobs.csv", mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                matched_jobs = list(reader)
        except FileNotFoundError:
            print(" final_matched_jobs.csv not found. No jobs to apply for.")
            return state

    # .env se Email credentials load karo
    SENDER_EMAIL = "mdamberkhan707@gmail.com"
    SENDER_PASSWORD = "blvp vtjm zvga jgoj" # Make sure ye PDF aapke project folder me ho

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print(" Email credentials missing in .env! Cannot send emails.")
        return state

    if not os.path.exists(RESUME_PATH):
        print(f" Resume file '{RESUME_PATH}' not found! Cannot send emails.")
        return state

    # SMTP Server setup (Gmail ke liye 587 port use hota hai TLS ke sath)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Secure connection start karo
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
    except Exception as e:
        print(f" Failed to connect to email server: {e}")
        return state

    emails_sent = 0

    for job in matched_jobs:
        recipient = job.get("email", "").strip()
        
        # 1. Skip condition: Agar email 'NA' hai, khali hai, ya valid format me nahi hai
        if not recipient or recipient.upper() == "NA" or "@" not in recipient:
            continue

        # 2. Construct the Email
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient
        msg['Subject'] = "Application for AI/ML Engineer Role - MD Amber Khan"

        # Email Body (Customized for your profile)
        body = """Hi Hiring Team,

I saw your recent hiring post and am very interested in the opportunity. 

With 2 years of experience building Agentic AI systems, RAG-based chatbots, and deploying ML models, I believe my skills strongly align with your requirements. 

I have attached my resume for your review. I would love to connect and discuss how I can add value to your team.

My details:
Name: Amber Khan

Contact Number: 9304800896

Email ID: mdamberkhan707@gmail.com

Current Company: Larsen & Toubro - Digital Solutions

Current Designation: Python Developer

Current Location: Chennai

Native Place: Bihar

Total Experience: 2 yrs

Education Qualification: BTech

Current CTC: 6 LPA

Expected CTC: 9 LPA

Notice Period: 15 days

Reason For Job Change: Career growth

Best Regards,
MD Amber Khan
LinkedIn: http://linkedin.com/in/md-amber-khan-8398a5355/
GitHub: https://github.com/amberkhan707
"""
        msg.attach(MIMEText(body, 'plain'))

        # 3. Attach Resume
        with open(RESUME_PATH, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename="MD_Amber_Khan_Resume.pdf")
            msg.attach(attach)

        # 4. Send Email
        try:
            server.send_message(msg)
            print(f"Application successfully sent to: {recipient}")
            emails_sent += 1
        except Exception as e:
            print(f"Failed to send email to {recipient}. Error: {e}")

    server.quit() # Connection close karo
    print(f"\nMission Accomplished! Total {emails_sent} job applications sent!")
    
    return state