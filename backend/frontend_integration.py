from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pickle
import asyncio
import os
from jinja2 import Environment, FileSystemLoader
from Contemplation.report_generator import ReportGenerator
from Explorations.main_exploration import MainExploration

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the pre-trained model
with open('logiclurker_model.pkl', 'rb') as f:
    model = pickle.load(f)

report_gen = ReportGenerator(model)
env = Environment(loader=FileSystemLoader('Contemplation/templates'))

@app.post("/analyze")
async def analyze_url(data: dict):
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    exploration = MainExploration(url)
    result = await exploration.run()
    report_gen.report = {
        "date": "June 17, 2025 04:01 PM EAT",
        "summary": {"total_records": 10, "positive": 2, "positive_percentage": "20%"},  # Update based on actual results
        "details": [{"id": 1, "name": "SQLi", "status": "Vulnerable", "value": 0.85}, {"id": 2, "name": "XSS", "status": "Safe", "value": 0.10}]  # Update based on model output
    }
    report_text = report_gen.generate_report(result)  # Placeholder, adjust based on MainExploration output
    template = env.get_template("report.html")
    html_content = template.render(report_gen.report)
    return {"report": html_content}

@app.post("/generate-pdf")
async def generate_pdf(data: dict):
    report = data.get("report")
    if not report:
        raise HTTPException(status_code=400, detail="Report is required")
    pdf_file = report_gen.generate_pdf_report()
    return {"file": pdf_file}