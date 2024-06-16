import pandas as pd
import io
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
        output = io.BytesIO()
        with io.TextIOWrapper(output, encoding='utf-8', newline='') as text_file:
            writer = csv.writer(text_file, delimiter=';')
            writer.writerow(headers_list)
            for row in data:
                writer.writerow(row)
            csv_binary_data = output.getvalue()
        #csv binary
        return csv_binary_data