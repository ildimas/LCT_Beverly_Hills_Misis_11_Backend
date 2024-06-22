import openpyxl
import io
import json
import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class BinaryXLSXParcer:
    def __init__(self):
        pass
    def binary_parcer(self, binary):
        if binary == None:
            return None
        doc = openpyxl.load_workbook(io.BytesIO(binary))
        doc_sheet = doc.active
        return doc_sheet
    
    def get_json(self):
        # Get the absolute path to the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the absolute path to the data.json file
        # print(script_dir)
        json_path = os.path.join(script_dir, "sber_files", "data.json")
        
        # Load the JSON data
        with open(json_path, 'r') as file:
            data = json.load(file)
        
        return data


