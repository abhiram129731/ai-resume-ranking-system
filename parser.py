import PyPDF2

def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    
    for page in pdf_reader.pages:
        text += page.extract_text() + " "
    
    return text
