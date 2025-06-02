from fastapi import FastAPI,UploadFile,File
import os
import fitz
from fastapi.middleware.cors  import CORSMiddleware
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/")
async def root():
    return {"message":"FastAPI is running"}


@app.post("/PDF_Parser")
async def extract_text_from_pdf(file: UploadFile = File(...)):
    try:
        file_path = f"./{file.filename}"
        if not file.filename.endswith('.pdf'):
            return {"error": "File is not a PDF"}

        with open(file_path, "wb") as pdf_file:
            pdf_file.write(await file.read())

        doc = fitz.open(file_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        os.remove(file_path)

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        title = ""
        for line in lines:
            match = re.search(r"\b(Yojana|Scheme|Circular)\b", line, re.IGNORECASE)
            if match:
                title = line.strip()
                break
            if match and "scheme" in line.lower():
                title = match.group(1).strip()
                break

        department = ""
        for line in lines:
            if re.search(r"(Ministry|Department) of", line, re.IGNORECASE):
                department = line.strip()
                break

        step_pattern = re.compile(r"^\d+\.\s+.+")
        steps = [line for line in lines if step_pattern.match(line)]

        description_lines = []
        for line in lines:
            if line.lower().startswith("page"):
                continue
            if step_pattern.match(line):
                break
            description_lines.append(line)
            if len(description_lines) >= 4:
                break

        full_text = "\n".join(lines)
        eligibility_criteria = ""
        eligibility_match = re.search(
        r"Eligibility Criteria[:\-]?\s*(.*?)(?=\n\d+\.|\n[A-Z][a-z]+[:\-])",
        full_text,
        re.DOTALL | re.IGNORECASE
        )
        if eligibility_match:
            eligibility_criteria = eligibility_match.group(1).strip().replace("\n"," ")

        used_lines = set(description_lines + steps + [department, title])

        others = [line for line in lines if line not in used_lines]

        others_text = " ".join(others)

        website_match = re.search(r"(https?://[^\s]+|www\.[^\s]+)", others_text)
        phone_match = re.search(
        r"(?i)(?:toll[\s-]?free[\s-]?number[:\-]?\s*)?(\+91[\s\-]?\d{2,5}[\s\-]?\d{3,4}[\s\-]?\d{3,4}|\b(?:1?8?00|08\d{2})[\d\s\-]{4,10}\b|\b\d{7,12}\b)",
        others_text)


        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", others_text)

        contact_details = {
            "website": website_match.group(0) if website_match else None,
            "toll_free_number": phone_match.group(1) if phone_match else None,
            "email": email_match.group(0) if email_match else None
        }

        return {
            "Title": title,
            "Department": department,
            "Description": " ".join(description_lines),
            "Eligibility Criteria": eligibility_criteria,
            "Steps": steps,
            "Other Details": others_text,
            "Contact Details": contact_details
        }

    except Exception as e:
        return {"error": str(e)}
