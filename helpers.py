import pandas as pd

from typing import Sequence, Optional
import pandas as pd

import columns

def calc_stats(
    group: pd.DataFrame,
    value_col: str,
    base_quantiles: Sequence[float] = [0.25, 0.5, 0.75],
    additional_quantiles: Optional[Sequence[float]] = None
) -> pd.Series:
    """
    Calculate summary statistics including quantiles, min, max, IQR, range, and count
    for a specified value column in a pandas DataFrame group.

    Parameters
    ----------
    group : pd.DataFrame
        The DataFrame group over which statistics are calculated.
    value_col : Hashable
        The column name (or index) containing the numeric values.
    base_quantiles : Sequence[float], optional
        List of base quantiles to compute (default: [0.25, 0.5, 0.75]).
    additional_quantiles : Sequence[float], optional
        Additional quantile levels to compute, added to the output with keys
        like "quantile_0.1" (default: None).

    Returns
    -------
    pd.Series
        A Series with computed statistics: q1, median, q3, min, max, iqr, range, data_points,
        plus any specified additional quantiles.
    """
    values = group[value_col]

    # Calculate base quantiles
    quantile_vals = values.quantile(base_quantiles)
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
    # If additional_quantiles are provided, calculate and add to stats
    if additional_quantiles is not None:
        addl_quantile_vals = values.quantile(additional_quantiles)
        # add each additional quantile to stats with a key naming convention
        for i, q_val in enumerate(additional_quantiles):
            stats[f"quantile_{q_val}"] = addl_quantile_vals.iloc[i]
    return pd.Series(stats)

def calc_stats_scenarios(
    group: pd.DataFrame,
    value_col: str,
    quantiles: Sequence[float] = [0.25, 0.5, 0.75]
) -> pd.DataFrame:
    """
    Compute quantiles for a value column in a DataFrame group,
    and return a melted DataFrame with quantile values and a 'percentile_value' column.

    Parameters
    ----------
    group : pd.DataFrame
        The DataFrame group to compute quantiles on.
    value_col : str
        Column of numeric values.
    quantiles : Sequence[float], optional
        quantiles to compute, default is [0.25, 0.5, 0.75]

    Returns
    -------
    pd.DataFrame
        Melted DataFrame with 'percentile' and percentile_value columns only (no multi-index columns).
    """
    values = group[value_col]
    quantile_vals = values.quantile(quantiles)
    percentiles = [str(p) for p in quantiles]
    quantile_dict = {percentile: quantile_vals.iloc[i] for i, percentile in enumerate(percentiles)}
    quantile_df = pd.DataFrame([quantile_dict])

    # When melting a dataframe with no id_vars, the index becomes "variable" by default.
    melted = quantile_df.melt(var_name="percentile", value_name=columns.PERCENTILE_VALUE)
    melted = melted.reset_index(drop=True)  # Ensure no "level_3" or other index columns
    return melted


def denormalize_text(s: str) -> str:
    """
    Convert a snake_case string back to a space-separated, capitalized format.
    E.g. 'ratio_value' -> 'Ratio Value', 'total__beds' -> 'Total Beds'
    """
    if not isinstance(s, str):
        return s
    # Replace multiple underscores with single space
    clean_str = s.replace("_", " ")
    clean_str = " ".join(clean_str.split())
    return clean_str.title()