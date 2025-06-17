from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
# generate report based on the model's result ...

class ReportGenerator:
    def __init__(self, model):
        self.model = model 
        self.report = dict()  # Initialize an empty report dictionary


    def generate_report(self, response_space):
        # This method should be implemented to generate a report based on the model's results
        # For now, it will just return a placeholder string
        # update self.report with the actual report data
        return "Report generated based on the model's results."
    
    def generate_pdf_report(self):
        env = Environment(loader=FileSystemLoader('Contemplation/templates'))
        template = env.get_template("report.html")
                
        # Render HTML template
        html_content = template.render(self.report)
        
        # Generate PDF
        pdf_file = HTML(string=html_content).write_pdf()
        
        return pdf_file