import numpy as np
import pandas as pd

def expand_df_by_values(df: pd.DataFrame, new_col: str, values, as_category: bool = True) -> pd.DataFrame:
    """
    Expand each row of `df` into multiple rows by attaching values from a fixed list.

    Parameters
    ----------
    df : pd.DataFrame
        Source dataframe.
    new_col : str
        Name of the new column to create with expanded values.
    values : list/array-like
        List of values to assign to each row.
    as_category : bool, default True
        Store `new_col` as a pandas Categorical to save memory.

    Returns
    -------
    pd.DataFrame
        Expanded dataframe with one row per (original row × value).
    """
    df = df.copy()
    n_vals = len(values)
    df_out = df.loc[df.index.repeat(n_vals)].copy()
    col = np.tile(values, len(df))
    df_out[new_col] = pd.Categorical(col) if as_category else col
    return df_out