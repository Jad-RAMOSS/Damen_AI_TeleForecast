import xgboost as xgb
import pandas as pd
from preprocessing import read_data, data_split, preprocess
from predict import predict
from newData import get_data
from html import escape
import requests


model = xgb.XGBRegressor()
try:
    model.load_model("xgb_weekly_forecast.json")
    print("model called successfully")
except:
    print("Error! Couldn't Load Model.")
############ this is temporary until database connection established
data_path="/home/jad/TeleForecast/UAT/Damen_AI_TeleForecast/data/ai data new.csv"
holidays_path="/home/jad/TeleForecast/UAT/Damen_AI_TeleForecast/data/egypt_holidays_2023_2024_2025_corrected.xlsx"
df = read_data(data_path, holidays_path)
X_train, y_train, X_test, y_test, pred = data_split('2025-06-10', '2025-06-03',df)
X_new=X_test
############
# X_new = get_data()
# X_new = preprocess(X_new)
string = predict(X_new, model)
print(string)
message_html = "<br><br>".join(escape(s) for s in string.split("\n\n"))

url = "http://10.29.55.23:3002/notify/"
payload = {
    "name": "TeleForeCast",
    "message": message_html
}

resp = requests.post(url, json=payload, timeout=10)  # json= sets Content-Type: application/json
resp.raise_for_status()
print("Status:", resp.status_code)
print("Body:", resp.text)









# #!/usr/bin/env python3
# import os
# import socket
# import urllib.parse
# import requests
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry

# import xgboost as xgb
# import pandas as pd

# # Project modules
# from preprocessing import read_data, data_split, preprocess  # noqa: F401 (preprocess may be unused here)
# from predict import predict
# # from newData import get_data  # Uncomment if you switch to live data


# # ---------- Config & helpers ----------
# def load_env():
#     try:
#         from dotenv import load_dotenv  # type: ignore
#         load_dotenv()
#     except Exception:
#         # .env loading is optional
#         pass


# def get_env_str(key: str, default: str) -> str:
#     val = os.getenv(key)
#     return val if val not in (None, "") else default


# def get_env_int(key: str, default: int) -> int:
#     try:
#         return int(os.getenv(key, str(default)))
#     except ValueError:
#         return default


# def is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
#     try:
#         with socket.create_connection((host, port), timeout=timeout):
#             return True
#     except OSError:
#         return False


# def make_http_session() -> requests.Session:
#     s = requests.Session()
#     # Ignore system proxy env by default; we also set NO_PROXY for 10.0.0.0/8
#     s.trust_env = False
#     retries = Retry(
#         total=3,
#         connect=3,
#         read=3,
#         backoff_factor=0.5,
#         status_forcelist=[502, 503, 504],
#         raise_on_status=False,
#     )
#     s.mount("http://", HTTPAdapter(max_retries=retries))
#     s.mount("https://", HTTPAdapter(max_retries=retries))
#     return s


# # ---------- Main ----------
# def main():
#     load_env()

#     # Paths / dates (override via .env if needed)
#     DATA_PATH = get_env_str(
#         "DATA_PATH",
#         "/home/jad/TeleForecast/UAT/Damen_AI_TeleForecast/data/ai data new.csv",
#     )
#     HOLIDAYS_PATH = get_env_str(
#         "HOLIDAYS_PATH",
#         "/home/jad/TeleForecast/UAT/Damen_AI_TeleForecast/data/egypt_holidays_2023_2024_2025_corrected.xlsx",
#     )
#     # Data window (example defaults taken from your previous run)
#     TEST_CUTOFF_DATE = get_env_str("TEST_CUTOFF_DATE", "2025-06-10")  # inclusive
#     TRAIN_END_DATE = get_env_str("TRAIN_END_DATE", "2025-05-15")

#     # Date offset for display (your requirement: +7 days)
#     DATE_OFFSET_DAYS = get_env_int("DATE_OFFSET_DAYS", 7)

#     # Notify settings
#     NOTIFY_URL = get_env_str("NOTIFY_URL", "http://10.29.55.23:3002/notify/")
#     CONNECT_TIMEOUT = float(get_env_int("CONNECT_TIMEOUT", 3))
#     READ_TIMEOUT = float(get_env_int("READ_TIMEOUT", 10))

#     # Ensure 10.x bypasses any corporate proxy automatically
#     os.environ.setdefault("NO_PROXY", "127.0.0.1,localhost,.local,10.0.0.0/8")
#     os.environ.setdefault("no_proxy", os.environ["NO_PROXY"])

#     # -------- Load model --------
#     model = xgb.XGBRegressor()
#     try:
#         model.load_model(get_env_str("MODEL_PATH", "xgb_weekly_forecast.json"))
#         print("model called successfully")
#     except Exception as e:
#         print("Error! Couldn't Load Model.", e)

#     # -------- Get data (temporary local path flow) --------
#     # For DB flow later:
#     # X_new = get_data()
#     # X_new = preprocess(X_new)

#     df = read_data(DATA_PATH, HOLIDAYS_PATH)
#     X_train, y_train, X_test, y_test, pred = data_split(TEST_CUTOFF_DATE, TRAIN_END_DATE, df)
#     X_new = X_test.copy()

#     # Shift the index by +N days so predict() prints the shifted date in its output string.
#     # (Your predict() uses group.index[i] for 'WEEK_START' → this controls the printed date.)
#     try:
#         X_new.index = pd.to_datetime(X_new.index) + pd.Timedelta(days=DATE_OFFSET_DAYS)
#     except Exception:
#         # If index isn't datetime-like, try to coerce it
#         X_new.index = pd.to_datetime(X_new.index, errors="coerce") + pd.Timedelta(days=DATE_OFFSET_DAYS)

#     # -------- Predict & format string --------
#     out_string = predict(X_new, model)
#     print(out_string)

#     from html import escape
#     message_html = "<br><br>".join(escape(s) for s in out_string.split("\n\n"))
#     # Optionally write any DF your predict may also produce; you already log Excel elsewhere.

#     # -------- Robust notify --------
#     payload = {
#         "name": "TeleForeCast",
#         "message": message_html,
#     }

#     parsed = urllib.parse.urlparse(NOTIFY_URL)
#     host = parsed.hostname
#     port = parsed.port or (80 if parsed.scheme == "http" else 443)

#     if not host:
#         print(f"Notify skipped: invalid NOTIFY_URL='{NOTIFY_URL}'")
#         return

#     if not is_port_open(host, port, timeout=CONNECT_TIMEOUT):
#         print(f"Notify skipped: cannot connect to {host}:{port}")
#         return

#     session = make_http_session()
#     try:
#         resp = session.post(
#             NOTIFY_URL,
#             json=payload,  # sets Content-Type: application/json
#             timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
#         )
#         resp.raise_for_status()
#         print("Status:", resp.status_code)
#         body_preview = resp.text if len(resp.text) <= 500 else (resp.text[:497] + "...")
#         print("Body:", body_preview)
#     except requests.exceptions.RequestException as e:
#         print("Notify FAILED:", e)


# if __name__ == "__main__":
#     main()