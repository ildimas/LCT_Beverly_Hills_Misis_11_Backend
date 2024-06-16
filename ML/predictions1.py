import pandas as pd
import numpy as np
from prophet import Prophet
import glob
import joblib

percent = 0
file_path = 'data5400-2024.XLSX'
data = pd.read_excel(file_path)


data_cleaned = data[data['Сумма распределения'] != 0].copy()
data_cleaned = data_cleaned.drop(columns=['Класс ОС', 'ID основного средства', 'Счет главной книги'])
data_cleaned['Дата отражения в учетной системе'] = pd.to_datetime(data_cleaned['Дата отражения в учетной системе'])
data_cleaned['Дата отражения в учетной системе'] = data_cleaned['Дата отражения в учетной системе'].fillna(method='ffill')
data_cleaned['year_month'] = data_cleaned['Дата отражения в учетной системе'].dt.to_period('M').dt.to_timestamp()

max_date = data_cleaned['Дата отражения в учетной системе'].max()

buildings_to_predict = data_cleaned['Здание'].unique()

next_month_start = (max_date + pd.offsets.MonthBegin(1)).replace(day=1)

models = joblib.load('J_final_model_with_regressor_sps0.1_cps0.1_foureir1.pkl')

future_months = pd.DataFrame({'ds': pd.date_range(start=next_month_start, periods=5, freq='MS')})


predictions = {}

for building_id in buildings_to_predict:
    if building_id in models:
        model = models[building_id]
        future = future_months.copy()
        average_area = data_cleaned[data_cleaned['Здание'] == building_id]['Площадь'].mean()
        future['Площадь'] = average_area
        forecast = model.predict(future)
        forecast['Здание'] = building_id
        predictions[building_id] = forecast[['ds', 'yhat', 'Здание']]
        percent += 1
        print(f"{'{:.2f}'.format((percent / len(buildings_to_predict)) * 100)}")

all_predictions = pd.concat(predictions.values(), axis=0).reset_index(drop=True)
print(all_predictions)