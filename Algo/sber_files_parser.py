import openpyxl
import io
import json
import csv

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
        with open("sber_files/data.json", 'r') as file:
            data = json.load(file)
        return data

