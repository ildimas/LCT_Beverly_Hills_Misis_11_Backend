files = ["sber_files/Распределенные счета на оплату 4200-4000-3800-2024.XLSX", "sber_files/Распределенные счета на оплату 5500-2023.XLSX",
         "sber_files/Распределенные счета на оплату 5400-2023.XLSX","sber_files/Распределенные счета на оплату 5400-2024.XLSX", "sber_files/Распределенные счета на оплату 3800-2023.XLSX"]
# files = ["sber_files/Распределенные счета на оплату 3800-2023.XLSX"]
import pandas as pd
from collections import defaultdict
import os
import json



def process_excel_file(file_path, ledger_building_dict):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        building = row['Здание']
        try:
            ledger_account = int(row['Счет главной книги'])
            building = building[4:]
        except Exception:
            continue
        if  building not in ledger_building_dict.keys():
            ledger_building_dict[building] = set()
            ledger_building_dict[building].add(ledger_account)
        else:
            ledger_building_dict[building].add(ledger_account)
    return ledger_building_dict

ledger_building_dict = {}
for file in files:
    print(f"current {file}")
    process_excel_file(file, ledger_building_dict)
    
for key in ledger_building_dict.keys():
    ledger_building_dict[key] = list(ledger_building_dict[key])    

print("json transmutation")
with open('data.json', 'w') as json_file:
    json.dump(ledger_building_dict, json_file)
