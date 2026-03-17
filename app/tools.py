import os
from dotenv import load_dotenv
from crewai.tools import tool
from crewai_tools import TavilySearchTool
from pypdf import PdfReader
import docx

# Load environment variables
load_dotenv()

@tool("Document Extractor Tool")
def extract_document_tool(file_path: str) -> str:
    """Read a document (PDF, DOCX, TXT) and return its extracted text content."""
    try:
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        
        if ext == '.pdf':
            reader = PdfReader(file_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        elif ext == '.docx':
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            return f"Unsupported file type: {ext}"
            
        return text
    except Exception as e:
        return f"Error extracting document text: {str(e)}"

# Initialize Search Tool
search_tool = TavilySearchTool()
