import xgboost as xgb
import pandas as pd
from preprocessing import read_data, data_split
from predict import predict

model = xgb.XGBRegressor()
try:
    model.load_model("UAT/Damen_AI_TeleForecast/xgb_weekly_forecast.json")
    print("model called successfully")
except:
    print("Error! Couldn't Load Model.")
############# this is temporary until database connection established
data_path="/home/jad/TeleForecast/UAT/Damen_AI_TeleForecast/data/ai data new.csv"
holidays_path="/home/jad/TeleForecast/UAT/Damen_AI_TeleForecast/data/egypt_holidays_2023_2024_2025_corrected.xlsx"
df = read_data(data_path, holidays_path)
X_train, y_train, X_test, y_test, pred = data_split('2025-06-10', '2025-06-03',df)
#############
X_new = X_test
string = predict(X_new, model)





