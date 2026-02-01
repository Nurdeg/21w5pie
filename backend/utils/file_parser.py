# backend/utils/file_parser.py
from fastapi import UploadFile, HTTPException
import pypdf
import docx
import io

async def parse_file(file: UploadFile) -> str:
    content = ""
    filename = file.filename.lower()
    
    # Read the file into memory
    file_bytes = await file.read()
    file_stream = io.BytesIO(file_bytes)

    try:
        if filename.endswith(".pdf"):
            reader = pypdf.PdfReader(file_stream)
            for page in reader.pages:
                content += page.extract_text() + "\n"
                
        elif filename.endswith(".docx"):
            doc = docx.Document(file_stream)
            content = "\n".join([para.text for para in doc.paragraphs])
            
        elif filename.endswith(".txt"):
            content = file_bytes.decode("utf-8")
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use PDF, DOCX, or TXT.")

        return content.strip()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File parsing error: {str(e)}")