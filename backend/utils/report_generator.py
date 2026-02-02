# backend/utils/report_generator.py
from fpdf import FPDF
import tempfile

class PDFReport(FPDF):
    def header(self):
        # Logo or Title
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'AI Smart Analysis Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(data: dict) -> str:
    pdf = PDFReport()
    pdf.add_page()
    
    # 1. Summary Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Executive Summary", 0, 1)
    pdf.set_font("Arial", "", 11)
    # Multi_cell handles text wrapping automatically
    pdf.multi_cell(0, 7, data.get("summary", "No summary available."))
    pdf.ln(5)

    # 2. Key Metrics (Sentiment & Intent)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Key Metrics", 0, 1)
    pdf.set_font("Arial", "", 11)
    
    sentiment = data.get("sentiment", "Unknown").title()
    score = data.get("sentiment_score", 0)
    intent = data.get("intent", "Unknown").title()
    
    pdf.cell(50, 10, f"Sentiment: {sentiment}", 1)
    pdf.cell(50, 10, f"Score: {score}", 1)
    pdf.cell(50, 10, f"Intent: {intent}", 1)
    pdf.ln(15)

    # 3. Entities Table
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Detected Entities", 0, 1)
    
    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(90, 10, "Entity Text", 1, 0, 'C', fill=True)
    pdf.cell(50, 10, "Category", 1, 1, 'C', fill=True)
    
    # Table Rows
    pdf.set_font("Arial", "", 10)
    for ent in data.get("entities", []):
        pdf.cell(90, 8, ent['text'], 1)
        pdf.cell(50, 8, ent['label'], 1, 1)

    # Save to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name