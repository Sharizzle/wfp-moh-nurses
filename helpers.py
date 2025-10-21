import pandas as pd

def calc_stats(group, value_col, quantiles=[0.25, 0.5, 0.75]):
    values = group[value_col]
    quantile_vals = values.quantile(quantiles)
    q1 = quantile_vals.iloc[0]
    median = quantile_vals.iloc[1]
    q3 = quantile_vals.iloc[2]
    min_val = values.min()
    max_val = values.max()
    iqr = q3 - q1
    range_val = max_val - min_val
    data_points = values.count()  # Ensure data_points is an integer value
    stats = {
        "q1": q1,
        "median": median,
        "q3": q3,
        "min": min_val,
        "max": max_val,
        "iqr": iqr,
        "range": range_val,
        "data_points": data_points
    }
    return pd.Series(stats)