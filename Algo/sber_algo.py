import sber_files_parser

input = []
for i in range(1, sber_files_parser.sheet_obj_path3800_2023.max_column + 1):
    input.append(sber_files_parser.sheet_obj_path3800_2023.cell(row = 353, column = i).value)
# принимаем - Компания, год, номер счёта, позиция счёта, ID услуги, ID договора, дата отражения учёта, стоимость без ДНС

#! Базовый
# список всех связанных ЗДН с ДПН
build_contracts = []
build_contracts_found = 0
for i in range(2, sber_files_parser.sheet_obj_contracts_buildings.max_row):
    if (build_contracts_found > 0 and sber_files_parser.sheet_obj_contracts_buildings.cell(row = i, column = 1).value != input[5]):
        break
    elif (sber_files_parser.sheet_obj_contracts_buildings.cell(row = i, column = 1).value == input[5]):
        build_contracts.append(sber_files_parser.sheet_obj_contracts_buildings.cell(row = i, column = 2).value)
        build_contracts_found += 1

build_contracts_squares = {}
build_contracts_squares_info = []
build_contracts_squares_found = 0

for i in range(0, len(build_contracts)):
    build_contracts_squares[build_contracts[i]] = []

for key in build_contracts_squares:
    for j in range(2, sber_files_parser.sheet_obj_buildings_square.max_row):
        if (build_contracts_squares_found > 0 and key != sber_files_parser.sheet_obj_buildings_square.cell(row = j, column = 1).value):
            build_contracts_squares[key] = build_contracts_squares_info
            build_contracts_squares_info = []
            build_contracts_squares_found = 0
            break
        elif (key == sber_files_parser.sheet_obj_buildings_square.cell(row = j, column = 1).value):
            build_contracts_squares_info.append(sber_files_parser.sheet_obj_buildings_square.cell(row = j, column = 6).value)
            build_contracts_squares_found += 1
offer_s_code = 0
#! ###########################
#? Опциональный ################################
# класс услуги
for i in range(2, sber_files_parser.sheet_obj_codes.max_row):
    if (input[4] == sber_files_parser.sheet_obj_codes.cell(row = i, column = 1).value):
        offer_s_code = sber_files_parser.sheet_obj_codes.cell(row = i, column = 2).value
        break

# прогоняем информацию по основным средствам
builds_fixed_assets = {}
builds_fixed_assets_info = []
builds_fixed_assets_info_one_asset = []
builds_fixed_assets_found = 0
distribution_position_num = 1

for i in range(0, len(build_contracts)):
    builds_fixed_assets[build_contracts[i]] = []

for key in builds_fixed_assets:
    for j in range(2, sber_files_parser.sheet_obj_fixed_assets.max_row):
        if (builds_fixed_assets_found > 0 and key != sber_files_parser.sheet_obj_fixed_assets.cell(row = j, column = 7).value):
            builds_fixed_assets_info_sorted = []
            for k in builds_fixed_assets_info:
                if k not in builds_fixed_assets_info_sorted:
                    builds_fixed_assets_info_sorted.append(k)
            builds_fixed_assets[key] = builds_fixed_assets_info_sorted
            builds_fixed_assets_info = []
            builds_fixed_assets_info_one_asset = []
            builds_fixed_assets_found = 0
            break
        elif (key == sber_files_parser.sheet_obj_fixed_assets.cell(row = j, column = 7).value):
                builds_fixed_assets_info_one_asset.append(sber_files_parser.sheet_obj_fixed_assets.cell(row = j, column = 1).value)
                builds_fixed_assets_info_one_asset.append(sber_files_parser.sheet_obj_fixed_assets.cell(row = j, column = 2).value)
                builds_fixed_assets_info_one_asset.append(sber_files_parser.sheet_obj_fixed_assets.cell(row = j, column = 3).value)
                builds_fixed_assets_info_one_asset.append(sber_files_parser.sheet_obj_fixed_assets.cell(row = j, column = 4).value)
                builds_fixed_assets_info_one_asset.append(sber_files_parser.sheet_obj_fixed_assets.cell(row = j, column = 5).value)
                builds_fixed_assets_info.append(builds_fixed_assets_info_one_asset)
                builds_fixed_assets_info_one_asset = []
                builds_fixed_assets_found += 1


# № позиции распределения + сумма распределения
all_squares_combined = 0
for key in builds_fixed_assets:
    for j in builds_fixed_assets[key]:
        all_squares_combined += j[4]
        j.append(distribution_position_num)
        distribution_position_num += 1

for key in builds_fixed_assets:
    for j in builds_fixed_assets[key]:
        j.append(round(j[4]/all_squares_combined*input[7], 2))

# добавляем output
output = []
output_one_line = []
for key in builds_fixed_assets:
    for j in builds_fixed_assets[key]:
        output_one_line = []
        output_one_line.append(input[0])        # компания
        output_one_line.append(input[1])        # год счёта
        output_one_line.append(input[2])        # номер счёта
        output_one_line.append(input[3])        # позиция счёта
        output_one_line.append(j[5])            # номер позиции распредлеления
        output_one_line.append(input[6])        # дата отражения в учётной системе
        output_one_line[5] = output_one_line[5].strftime("%Y-%m-%d")
        output_one_line.append(input[5])        # ID договора
        output_one_line.append(input[4])        # услуга
        output_one_line.append(offer_s_code)    # ID услуги
        output_one_line.append(key)             # здание
        output_one_line.append(j[1])            # класс основного средства
        output_one_line.append(j[0])            # ID основного средства
        output_one_line.append(j[2])            # признак "используется в основной деятельности"
        output_one_line.append(j[3])            # признак передачи в аренду
        output_one_line.append(j[4])            # площадь
        output_one_line.append(j[6])            # сумма распределения
        output_one_line.append("7048209010")    # счёт главной книги - непонятно, откуда брать, захардкодил
        output.append(output_one_line)