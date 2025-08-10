import xgboost as xgb

def train_model(X_train,y_train):
    model =xgb.XGBRegressor(
        objective='reg:absoluteerror',  # regression objective
        n_estimators=3000,              # number of trees
        learning_rate=0.1,             # step size shrinkage
        max_depth=8,                   # maximum tree depth
        subsample=0.8,                 # % of data used per tree
        colsample_bytree=0.8,          # % of features used per tree
        reg_alpha=0.7,                 # L1 regularization term
        reg_lambda=0.1,                  # L2 regularization term
        random_state=42                # for reproducibility
    )

    # Fit the model
    model.fit(X_train, y_train)
    model.save_model("UAT/Damen_AI_TeleForecast/xgb_weekly_forecast.json")
    print("Saved new model successfully!")
    return model