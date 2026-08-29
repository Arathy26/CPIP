import sys
sys.path.append(".")

from app.services.resume_parser import extract_text

with open("Arathy Rajeev Resume.pdf", "rb") as f:
    text = extract_text("Arathy Rajeev Resume.pdf", f.read())

print(text[:2000])