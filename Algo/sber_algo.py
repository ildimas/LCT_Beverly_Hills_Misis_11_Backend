from typing import Optional
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from io import BytesIO
from Algo.sber_files_parser import BinaryXLSXParcer
import asyncio
from convert_csv_to_xlsx import DATA_CSV_XLSX_Converter


# bills_binary : BytesIO, contracts_buildings_binary: Optional[BytesIO],
#                  buildings_square_binary : Optional[BytesIO], codes_binary : Optional[BytesIO],
#                  fixed_assets_binary : Optional[BytesIO], contracts_binary : Optional[BytesIO]
class MainAllocationAssembler:
    def __init__(self, binary_dict, reference_dict, rules_dict):
        self.bin_parse = BinaryXLSXParcer()
        self.headers = ["Компания", "Год счета", "Номер счета", "Позиция счета", 
           "Номер позиции распределения", "Дата отражения в учетной системе", "ID договора",
           "Услуга", "ID услуги", "Здание", "Класс ОС", "ID основного средства",
           "Признак использования в основной деятельности", "Признак передачи в аренду",
           "Площадь", "Сумма распределения", "Счет главной книги"]
        self.bills = self.bin_parse.binary_parcer(binary_dict["bills_to_pay"])
        print("1 parced")
        self.contracts = self.bin_parse.binary_parcer(reference_dict["contracts"])
        print("2 parced")
        self.building_square = self.bin_parse.binary_parcer(reference_dict["codes"])
        print("3 parced")
        self.codes = self.bin_parse.binary_parcer(reference_dict["fixedassets"])
        print("4 parced")
        self.fixed_assets = self.bin_parse.binary_parcer(reference_dict["building_squares"])
        print("5 parced")
        self.contract_building = self.bin_parse.binary_parcer(reference_dict["contracts_to_building"])
        print("6 parced")
        #!passer         #! result
        self.input = []; self.final_output = []; input_row = []
        
    def main(self):
        counter = 0
        # принимаем - Компания, год, номер счёта, позиция счёта, ID услуги, ID договора, дата отражения учёта, стоимость без ДНС
        for row in self.bills.iter_rows(min_row=2, max_row=self.bills.max_row, max_col=self.bills.max_column, values_only=True):
            self.input.append(list(row))
            print(counter)
            counter += 1
        print("data loaded")
        self.build_contracts_data = list(self.contract_building.iter_rows(min_row=2, max_row=self.contract_building.max_row, max_col=2, values_only=True))
        self.building_square_data = list(self.building_square.iter_rows(min_row=2, max_row=self.building_square.max_row, values_only=True))
        self.fixed_assets_data = list(self.fixed_assets.iter_rows(min_row=2, max_row=self.fixed_assets.max_row, values_only=True))
        print("for loop started !")
        for i in range(0, len(self.input)):
            print(f"calcul {i} out of {len(self.input)}")
            self.calculation(i)
        
        
    def calculation(self, num):
        #! Договор - здание
        build_contracts = [row[1] for row in self.build_contracts_data if row[0] == self.input[num][5]]
        #! Площади
        build_contracts_squares = {contract: [] for contract in build_contracts}
        for contract in build_contracts:
            build_contracts_squares[contract] = [row[5] for row in self.building_square_data if row[0] == contract]
        #! Основные средства
        for i in range(0, len(build_contracts)):
            build_contracts_squares[build_contracts[i]] = []

            # Create a dictionary to hold builds fixed assets
        builds_fixed_assets = {contract: [] for contract in build_contracts}
        for contract in builds_fixed_assets:
            builds_fixed_assets[contract] = [
                [row[0], row[1], row[2], row[3], row[4]] for row in self.fixed_assets_data if row[6] == contract
            ]
            # Remove duplicates and maintain order
            builds_fixed_assets[contract] = [list(x) for x in set(tuple(x) for x in builds_fixed_assets[contract])]

        # Calculate combined squares and assign distribution positions
        all_squares_combined = sum(j[4] for key in builds_fixed_assets for j in builds_fixed_assets[key])
        distribution_position_num = 1
        for key in builds_fixed_assets:
            for j in builds_fixed_assets[key]:
                j.append(distribution_position_num)
                j.append(round(j[4] / all_squares_combined * self.input[num][7], 2))
                distribution_position_num += 1

        # Add general ledger account from JSON
        json_data = self.bin_parse.get_json()
        for key in builds_fixed_assets:
            for j in builds_fixed_assets[key]:
                j.append("7048209010")
                key_data = key.replace("ЗДН ", "")
                if key_data in json_data:
                    j[7] = json_data[key_data][0]

        # Prepare final output
        output = []
        for key in builds_fixed_assets:
            for j in builds_fixed_assets[key]:
                output_one_line = [
                    self.input[num][0],    # компания
                    self.input[num][1],    # год счёта
                    self.input[num][2],    # номер счёта
                    self.input[num][3],    # позиция счёта
                    j[5],                  # номер позиции распределения
                    self.input[num][6].strftime("%Y-%m-%d"),  # дата отражения в учётной системе
                    self.input[num][5],    # ID договора
                    self.input[num][4],    # услуга
                    key,                   # здание
                    j[1],                  # класс основного средства
                    j[0],                  # ID основного средства
                    j[2],                  # признак "используется в основной деятельности"
                    j[3],                  # признак передачи в аренду
                    j[4],                  # площадь
                    j[6],                  # сумма распределения
                    j[7]                   # счёт главной книги
                ]
                output.append(output_one_line)
                print(output)
        self.final_output += output
if __name__ == "__main__":
    filepaths_bills = ["sber_files/Счета на оплату 3800-2023.XLSX"]
    filepaths_refs = ["sber_files/Договоры.XLSX", "sber_files/Коды услуг.XLSX", "sber_files/Основные средства.XLSX", "sber_files/Площади зданий.XLSX", "sber_files/Связь договор - здания.XLSX"]
    filepaths_refs_keys = ["contracts", "codes", "fixedassets", "building_squares", "contracts_to_building"]
    bin_dict = {
    "bills_to_pay": open(filepaths_bills[0], "rb").read() if os.path.exists(filepaths_bills[0]) else None
    }
    ref_dict = {
    key: open(fp, "rb").read() if os.path.exists(fp) else None
    for key, fp in zip(filepaths_refs_keys, filepaths_refs)
    }
    rules = {}
    # print(bin_dict)
    # print(ref_dict)
    print("dicts filled")
    x = MainAllocationAssembler(binary_dict=bin_dict, reference_dict=ref_dict, rules_dict=rules)
    print("x initialized")
    x.main()
    y = DATA_CSV_XLSX_Converter()
    csv_binary = y.data_to_csv(headers_list=x.headers, data=x.final_output)
    # xlsx_binary = y.convert(csv_binary)
    print(csv_binary)
    # print(xlsx_binary)