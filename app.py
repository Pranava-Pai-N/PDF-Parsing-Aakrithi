from fastapi import FastAPI,UploadFile,File
import os
import fitz

app = FastAPI()



@app.get("/")
async def root():
    return {"message":"FastAPI is running"}


@app.post("/PDF_Parser")
async def extract_text_from_pdf(file: UploadFile = File(...)):
    try:
        file_path = f"./{file.filename}"
        if not(file.filename.endswith('.pdf')): 
            return {"error": "File is not a PDF"}
        
        with open(file_path, "wb") as pdf_file:
            pdf_file.write(await file.read())

        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text().strip()+"\n"
            
        text = text.strip()
        
        doc.close()
        os.remove(file_path)
        
        return {"extracted_text": text.replace("\n"," ")}
    
    
    except Exception as e:
        return {"error": str(e)}
