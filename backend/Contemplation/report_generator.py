import os
import pickle
import sys
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
# generate report based on the model's result ...
from importnb import Notebook
with Notebook():
    import logic_lurker as ll


class ReportGenerator:
    def __init__(self, models, response_space):
        self.models = models 
        self.response_space = response_space
        self.vulnerableRequestDetected = []
        self.report = dict()  # Initialize an empty report dictionary

    def data_preprocessing(self, model_name, instance):
        # Implement data preprocessing logic here 
        pass

    def inference(self):
        for instance in self.response_space:
            for model in self.models:
                prepared_data_instance = self.data_preprocessing(model.name, instance)
                model.add_data(prepared_data_instance)
                model.infer()
                
                model.state()[''] # replace model by the formula name...  


        pass


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
    

def main():
    pass

main()