import pandas as pd
import numpy as np
from prophet import Prophet
import glob
import joblib
from io import BytesIO
import os
import sys
import asyncio
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


from API.App.core.loging_config import LogConfig
from logging.config import dictConfig
import logging
dictConfig(LogConfig().model_dump())
logger = logging.getLogger("washingtonsilver")


class MashineLearning:
    def __init__(self, binary_data):
        self.procesed_buildings = 0
        #!####################################### PREPARATION #######################################################
        bytes_io = BytesIO(binary_data)
        data = pd.read_excel(bytes_io)
        self.data_cleaned = data[data['Сумма распределения'] != 0].copy()
        # Retain necessary columns
        self.data_cleaned['Дата отражения в учетной системе'] = pd.to_datetime(self.data_cleaned['Дата отражения в учетной системе'])
        self.data_cleaned['Дата отражения в учетной системе'] = self.data_cleaned['Дата отражения в учетной системе'].fillna(method='ffill')
        self.data_cleaned['year_month'] = self.data_cleaned['Дата отражения в учетной системе'].dt.to_period('M').dt.to_timestamp()
        #!##############################################################################################
        
    async def main(self):
        loop = asyncio.get_event_loop()
        max_date = self.data_cleaned['Дата отражения в учетной системе'].max()

        self.buildings_to_predict = self.data_cleaned['Здание'].unique()
        next_month_start = (max_date + pd.offsets.MonthBegin(1)).replace(day=1)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, 'J_final_model_with_regressor_sps0.1_cps0.1_foureir1.pkl')
        
        print(script_dir, model_path)
        
        models = await loop.run_in_executor(None, joblib.load, model_path)

        future_months = pd.DataFrame({'ds': pd.date_range(start=next_month_start, periods=12, freq='MS')})

        self.predictions = {}
        
        tasks = [
            self.predict_for_building(building_id, models[building_id], future_months.copy())
            for building_id in self.buildings_to_predict if building_id in models
        ]
        
        logger.warning("Starting prediction tasks...")
        results = await asyncio.gather(*tasks)
        logger.warning("Prediction tasks completed.")
        
        for result in results:
            if result:
                building_id, forecast = result
                self.predictions[building_id] = forecast

        self.all_predictions = pd.concat(self.predictions.values(), axis=0).reset_index(drop=True)
        
    async def predict_for_building(self, building_id, model, future):
        loop = asyncio.get_event_loop()
        average_area = self.data_cleaned[self.data_cleaned['Здание'] == building_id]['Площадь'].mean()
        future['Площадь'] = average_area
        forecast = await loop.run_in_executor(None, model.predict, future)
        forecast['Здание'] = building_id
        
        retained_columns = self.data_cleaned[self.data_cleaned['Здание'] == building_id][['Класс ОС', 'ID основного средства', 'Счет главной книги']].iloc[0]
        forecast['Класс ОС'] = retained_columns['Класс ОС']
        forecast['ID основного средства'] = retained_columns['ID основного средства']
        forecast['Счет главной книги'] = retained_columns['Счет главной книги']
        
        self.procesed_buildings += 1
        if self.procesed_buildings % 100 == 0:
            logger.info(f"CURRENTLY PREDICTED BUILDINGS ARE: {self.procesed_buildings} out of {len(self.buildings_to_predict)}")
        return building_id, forecast[['ds', 'yhat', 'Здание', 'Класс ОС', 'ID основного средства', 'Счет главной книги']]

    def get_all_data(self):
        data_output = []
        for key in self.predictions.keys():
            for row in self.predictions[key].to_numpy():
                row = row.tolist()
                row[0] = row[0].to_pydatetime() if isinstance(row[0], pd.Timestamp) else row[0]
                row[1] = abs(row[1])
                data_output.append(row)
        return data_output

if __name__ == "__main__":
    async def main_async():
        with open('data5400-2024.XLSX', 'rb') as f:
            binary_content = f.read()
        
        x = MashineLearning(binary_content)
        await x.main()
        for key in x.predictions.keys():
            for row in x.predictions[key].to_numpy():
                row = row.tolist()
                row[0] = row[0].to_pydatetime() if isinstance(row[0], pd.Timestamp) else row[0]
                row[1] = abs(row[1])
                # print(row)
    
    asyncio.run(main_async())