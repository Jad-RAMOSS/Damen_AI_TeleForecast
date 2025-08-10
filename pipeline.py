from preprocessing import read_data, data_split
from model import train_model

data_path="/home/jad/TeleForecast/UAT/Damen_AI_TeleForecast/data/ai data new.csv"
holidays_path="/home/jad/TeleForecast/UAT/Damen_AI_TeleForecast/data/egypt_holidays_2023_2024_2025_corrected.xlsx"
df = read_data(data_path, holidays_path)
X_train, y_train, X_test, y_test, pred = data_split('2025-06-10', '2025-05-06',df)
model = train_model(X_train, y_train)