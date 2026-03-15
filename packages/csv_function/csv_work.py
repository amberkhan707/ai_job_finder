import os 
import csv

def append_to_csv(csv_file: str, name: str, email: str, content: str):
    file_exists = os.path.exists(csv_file)

    with open(csv_file, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)

        if not file_exists:
            writer.writerow(["name", "email", "content"])

        writer.writerow([name, email, content])

def is_duplicate(csv_file: str, normalized_content: str) -> bool:
    if not os.path.exists(csv_file):
        return False

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("content") == normalized_content:
                return True

    return False