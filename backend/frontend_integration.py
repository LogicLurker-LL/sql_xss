from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.Explorations.path_subdomain_finder import Workset
from backend.Contemplation.report_generator import generate_report  # Adjust import
from backend.Explorations.fuzzer import fuzz_inputs  # Adjust import
from urllib.parse import urlparse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
import asyncio

app = FastAPI(title="Logic Lurker Frontend Integration")

# CORS middleware to allow frontend (e.g., http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust if using a different port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    url: str
    format: str = "json"  # Default to JSON, support json/pdf/text

async def scan_url(request: ScanRequest):
    try:
        # Path Finder
        workset = Workset()
        workset.url = request.url
        workset.parsed_url = urlparse(request.url)
        workset.base_domain = workset.parsed_url.netloc
        paths = workset.find_paths()  # From path_subdomain_finder_2.py

        # Parser (simplified; implement your parser if separate)
        parsed_data = [p for p in paths if p]

        # Fuzzer
        fuzzed_data = await fuzz_inputs(parsed_data)  # Assume async fuzzer

        # Neurosymbolic Logic (Logic Lurker - placeholder)
        async def analyze_vulnerabilities(data):
            vulnerabilities = []
            for item in data:
                if "sql" in item.lower():
                    vulnerabilities.append({
                        "type": "SQL Injection",
                        "location": item,
                        "reason": "Unescaped input detected",
                        "mitigation": ["Use prepared statements", "Sanitize inputs"]
                    })
                elif "script" in item.lower():
                    vulnerabilities.append({
                        "type": "XSS",
                        "location": item,
                        "reason": "Reflected script tag detected",
                        "mitigation": ["Escape HTML", "Implement CSP"]
                    })
            return vulnerabilities

        vulnerabilities = await analyze_vulnerabilities(fuzzed_data)

        # Report Generator
        report = generate_report(vulnerabilities, format=request.format)  # From report_generator_the_model.py

        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

@app.post("/scan")
async def scan_vulnerabilities(request: ScanRequest):
    report = await scan_url(request)
    if report is None:
        raise HTTPException(status_code=500, detail="No report generated")

    if request.format == "json":
        return {"vulnerabilities": report}
    elif request.format == "pdf":
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []
        for vuln in report:
            elements.append(Paragraph(f"Type: {vuln['type']}"))
            elements.append(Paragraph(f"Location: {vuln['location']}"))
            elements.append(Paragraph(f"Reason: {vuln['reason']}"))
            elements.append(Paragraph(f"Mitigation: {', '.join(vuln['mitigation'])}"))
            elements.append(Paragraph("\n"))
        doc.build(elements)
        pdf_buffer.seek(0)
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=vulnerability_report.pdf"})
    elif request.format == "text":
        text_content = "\n".join([f"Type: {vuln['type']}\nLocation: {vuln['location']}\nReason: {vuln['reason']}\nMitigation: {', '.join(vuln['mitigation'])}\n" for vuln in report])
        return Response(content=text_content, media_type="text/plain", headers={"Content-Disposition": "attachment; filename=vulnerability_report.txt"})
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

from fastapi.responses import StreamingResponse, Response