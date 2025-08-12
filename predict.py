import pandas as pd
from pathlib import Path

def predict(X_new, model, date_shift_days=7):
    """
    Run predictions for each MAIN_BILLER_ID, write an Excel with results,
    and return a human-readable block with WEEK_START shifted by +date_shift_days.
    """
    from pathlib import Path
    import pandas as pd

    features = list(X_new.columns)
    product_name = {13: "Vodafone", 14: "Orange", 15: "Etisalat", 16: "We"}

    # ---- Run predictions & build result rows ----
    records = []
    for product_id in sorted(X_new["MAIN_BILLER_ID"].unique()):
        group = X_new[X_new["MAIN_BILLER_ID"] == product_id].sort_index()
        X_test = group[features]
        y_pred = model.predict(X_test)

        for idx, pred in zip(group.index, y_pred):
            records.append(
                {
                    "MAIN_BILLER_ID": product_id,
                    "Product": product_name.get(product_id, str(product_id)),
                    "WEEK_START": pd.to_datetime(idx),  # ensure datetime
                    "Predicted": float(pred),
                }
            )

    df_out = pd.DataFrame(records)

    # ---- Write Excel ----
    out_path = Path("data") / "predictions_vs_actual.xlsx"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_excel(out_path, index=False)
    print(
        f"Excel file written: {out_path.name} "
        f"(columns: MAIN_BILLER_ID, Product, WEEK_START, Predicted)"
    )

    # ---- Latest row per product (by WEEK_START) ----
    latest = (
        df_out.sort_values("WEEK_START")
        .groupby("Product", as_index=False, sort=False)
        .tail(1)
    )

    # ---- Build the output string (with blank lines) ----
    date_fmt = "%Y-%m-%d"
    order = ["Vodafone", "Orange", "Etisalat", "We"]
    lines = []
    day_offset = pd.to_timedelta(date_shift_days, unit="D")

    for name in order:
        row = latest[latest["Product"] == name]
        if row.empty:
            continue

        # Use the latest row for that product
        wk_start = pd.to_datetime(row["WEEK_START"].iloc[0]) + day_offset
        date_str = wk_start.strftime(date_fmt)

        # Robust numeric formatting
        val = int(round(float(row["Predicted"].iloc[0])))

        lines.append(f"{name} ({date_str}): {val}")

    return "\n\n".join(lines)

