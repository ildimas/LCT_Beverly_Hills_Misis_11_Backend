import pandas as pd
import io
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from typing import BinaryIO
import csv

class DATA_CSV_XLSX_Converter:
    def __init__(self):
        pass
    def convert(self, binary: BinaryIO):
        csv_file = io.BytesIO(binary)
        df = pd.read_csv(csv_file)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        #excel binary
        return excel_buffer.getvalue()
    
    def data_to_csv(self, headers_list, data):
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow(headers_list)
        csv_writer.writerows(data)
        csv_binary_string = csv_buffer.getvalue().encode('utf-8')  # Convert to binary
        return csv_binary_string
