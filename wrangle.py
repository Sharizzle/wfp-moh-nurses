import pandas as pd
import numpy as np
from typing import Any, Optional
import re

import config

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to snake_case, but preserve '%' as is:
    - Strip leading/trailing spaces
    - Lowercase everything
    - Replace spaces and hyphens with underscores
    - Remove duplicate underscores
    - Remove non-alphanumeric characters (except underscores and %)

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized column names.
    """
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()                      # remove leading/trailing spaces
        .str.lower()                      # lowercase
        .str.replace(r"[ \-]+", "_", regex=True)   # spaces/hyphens → underscore
        .str.replace(r"[^\w_%]", "", regex=True)   # drop non-alphanumeric except _ and %
        .str.replace(r"__+", "_", regex=True)      # collapse multiple underscores
        .str.strip("_")                   # remove leading/trailing underscores
    )
    return df

def denormalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Do the opposite of snake_case normalization:
    - Replace underscores with spaces
    - Capitalize each word
    - Restore hyphens where spaces were previously inserted? (best effort: convert every other space to hyphen)
    - (Can't recover lost non-alphanumeric chars, so skip that)

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with denormalized (prettified) column names.
    """

    # Define abbreviations that should be fully upper-cased if present in any column name
    abbreviations = config.ABBREVIATIONS

    def upcase_abbr_in_col(col: str, abbreviations) -> str:
        for abbr in abbreviations:
            # Use regex for word boundary (case insensitive, preserve %)
            pattern = re.compile(re.escape(abbr), re.IGNORECASE)
            col = pattern.sub(abbr.upper(), col)
        return col

    df = df.copy()
    new_cols = []
    for col in df.columns:
        # Step 1: underscore to space, title case
        col_pretty = col.replace("_", " ").title()
        # Step 2: upper case abbreviations inside column
        col_pretty = upcase_abbr_in_col(col_pretty, abbreviations)
        new_cols.append(col_pretty)
    df.columns = new_cols

    return df

def rename_columns(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """
    Rename columns using a dictionary {old: new}.
    """
    df = df.copy()
    return df.rename(columns=mapping)

def missing_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a summary of missing values by column.
    """
    df = df.copy()
    return (
        df.isna()
        .sum()
        .reset_index(name="missing")
        .rename(columns={"index": "column"})
        .assign(
            total=len(df),
            pct=lambda d: d["missing"] / d["total"] * 100
        )
        .sort_values("pct", ascending=False)
        .reset_index(drop=True)
    )

def rename_values(df: pd.DataFrame, col: str, mapping: dict) -> pd.DataFrame:
    """
    Map messy category values to clean ones.
    Example: {"M": "Male", "male": "Male", "F": "Female"}
    """
    df = df.copy()
    df[col] = df[col].replace(mapping)
    return df

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
    # Reset index to ensure unique, monotonic numbering before repeating
    df_reset = df.reset_index(drop=True)
    df_out = df_reset.loc[df_reset.index.repeat(n_vals)].copy()
    col = np.tile(values, len(df_reset))
    df_out[new_col] = pd.Categorical(col) if as_category else col
    df_out = df_out.reset_index(drop=True)
    return df_out

def fill_missing(df: pd.DataFrame, fill_map: dict) -> pd.DataFrame:
    """
    Fill missing values using a column: value map.
    Example: {"age": 0, "city": "unknown"}
    """
    df = df.copy()
    return df.fillna(fill_map)

def drop_rows_by_value(df: pd.DataFrame, column: str, value) -> pd.DataFrame:
    """
    Remove every row where `column` equals `value`.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    column : str
        Column name to check.
    value : any
        Value to match. All rows where df[column] == value are dropped.

    Returns
    -------
    pd.DataFrame
        DataFrame without the matching rows.
    """
    df = df.copy()
    mask = df[column] != value
    return df.loc[mask].reset_index(drop=True)

def drop_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Drop specified columns from a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    columns : list[str]
        List of column names to drop.

    Returns
    -------
    pd.DataFrame
        DataFrame without the specified columns.
    """
    df = df.copy()
    return df.drop(columns=columns, errors="ignore")

def vlookup_df(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    left_on: str | list[str],
    right_on: str | list[str],
    return_col: str,
    default: Optional[Any] = None
) -> pd.Series | pd.DataFrame:
    """
    Acts like Excel's VLOOKUP for an entire DataFrame column, supporting single or multiple columns as keys.

    Parameters
    ----------
    left_df : pd.DataFrame
        The DataFrame containing the keys to look up.
    right_df : pd.DataFrame
        The lookup table DataFrame containing the lookup and return columns.
    left_on : str or list of str
        Column(s) in `left_df` whose values will be looked up.
    right_on : str or list of str
        Column(s) in `right_df` where matching keys will be searched.
    return_col : str
        Column in `right_df` whose values will be returned.
    default : Any, optional
        Value to fill when a match is not found (default: None).

    Returns
    -------
    pd.Series
        A Series aligned with `left_df` containing the looked-up values.
    """
    if isinstance(left_on, str):
        left_on = [left_on]
    if isinstance(right_on, str):
        right_on = [right_on]
    # Compose a DataFrame that has all the needed columns for merge
    right_merge = right_df[right_on + [return_col]].copy()
    merged = pd.merge(
        left_df[left_on].reset_index(drop=True),
        right_merge,
        how="left",
        left_on=left_on,
        right_on=right_on
    )
    if default is not None:
        # Only call .fillna if default is not None, to avoid ValueError with pandas
        result = merged[return_col].fillna(default)
    else:
        result = merged[return_col]
    return result

