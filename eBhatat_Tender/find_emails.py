import re
import os

files_to_check = [
    'tenders/views.py', 
    'funding/views.py', 
    'coreadmin/views.py', 
    'bids/views.py', 
    'accounts/views.py', 
    'accounts/signals.py'
]

with open('emails_list.txt', 'w', encoding='utf-8') as out_f:
    for filepath in files_to_check:
        out_f.write(f"\n[{filepath}]:\n")
        if not os.path.exists(filepath): continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if 'send_ebharat_email(' in line:
                action = "unknown"
                for j in range(i, -1, -1):
                    if lines[j].strip().startswith("def "):
                        action = lines[j].strip()
                        break
                
                template_name = "unknown"
                for j in range(i, min(i+15, len(lines))):
                    match = re.search(r'template_name=[\'"]([^\'"]+)[\'"]', lines[j])
                    if match:
                        template_name = match.group(1)
                        break
                        
                out_f.write(f"- line {i+1}: Action '{action}' uses template '{template_name}'\n")
