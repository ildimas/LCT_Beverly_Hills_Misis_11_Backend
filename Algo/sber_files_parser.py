import openpyxl

path3800_2023 = "sber_files/Счета на оплату 3800-2023.XLSX"
contracts = "sber_files/Договоры.XLSX"
codes = "sber_files/Коды услуг.XLSX"
fixed_assets = "sber_files/Основные средства.XLSX"
buildings_square = "sber_files/Площади зданий.XLSX"
contracts_buildings = "sber_files/Связь договор - здания.XLSX"

# парсинг счетов на оплату
wb_obj_path3800_2023 = openpyxl.load_workbook(path3800_2023)
sheet_obj_path3800_2023 = wb_obj_path3800_2023.active

# парсинг связи договора-зданий
wb_obj_contracts_buildings = openpyxl.load_workbook(contracts_buildings)
sheet_obj_contracts_buildings = wb_obj_contracts_buildings.active

# парсинг площадей зданий
wb_obj_buildings_square = openpyxl.load_workbook(buildings_square)
sheet_obj_buildings_square = wb_obj_buildings_square.active

# парсинг кодов услуг
wb_obj_codes = openpyxl.load_workbook(codes)
sheet_obj_codes = wb_obj_codes.active

# парсинг основного средства
wb_obj_fixed_assets = openpyxl.load_workbook(fixed_assets)
sheet_obj_fixed_assets = wb_obj_fixed_assets.active