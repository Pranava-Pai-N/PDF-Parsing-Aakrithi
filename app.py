from fastapi import FastAPI,UploadFile,File
import os
import fitz
from fastapi.middleware.cors  import CORSMiddleware
import re
import unicodedata


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
        if not file.filename.endswith('.pdf'):
            return {"Error":"File is not PDF"}
        
        file_path = f"./{file.filename}"
        
        with open(file_path,"wb") as pdf_file:
            pdf_file.write(await file.read())
            
        doc = fitz.open(file_path)
        text = '\n'.join(page.get_text() for page in doc)
        doc.close()
        
        os.remove(file_path)
        normalized_text = unicodedata.normalize("NFKD", text)
        clean_text = normalized_text.encode("utf-8", "ignore").decode("utf-8").replace("\n"," ")
        
        return {"Response" : clean_text}
    
    
    except Exception as e:
        return {"error": str(e)}
