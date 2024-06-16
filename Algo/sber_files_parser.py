import openpyxl
import json

path3800_2023 = "sber_files/Счета на оплату тест.xlsx"
contracts = "sber_files/Договоры.xlsx"
codes = "sber_files/Коды услуг.xlsx"
fixed_assets = "sber_files/Основные средства.xlsx"
buildings_square = "sber_files/Площади зданий.xlsx"
contracts_buildings = "sber_files/Связь договор - здания.xlsx"

# парсинг счетов на оплату
wb_obj_path3800_2023 = openpyxl.load_workbook(path3800_2023)
sheet_obj_path3800_2023 = wb_obj_path3800_2023.active
wb_obj_path3800_2023.save(path3800_2023)

# парсинг связи договора-зданий
wb_obj_contracts_buildings = openpyxl.load_workbook(contracts_buildings)
sheet_obj_contracts_buildings = wb_obj_contracts_buildings.active
wb_obj_contracts_buildings.save(contracts_buildings)

# парсинг площадей зданий
wb_obj_buildings_square = openpyxl.load_workbook(buildings_square)
sheet_obj_buildings_square = wb_obj_buildings_square.active
wb_obj_buildings_square.save(buildings_square)

# парсинг кодов услуг
wb_obj_codes = openpyxl.load_workbook(codes)
sheet_obj_codes = wb_obj_codes.active
wb_obj_codes.save(codes)

# парсинг основного средства
wb_obj_fixed_assets = openpyxl.load_workbook(fixed_assets)
sheet_obj_fixed_assets = wb_obj_fixed_assets.active
wb_obj_fixed_assets.save(fixed_assets)

# запись json
with open("sber_files/data.JSON", 'r') as file:
    data = json.load(file)