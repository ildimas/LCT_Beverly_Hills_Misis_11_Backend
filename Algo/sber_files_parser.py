import openpyxl
import io
import json
import csv
import sys
import os
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

class BinaryXLSXParcer:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)  # Adjust the number of workers as needed

    async def binary_parcer(self, binary):
        if binary is None:
            return None
        loop = asyncio.get_event_loop()
        doc = await loop.run_in_executor(self.executor, openpyxl.load_workbook, io.BytesIO(binary))
        doc_sheet = doc.active
        return doc_sheet
    
    async def get_json(self):
        # Get the absolute path to the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the absolute path to the data.json file
        json_path = os.path.join(script_dir, "sber_files", "data.json")
        
        async with aiofiles.open(json_path, 'r') as file:
            data = await file.read()
        
        return json.loads(data)