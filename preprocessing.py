import pandas as pd
import numpy as np
from datetime import timedelta

def get_holiday_features_for_week(week_start, holidays_df):
    """
    Calculates holiday features for a given week.
    
    Args:
        week_start (datetime): The starting date of the week (e.g., Monday).
        holidays_df (DataFrame): The dataframe of all holidays.
        
    Returns:
        dict: A dictionary containing holiday features for that week.
    """
    week_end = week_start + timedelta(days=6)
    
    holidays_in_week = holidays_df[
        (holidays_df['Date'] >= week_start) & (holidays_df['Date'] <= week_end)
    ]

    num_holiday_days = len(holidays_in_week)

    holiday_name = holidays_in_week['Holiday Name'].unique().tolist()
    holiday_types = holidays_in_week['Holiday Type'].unique().tolist()
    long_weekend = bool(holidays_in_week['Long Weekend'].any())
    
    return {
        'num_holiday_days': num_holiday_days,
        'holiday_names': holiday_name,
        'holiday_types': holiday_types,
        'long_weekend': long_weekend
    }

def read_data(file_path1, file_path2):
    df = pd.read_csv(file_path1)
    df['WEEK_START'] = pd.to_datetime(df['WEEK_START'])
    
    try:
        holidays_df = pd.read_excel(file_path2)
    except FileNotFoundError:
        print(f"Error: {file_path2} not found")
        holidays_df = pd.DataFrame()
    holidays_df['Date'] = pd.to_datetime(holidays_df['Date'])
    
    holiday_features = df['WEEK_START'].apply(
        lambda date: get_holiday_features_for_week(date, holidays_df)
    )

    holiday_features_df = pd.json_normalize(holiday_features)

    df = pd.concat([df, holiday_features_df], axis=1)

    df = df.drop(columns=['holiday_types', 'holiday_names'])

    df = df.apply(lambda x: x.astype(int) if x.name not in ['date','WEEK_START','long_weekend'] and x.notnull().all() else x)
    df.set_index('WEEK_START', inplace=True)
    return df

def preprocess(df, file_path):
    df.set_index('WEEK_START', inplace=True)
    
    try:
        holidays_df = pd.read_excel(file_path)
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        holidays_df = pd.DataFrame()
    holidays_df['Date'] = pd.to_datetime(holidays_df['Date'])
    
    holiday_features = df['WEEK_START'].apply(
        lambda date: get_holiday_features_for_week(date, holidays_df)
    )

    holiday_features_df = pd.json_normalize(holiday_features)

    df = pd.concat([df, holiday_features_df], axis=1)

    df = df.drop(columns=['holiday_types', 'holiday_names'])

    df = df.apply(lambda x: x.astype(int) if x.name not in ['date','WEEK_START','long_weekend'] and x.notnull().all() else x)
    df.set_index('WEEK_START', inplace=True)

def data_split(splitDate1,splitDate2,df):
    split_date=splitDate1
    df = df[df.index < split_date]
    split_date=splitDate2
    train_df = df[df.index < split_date]
    test_df = df[df.index >= split_date]
    pred="NEXT_WEEK_TOTAL_AMOUNT"

    X_train = train_df.drop(pred, axis=1)   # features
    y_train = train_df[pred]    # target

    X_test = test_df.drop(pred, axis=1)
    y_test = test_df[pred] 
    
    return X_train,y_train,X_test,y_test,pred

