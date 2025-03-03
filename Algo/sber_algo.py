from typing import Optional
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from io import BytesIO
from Algo.sber_files_parser import BinaryXLSXParcer
import asyncio
from Algo.convert_csv_to_xlsx import DATA_CSV_XLSX_Converter


#!################ LOGER #################
from API.App.core.loging_config import LogConfig
from logging.config import dictConfig
import logging
dictConfig(LogConfig().model_dump())
logger = logging.getLogger("washingtonsilver")
#!########################################

class MainAllocationAssembler:
    def __init__(self, binary_dict, reference_dict, rules_dict: dict):
        self.binary_dict = binary_dict
        self.reference_dict = reference_dict
        self.rules_dict = rules_dict
        self.headers = [
            "Компания", "Год счета", "Номер счета", "Позиция счета", 
            "Номер позиции распределения", "Дата отражения в учетной системе", "ID договора",
            "Услуга", "Класс услуги", "Здание", "Класс ОС", "ID основного средства",
            "Признак использования в основной деятельности", "Признак передачи в аренду",
            "Площадь", "Сумма распределения", "Счет главной книги"
        ]
        self.bin_parse = BinaryXLSXParcer()
        self.codes_dict = {}
        self.input = []
        self.final_output = []

    async def async_init(self):
        self.bills = await self.bin_parse.binary_parcer(self.binary_dict["bills_to_pay"])
        self.contracts = await self.bin_parse.binary_parcer(self.reference_dict["contracts"])
        self.building_square = await self.bin_parse.binary_parcer(self.reference_dict["building_squares"])
        self.codes = await self.bin_parse.binary_parcer(self.reference_dict["codes"])
        self.fixed_assets = await self.bin_parse.binary_parcer(self.reference_dict["fixedassets"])
        self.contract_building = await self.bin_parse.binary_parcer(self.reference_dict["contracts_to_building"])

        self.codes_dict = {
            int(row[0]): row[1] for row in self.codes.iter_rows(min_row=2, values_only=True)
        }
        self.json_data = await self.bin_parse.get_json()
        
    async def main(self):
        for row in self.bills.iter_rows(min_row=2, max_row=self.bills.max_row, max_col=self.bills.max_column, values_only=True):
            self.input.append(list(row))

        self.build_contracts_data = list(self.contract_building.iter_rows(min_row=2, max_row=self.contract_building.max_row, max_col=2, values_only=True))
        self.building_square_data = list(self.building_square.iter_rows(min_row=2, max_row=self.building_square.max_row, values_only=True))
        self.fixed_assets_data = list(self.fixed_assets.iter_rows(min_row=2, max_row=self.fixed_assets.max_row, values_only=True))

        for i in range(len(self.input)):
            if i % 100 == 0:
                logger.info(f"Cycle {i} of {len(self.input)}")
            await self.calculation(i)

        #! Post processing 
        y = DATA_CSV_XLSX_Converter()
        csv_binary = y.data_to_csv(headers_list=self.headers, data=self.final_output)
        xlsx_binary = y.convert(csv_binary)
        return csv_binary, xlsx_binary

    async def calculation(self, num: int):
        await asyncio.sleep(0)  # Yield control to the event loop
        build_contracts = [row[1] for row in self.build_contracts_data if row[0] == self.input[num][5]]
        if not build_contracts:
            return

        builds_fixed_assets = {building: [] for building in build_contracts}
        for building in builds_fixed_assets:
            builds_fixed_assets[building] = [
                [row[0], row[1], row[2], row[3], row[4]] 
                for row in self.fixed_assets_data if row[6] == building
            ]
            builds_fixed_assets[building] = [list(x) for x in set(tuple(x) for x in builds_fixed_assets[building])]

        all_squares_combined = sum(j[4] for key in builds_fixed_assets.keys() for j in builds_fixed_assets[key])
        distribution_position_num = 1
        for key in builds_fixed_assets.keys():
            for g in builds_fixed_assets[key]:
                mult = self.input[num][7]
                try:
                    mult = float(str(mult).replace(",", ".").replace(" ", ""))
                except AttributeError:
                    pass
                g.append(distribution_position_num)
                try:
                    g.append(round((g[4] / all_squares_combined) * mult, 2))
                except Exception as e:
                    logger.error(f"Exception while calculating combined price {e}")
                    g.append(None)
                distribution_position_num += 1

        for key in builds_fixed_assets:
            for j in builds_fixed_assets[key]:
                #! logger.info(key)
                key_data = key[4:]
                j.append(self.json_data.get(key_data, ["7048209010"])[0])

        for key in builds_fixed_assets:
            for j in builds_fixed_assets[key]:
                output_one_line = [
                    self.input[num][0],    # компания
                    self.input[num][1],    # год счёта
                    self.input[num][2],    # номер счёта
                    self.input[num][3],    # позиция счёта
                    j[5],                  # номер позиции распределения
                    self.input[num][6],    # дата отражения в учётной системе
                    self.input[num][5],    # ID договора
                    self.input[num][4],    # услуга
                    self.codes_dict[int(self.input[num][4])],  # Класс услуги
                    key,                   # здание
                    j[1],                  # класс основного средства
                    str(j[0]).replace(".", ""),  # ID основного средства
                    j[2],                  # признак "используется в основной деятельности"
                    j[3],                  # признак передачи в аренду
                    j[4],                  # площадь
                    j[6],                  # сумма распределения
                    j[7]                   # счёт главной книги
                ]
                self.final_output.append(output_one_line)

        


if __name__ == "__main__":
    async def main():
        filepaths_bills = ["sber_files/Счета на оплату 3800-2023.XLSX", "sber_files/main.XLSX",
                           "sber_files/Счета на оплату 5400-2023.XLSX", "sber_files/Счета на оплату 5400-2024.XLSX",
                           "sber_files/Счета на оплату 5500-2023.XLSX", "sber_files/Счета на оплату 4200-4000-3800-2024.XLSX"]
        for file_path_bills in filepaths_bills:
            result = []
            filepaths_refs = ["sber_files/Договоры.XLSX", "sber_files/Коды услуг.XLSX", "sber_files/Основные средства.XLSX", "sber_files/Площади зданий.XLSX", "sber_files/Связь договор - здания.XLSX"]
            filepaths_refs_keys = ["contracts", "codes", "fixedassets", "building_squares", "contracts_to_building"]

            bin_dict = {
                "bills_to_pay": open(file_path_bills, "rb").read() if os.path.exists(file_path_bills) else None
            }
            ref_dict = {
                key: open(fp, "rb").read() if os.path.exists(fp) else None
                for key, fp in zip(filepaths_refs_keys, filepaths_refs)
            }
            rules = {}
            print("dicts filled")

            assembler = MainAllocationAssembler(binary_dict=bin_dict, reference_dict=ref_dict, rules_dict=rules)
            await assembler.async_init()
            print("assembler initialized")

            csv_binary, xlsx_binary = await assembler.main()
            print("csv_binary", csv_binary[:100])
            print("xlsx_binary", xlsx_binary[:100])
            if csv_binary != None and xlsx_binary != None:
                result.append(True)
            else:
                result.append(False)
        
    asyncio.run(main())