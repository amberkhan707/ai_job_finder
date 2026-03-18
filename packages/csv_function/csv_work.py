import csv
import os

def append_to_csv(filename: str, name: str, email: str, text: str):
    file_exists = os.path.isfile(filename)
    
    # Check if file is empty (size 0) to write headers even if file exists
    is_empty = not file_exists or os.path.getsize(filename) == 0

    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        # LLM script yahi fieldnames expect kar raha hai: 'Name', 'Email', 'Text'
        writer = csv.DictWriter(f, fieldnames=['Name', 'Email', 'Text'])
        
        if is_empty:
            writer.writeheader()  # Pehli baar me header likh do
            
        writer.writerow({
            'Name': name,
            'Email': email,
            'Text': text
        })

def is_duplicate(filename: str, text: str) -> bool:
    if not os.path.isfile(filename):
        return False
        
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if 'Text' column matches
            if row.get('Text') == text:
                return True
    return False