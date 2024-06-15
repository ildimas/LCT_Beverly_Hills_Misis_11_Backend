import sber_algo
import csv
from openpyxl import Workbook

# пишем csv
filename_csv = "sample.csv"
headers = ["Компания", "Год счета", "Номер счета", "Позиция счета", 
           "Номер позиции распределения", "Дата отражения в учетной системе", "ID договора",
           "Услуга", "ID услуги", "Здание", "Класс ОС", "ID основного средства",
           "Признак использования в основной деятельности", "Признак передачи в аренду",
           "Площадь", "Сумма распределения", "Счет главной книги"]

with open(filename_csv, mode='w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    
    writer.writerow(headers)
    
    for row in sber_algo.output:
        writer.writerow(row)

print("CSV файл был успешно записан!")

# пишем xlsx
filename_xlsx = "sample.XLSX"
wb = Workbook()
ws = wb.active

for i in range(0, len(headers)):
    ws.cell(row = 1, column = i + 1).value = headers[i]

for i in range(0, len(sber_algo.output)):
    for j in range(0, len(sber_algo.output[i])):
        ws.cell(row = i + 2, column = j + 1).value = sber_algo.output[i][j]

wb.save(filename_xlsx)

print("XLSX файл был успешно записан!")